import uuid
from datetime import datetime
from typing import List, Dict

class ConversationManager:
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
    
    def create_session(self) -> str:
        """Create a new conversation session"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'id': session_id,
            'created': datetime.now(),
            'history': [],
            'metadata': {
                'message_count': 0,
                'tokens_used': 0
            }
        }
        return session_id
    
    def add_message(self, session_id: str, user_msg: str, assistant_msg: str):
        """Add a message pair to session history"""
        if session_id not in self.sessions:
            session_id = self.create_session()
        
        self.sessions[session_id]['history'].append({
            'user': user_msg,
            'assistant': assistant_msg,
            'timestamp': datetime.now()
        })
        self.sessions[session_id]['metadata']['message_count'] += 1
    
    def get_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session"""
        return self.sessions.get(session_id, {}).get('history', [])
    
    def clear_session(self, session_id: str):
        """Clear a session's history"""
        if session_id in self.sessions:
            self.sessions[session_id]['history'] = []
            self.sessions[session_id]['metadata']['message_count'] = 0

# Singleton instance
conversation_manager = ConversationManager()