import os
import sys

# Try to load dotenv, but don't fail if it's not available
try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment variables")
    print("   Install it with: pip install python-dotenv")
except Exception as e:
    print(f"⚠️  Error loading .env file: {e}")

# Hugging Face configuration - MAKE SURE YOU'VE REPLACED WITH YOUR NEW KEY!
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')

if not HUGGINGFACE_API_KEY:
    print("❌ ERROR: HUGGINGFACE_API_KEY not found in environment variables")
    print("\nPlease set your Hugging Face API key in one of these ways:")
    print("1. Create a .env file with: HUGGINGFACE_API_KEY=your_key_here")
    print("2. Set it as an environment variable:")
    print("   - Windows (Command Prompt): set HUGGINGFACE_API_KEY=your_key_here")
    print("   - Windows (PowerShell): $env:HUGGINGFACE_API_KEY='your_key_here'")
    print("   - Linux/Mac: export HUGGINGFACE_API_KEY=your_key_here")
    sys.exit(1)

# Model configuration - USE THE NEW ROUTER ENDPOINT
MODEL_ID = "black-forest-labs/FLUX.1-dev"
# CRITICAL FIX: Use the new router endpoint
API_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL_ID}"

# Generation parameters
DEFAULT_PARAMS = {
    "max_new_tokens": 100,
    "temperature": 1.0,
    "top_p": 0.9,
    "do_sample": True,
}

print(f"🔧 Config loaded - API URL: {API_URL}")