import base64
from io import BytesIO
from PIL import Image
import requests
import json
from config import HUGGINGFACE_API_KEY, API_URL, DEFAULT_PARAMS

class ImageGenerator:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        # Use only the new router endpoint
        self.api_url = API_URL
        print(f"🔧 ImageGenerator initialized with API_URL: {self.api_url}")
    
    def generate_image(self, prompt, params=None):
        """
        Generate an image from a text prompt
        """
        if params is None:
            params = DEFAULT_PARAMS.copy()
        
        # Prepare the payload
        payload = {
            "inputs": prompt,
            "parameters": params
        }
        
        print(f"🎨 Generating image for: '{prompt}'")
        print(f"⚙️ Parameters: {params}")
        print(f"🔄 Using endpoint: {self.api_url}")
        
        try:
            # Make API request
            response = requests.post(
                self.api_url, 
                headers=self.headers, 
                json=payload,
                timeout=120  # Increased timeout for image generation
            )
            
            print(f"📡 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Success!")
                return self._process_response(response)
            elif response.status_code == 503:
                # Model is loading
                print("⏳ Model is loading. This might take 20-30 seconds...")
                # You could add retry logic here
                raise Exception("Model is loading, please try again in a few seconds")
            else:
                error_msg = f"API Error {response.status_code}: {response.text}"
                print(f"⚠️  {error_msg}")
                raise Exception(error_msg)
                
        except requests.exceptions.Timeout:
            raise Exception("Request timed out. The model might be loading or busy.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def _process_response(self, response):
        """
        Process the API response and convert to PIL Image
        """
        content_type = response.headers.get('content-type', '')
        print(f"📦 Response Content-Type: {content_type}")
        
        if 'image' in content_type:
            # Direct image response
            return Image.open(BytesIO(response.content))
        else:
            # Try to parse as JSON
            try:
                data = response.json()
                print(f"📦 Response data type: {type(data)}")
                
                # Handle different response formats
                if isinstance(data, list) and len(data) > 0:
                    if isinstance(data[0], dict) and 'generated_image' in data[0]:
                        img_data = base64.b64decode(data[0]['generated_image'])
                        return Image.open(BytesIO(img_data))
                elif isinstance(data, dict):
                    if 'image' in data:
                        img_data = base64.b64decode(data['image'])
                        return Image.open(BytesIO(img_data))
                
                # If we can't parse, save for debugging
                with open("error_response.json", "w") as f:
                    json.dump(data, f, indent=2)
                print("⚠️ Unexpected response format. Saved to error_response.json")
                
            except Exception as e:
                print(f"⚠️ Error parsing response: {e}")
            
            raise Exception(f"Unexpected response format. Content-Type: {content_type}")
    
    def save_image(self, image, filename):
        """
        Save generated image to file
        """
        image.save(filename)
        print(f"💾 Image saved as {filename}")

def create_prompt_with_style(base_prompt, style=None):
    """
    Enhance prompt with style specifications
    """
    if style:
        style_prompts = {
            "realistic": "photorealistic, highly detailed, 4k, professional photography",
            "anime": "anime style, vibrant colors, detailed illustration",
            "oil_painting": "oil painting style, artistic, textured brush strokes",
            "sketch": "pencil sketch, black and white, artistic drawing",
            "watercolor": "watercolor painting, soft colors, artistic",
        }
        
        if style in style_prompts:
            return f"{base_prompt}, {style_prompts[style]}"
    
    return base_prompt