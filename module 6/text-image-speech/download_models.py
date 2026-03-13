# download_models.py
import os
import time
from huggingface_hub import snapshot_download, login
import torch
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Your HF token (from .env)
HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY")
if not HF_TOKEN:
    raise ValueError("HUGGINGFACE_API_KEY not found in .env file")

# Set environment variable for longer timeout
os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "120"
os.environ["HF_HUB_ETAG_TIMEOUT"] = "120"

print("Downloading models with extended timeout...")
print(f"Timeout set to: {os.environ.get('HF_HUB_DOWNLOAD_TIMEOUT')} seconds")

# Login to Hugging Face
login(token=HF_TOKEN, add_to_git_credential=True)

try:
    # Download SDXL with resume capability (without unsupported parameters)
    print("\n📥 Downloading Stable Diffusion XL (this will take 10-15 minutes)...")
    model_path = snapshot_download(
        repo_id="stabilityai/stable-diffusion-xl-base-1.0",
        local_dir="./models/sdxl",  # Save to local folder
        resume_download=True,
        local_files_only=False,
        ignore_patterns=["*.safetensors", "*.bin"],  # Optional: skip model files if you just want config
        max_workers=2  # Slower but more stable
    )
    
    print(f"✅ Models downloaded successfully to: {model_path}")
    print("\n🎉 You can now run your main pipeline!")

except Exception as e:
    print(f"\n❌ Error downloading: {e}")
    print("\n💡 Alternative: Let's try a smaller model instead...")
    
    # Try smaller model as fallback
    try:
        print("\n📥 Downloading TinySD (ultra-lightweight, ~500MB)...")
        small_model_path = snapshot_download(
            repo_id="stabilityai/TinySD",
            local_dir="./models/tiny",
            resume_download=True,
            max_workers=2,
            ignore_patterns=["*.safetensors", "*.bin"]
        )
        print(f"✅ Config-only download to: {small_model_path}")
        print("\n💡 For full quantized model (~1GB):")
        print("   pip install optimum[onnxruntime]")
        print("   optimum.exporters.onnx --model stabilityai/TinySD --task text-to-image onnx_tiny")
        
    except Exception as e2:
        print(f"❌ Even smaller model failed: {e2}")
        print("\n💡 Try Solution 4 - Use Google Colab instead")