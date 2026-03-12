import requests
from config import HUGGINGFACE_API_KEY

# List of models to test
models_to_test = [
    "black-forest-labs/FLUX.1-dev",
    "stabilityai/stable-diffusion-xl-base-1.0",
    "runwayml/stable-diffusion-v1-5",
    "prompthero/openjourney-v4",
    "Phr00t/Qwen-Image-Edit-Rapid-AIO"  # Your original model
]

headers = {
    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
}

for model_id in models_to_test:
    print(f"\n🔍 Testing model: {model_id}")
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"✅ Model accessible")
            model_info = response.json()
            print(f"   Pipeline: {model_info.get('pipeline_tag', 'Unknown')}")
        elif response.status_code == 401:
            print(f"❌ Authentication error - check your API key")
        elif response.status_code == 404:
            print(f"❌ Model not found")
        else:
            print(f"⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Error: {e}")