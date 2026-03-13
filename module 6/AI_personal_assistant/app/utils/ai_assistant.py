import requests
import json
from flask import current_app
import time
import os


class AIAssistant:
    def __init__(self):
        self.api_token = None
        self.model = None
        self.session = requests.Session()

    def init_app(self, app):
        """Initialize with Flask app config"""
        self.api_token = app.config.get('GROQ_API_KEY')
        self.model = app.config.get('GROQ_MODEL', 'llama-3.3-70b-versatile')
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        })

    def generate_response(self, prompt, history=None, max_length=500, search_context=None):
        """
        Generate response using Groq API with optional search context
        """
        if not self.api_token:
            return "⚠️ API token not configured. Please set GROQ_API_KEY in .env file."
        
        if self.api_token == "your-groq-api-key-here":
            return "⚠️ Please replace the placeholder token in .env with your actual Groq API token."
        
        # Build conversation messages with search context if available
        messages = self._build_messages(prompt, history, search_context)
        
        # Groq API endpoint
        api_url = "https://api.groq.com/openai/v1/chat/completions"
        
        # Prepare payload for Groq chat completions
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_length,
            "temperature": 0.7,
            "top_p": 0.95,
            "stream": False
        }
        
        try:
            response = self.session.post(api_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                # Extract message from chat completion format
                if 'choices' in result and len(result['choices']) > 0:
                    message = result['choices'][0].get('message', {})
                    return message.get('content', '').strip()
                else:
                    return str(result)
            else:
                error_msg = f"Error: API returned {response.status_code}"
                try:
                    error_detail = response.json()
                    if 'error' in error_detail:
                        error_msg += f" - {error_detail['error'].get('message', error_detail['error'])}"
                except:
                    pass
                return error_msg
            
        except requests.exceptions.Timeout:
            return "⌛ Request timed out. Please try again."
        except requests.exceptions.ConnectionError:
            return "🔌 Connection error. Please check your internet connection."
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def _build_messages(self, prompt, history=None, search_context=None):
        """Build conversation messages in chat format with optional search context"""
        from datetime import datetime
        current_date = datetime.now().strftime("%B %d, %Y")
        
        system_content = f"""You are a helpful AI assistant with access to real-time information. 
Today's date is {current_date}. 
Provide clear, concise, and accurate responses based on the information available to you.
When you have web search results, use them to provide up-to-date and accurate information.
Always cite your sources when using web search results."""
        
        messages = [
            {"role": "system", "content": system_content}
        ]
        
        # Add conversation history
        if history:
            for msg in history[-5:]:  # Last 5 messages for context
                messages.append({"role": "user", "content": msg['user']})
                messages.append({"role": "assistant", "content": msg['assistant']})
        
        # Add search context if available
        if search_context:
            enhanced_prompt = f"{prompt}\n\n[Web Search Results]:\n{search_context}\n\nPlease answer based on the above search results and provide accurate, current information."
            messages.append({"role": "user", "content": enhanced_prompt})
        else:
            messages.append({"role": "user", "content": prompt})
        
        return messages
