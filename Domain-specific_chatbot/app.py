from flask import Flask, request, jsonify, render_template, session
import logging
import json
from config import Config
from model_utils import model_instance
from conversation import conversation_manager
import os
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app [citation:1][citation:6]
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# Load model in background thread
def load_model_background():
    """Load model in background to not block app startup"""
    with app.app_context():
        logger.info("Loading model in background...")
        success = model_instance.load_model()
        if success:
            logger.info("✅ Model loaded successfully")
        else:
            logger.error("❌ Failed to load model")

@app.route('/model-info', methods=['GET'])
def model_info():
    """Check if model is loaded"""
    return jsonify({
        'loaded': model_instance.model is not None,
        'model_id': model_instance.config.MODEL_ID if model_instance.model else None,
        'domain': model_instance.config.DOMAIN
    })

@app.route('/')
def index():
    """Render the main chat interface"""
    # Initialize session
    if 'session_id' not in session:
        session['session_id'] = conversation_manager.create_session()
        logger.info(f"New session created: {session['session_id']}")
    
    return render_template('index.html', domain=Config.DOMAIN)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages [citation:1][citation:4]"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get or create session
        session_id = session.get('session_id')
        if not session_id:
            session_id = conversation_manager.create_session()
            session['session_id'] = session_id
        
        # Get conversation history
        history = conversation_manager.get_history(session_id)
        
        # Check if model is loaded
        if model_instance.model is None:
            return jsonify({
                'response': "Model is still loading. Please wait a moment and try again.",
                'loading': True
            }), 202
        
        # Generate response [citation:4]
        logger.info(f"Processing message: {user_message[:50]}...")
        response = model_instance.generate_response(user_message, history)
        
        # Save to history
        conversation_manager.add_message(session_id, user_message, response)
        
        return jsonify({
            'response': response,
            'session_id': session_id,
            'message_count': len(history) + 1
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['GET'])
def get_history():
    """Get conversation history for current session"""
    session_id = session.get('session_id')
    if not session_id:
        return jsonify({'history': []})
    
    history = conversation_manager.get_history(session_id)
    return jsonify({
        'history': history,
        'session_id': session_id
    })

@app.route('/clear', methods=['POST'])
def clear_history():
    """Clear conversation history"""
    session_id = session.get('session_id')
    if session_id:
        conversation_manager.clear_session(session_id)
        return jsonify({'status': 'cleared'})
    return jsonify({'error': 'No session found'}), 404

@app.route('/sections', methods=['GET'])
def get_sections():
    """Get all sections from localStorage"""
    try:
        with open('sections.json', 'r') as f:
            sections = json.load(f)
        return jsonify({'sections': sections})
    except FileNotFoundError:
        return jsonify({'sections': []})
    except Exception as e:
        logger.error(f"Error loading sections: {e}")
        return jsonify({'sections': []}), 500

@app.route('/sections', methods=['POST'])
def save_sections():
    """Save sections to localStorage"""
    try:
        data = request.get_json()
        sections = data.get('sections', [])
        with open('sections.json', 'w') as f:
            json.dump(sections, f, indent=2)
        return jsonify({'status': 'saved'})
    except Exception as e:
        logger.error(f"Error saving sections: {e}")
        return jsonify({'error': 'Failed to save sections'}), 500

if __name__ == '__main__':
    # Start model loading in background
    threading.Thread(target=load_model_background).start()
    
    # Run Flask app
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=False  # Set to False in production
    )