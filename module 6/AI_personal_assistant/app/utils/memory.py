from datetime import datetime
from collections import defaultdict


class ConversationMemory:
    """Manages conversation history for users"""
    
    def __init__(self):
        # Structure: {user_id: {conversation_id: [messages]}}
        self.conversations = defaultdict(lambda: defaultdict(list))
    
    def add_message(self, user_id, conversation_id, user_message, assistant_response):
        """Add a message exchange to conversation history"""
        message = {
            'user': user_message,
            'assistant': assistant_response,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.conversations[user_id][conversation_id].append(message)
    
    def get_conversation(self, user_id, conversation_id):
        """Get a specific conversation history"""
        return self.conversations[user_id].get(conversation_id, [])
    
    def get_all_conversations(self, user_id):
        """Get all conversations for a user"""
        return dict(self.conversations[user_id])
    
    def clear_conversations(self, user_id):
        """Clear all conversations for a user"""
        if user_id in self.conversations:
            del self.conversations[user_id]
    
    def clear_conversation(self, user_id, conversation_id):
        """Clear a specific conversation"""
        if user_id in self.conversations and conversation_id in self.conversations[user_id]:
            del self.conversations[user_id][conversation_id]
