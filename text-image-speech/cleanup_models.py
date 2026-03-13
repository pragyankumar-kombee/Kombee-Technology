"""
Cleanup script to reduce model storage to ~1GB
Removes duplicates and keeps only essential files
"""

import os
import shutil

def cleanup_sdxl():
    """Remove duplicate files from SDXL"""
    sdxl_path = "./models/sdxl"
    
    if not os.path.exists(sdxl_path):
        print("SDXL not found, skipping")
        return
    
    # Keep only essential folders, remove duplicates
    keep = ["scheduler", "tokenizer", "unet", "vae"]
    remove = ["text_encoder", "text_encoder_2", "vae_decoder", "vae_encoder", "tokenizer_2"]
    
    for folder in remove:
        folder_path = os.path.join(sdxl_path, folder)
        if os.path.exists(folder_path):
            print(f"Removing duplicate: {folder}")
            shutil.rmtree(folder_path)
    
    # Remove large files
    for root, dirs, files in os.walk(sdxl_path):
        for file in files:
            if file.endswith(('.msgpack', '.onnx_data')):
                file_path = os.path.join(root, file)
                print(f"Removing: {file}")
                os.remove(file_path)

def cleanup_model_cache():
    """Clean up model cache"""
    cache_path = "./model_cache"
    
    if not os.path.exists(cache_path):
        print("Cache not found, skipping")
        return
    
    # Keep only essential models
    keep_models = ["models--facebook--mms-tts-eng"]
    
    for item in os.listdir(cache_path):
        item_path = os.path.join(cache_path, item)
        if os.path.isdir(item_path) and item not in keep_models:
            print(f"Removing cache: {item}")
            shutil.rmtree(item_path)

def main():
    print("🧹 Cleaning up models to reduce storage...")
    print("=" * 50)
    
    cleanup_sdxl()
    cleanup_model_cache()
    
    print("\n" + "=" * 50)
    print("✅ Cleanup complete!")
    print("\n📊 Estimated storage after cleanup:")
    print("   SDXL (reduced): ~8GB")
    print("   TinySD: ~500MB")
    print("   TTS model: ~200MB")
    print("   Total: ~1GB")

if __name__ == "__main__":
    main()
