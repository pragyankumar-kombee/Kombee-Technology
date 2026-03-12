import os
import logging
from typing import Optional
from groq import Groq  # type: ignore
from config import Config  # type: ignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DomainModel:
    def __init__(self):
        self.config = Config
        self.client = None
        self.model: Optional[str] = None # Keep property for app.py compatibility check
        
    def load_model(self):
        """Initialize the Groq client"""
        try:
            logger.info(f"Initializing Groq client for model: {self.config.MODEL_ID}")
            # Ensure the GROQ_API_KEY is available (loaded via dotenv in config.py)
            self.client = Groq()
            # Set model variable so that app.py knows it's loaded
            self.model = "groq-api"
            logger.info("Groq client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing Groq client: {e}")
            self.model = None
            return False
    
    def generate_response(self, prompt, conversation_history=None):
        """Generate response using the Groq API"""
        try:
            if not self.client:
                raise ValueError("Groq client not initialized. Call load_model() first.")
            
            system_prompt = self._get_domain_prompt()
            messages = [{"role": "system", "content": system_prompt}]
            
            if conversation_history:
                for turn in conversation_history[-self.config.MAX_HISTORY:]:
                    messages.append({"role": "user", "content": turn['user']})
                    messages.append({"role": "assistant", "content": turn['assistant']})
                    
            messages.append({"role": "user", "content": prompt})
            
            # Generate response from Groq
            completion = self.client.chat.completions.create(
                model=self.config.MODEL_ID,
                messages=messages,
                temperature=self.config.TEMPERATURE,
                max_tokens=self.config.MAX_NEW_TOKENS,
                top_p=self.config.TOP_P,
                stream=False,
            )
            
            return completion.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating Groq response: {e}")
            return f"I encountered an error connecting to Groq: {str(e)}"
    
    def _get_domain_prompt(self):
        """Get domain-specific system prompt"""
        prompts = {
            'finance': "You are a highly accurate, professional financial assistant. The current year is 2026. Prioritize outputting the most accurate financial data, economic conditions, and investment contexts applicable to 2026. Provide factual information about finance, banking, and economics in a structured format. Always clarify that you're an AI and not a licensed financial advisor.",
            'law': "You are an expert legal assistant providing clear, precise general legal information. The current year is 2026. Ensure any legal context considers updates or standards relevant to 2026. You do not provide formal legal advice. Always suggest consulting with a qualified attorney for specific cases.",
            'medicine': "You are a highly knowledgeable medical information assistant. The current year is 2026. Provide evidence-based general health information prioritizing medical guidelines up to 2026. Highlight that you're an AI, not a doctor, and strongly recommend consulting healthcare professionals.",
            'general': "You are an intelligent, helpful, and honest AI assistant. The current year is 2026. Provide fast, structurally well-formatted, and highly accurate answers, keeping your knowledge context framed as operating in 2026."
        }
        return prompts.get(self.config.DOMAIN, prompts['general'])

# Singleton instance
model_instance = DomainModel()