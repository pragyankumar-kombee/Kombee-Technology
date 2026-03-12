import os
from dotenv import load_dotenv  # type: ignore

# Load environment variables
load_dotenv()

class Config:
    # Flask configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-in-production')
    PORT = int(os.getenv('FLASK_PORT', 5000))
    HOST = os.getenv('FLASK_HOST', '127.0.0.1')
    
    # Domain configuration
    DOMAIN = os.getenv('DOMAIN', 'general').lower()
    
    # Model configuration based on domain (Using Groq supported endpoints)
    MODEL_CONFIGS = {
        'finance': {
            'model_id': os.getenv('GROQ_MODEL_FINANCE', 'llama-3.3-70b-versatile'),
            'description': 'Finance domain chatbot',
            'context_length': 8192
        },
        'law': {
            'model_id': os.getenv('GROQ_MODEL_LAW', 'llama-3.3-70b-versatile'),
            'description': 'Legal domain chatbot',
            'context_length': 8192
        },
        'medicine': {
            'model_id': os.getenv('GROQ_MODEL_MEDICINE', 'llama-3.3-70b-versatile'),
            'description': 'Medical domain chatbot',
            'context_length': 8192
        },
        'general': {
            'model_id': os.getenv('GROQ_MODEL_GENERAL', 'llama-3.1-8b-instant'),
            'description': 'General purpose chatbot',
            'context_length': 8192
        }
    }
    
    # Get model for selected domain
    MODEL_CONFIG = MODEL_CONFIGS.get(DOMAIN, MODEL_CONFIGS['general'])
    MODEL_ID = MODEL_CONFIG['model_id']
    
    # Hardware configuration (Not actually used by Groq API but kept for compatibility)
    USE_GPU = os.getenv('USE_GPU', 'false').lower() == 'true'
    DEVICE = 'cloud' # Groq is cloud-based
    
    # Generation parameters
    MAX_NEW_TOKENS = 512 # Reduced for faster response time
    TEMPERATURE = 0.7
    TOP_P = 0.9
    REPETITION_PENALTY = 1.1
    
    # Cache directory
    CACHE_DIR = os.getenv('MODEL_CACHE_DIR', './model_cache')
    
    # Conversation settings
    MAX_HISTORY = 10  # Keep last 10 messages for context