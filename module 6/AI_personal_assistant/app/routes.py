from flask import Blueprint, render_template, request, jsonify, session, current_app
from app.utils.memory import ConversationMemory
from app.utils.web_search import WebSearchTool
import uuid
import json

bp = Blueprint('main', __name__)
memory = ConversationMemory()
search_tool = WebSearchTool()


# Import AIAssistant inside route functions to avoid circular imports
@bp.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@bp.route('/chat', methods=['GET', 'POST'])
def chat():
    """Chat interface"""
    # Initialize session if new user
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        session['conversation_id'] = str(uuid.uuid4())

    if request.method == 'POST':
        from app.utils.ai_assistant import AIAssistant
        assistant = AIAssistant()
        assistant.init_app(current_app)

        user_message = request.json.get('message', '')

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Get conversation history
        history = memory.get_conversation(
            session['user_id'],
            session['conversation_id']
        )

        # Check if we need to search the web
        search_context = None
        if search_tool.should_search(user_message):
            print(f"🔍 Searching web for: {user_message}")
            search_results = search_tool.search(user_message, max_results=3)
            if search_results:
                search_context = search_tool.format_search_results(search_results)
                print(f"✅ Found {len(search_results)} results")

        # Get AI response with search context
        response = assistant.generate_response(
            user_message,
            history,
            max_length=500,
            search_context=search_context
        )

        # Save to memory
        memory.add_message(
            session['user_id'],
            session['conversation_id'],
            user_message,
            response
        )

        return jsonify({
            'response': response,
            'conversation_id': session['conversation_id'],
            'used_search': search_context is not None
        })

    return render_template('chat.html')


@bp.route('/history')
def history():
    """View conversation history"""
    if 'user_id' not in session:
        return render_template('history.html', conversations=[])

    conversations = memory.get_all_conversations(session['user_id'])
    return render_template('history.html', conversations=conversations)


@bp.route('/settings')
def settings():
    """Settings page"""
    return render_template('settings.html')


@bp.route('/clear-history', methods=['POST'])
def clear_history():
    """Clear conversation history"""
    if 'user_id' in session:
        memory.clear_conversations(session['user_id'])
    return jsonify({'status': 'success'})


@bp.route('/export-all')
def export_all():
    """Export all conversations"""
    if 'user_id' not in session:
        return jsonify({'error': 'No data to export'}), 404
    
    conversations = memory.get_all_conversations(session['user_id'])
    return jsonify(conversations)
