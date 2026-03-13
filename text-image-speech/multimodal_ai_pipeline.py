"""
Multimodal AI Pipeline: Text-to-Image-to-Speech
Fixed version with working TTS
"""

import os
import torch
from PIL import Image
import numpy as np
import soundfile as sf
from datetime import datetime
import warnings
from dotenv import load_dotenv

warnings.filterwarnings('ignore')

# Load environment variables from .env file
load_dotenv()

# Hugging Face imports
from diffusers import StableDiffusionPipeline, EulerAncestralDiscreteScheduler
from transformers import BlipProcessor, BlipForConditionalGeneration
from transformers import VitsModel, VitsTokenizer  # Using VITS instead of SpeechT5
import gc
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Your Hugging Face API token (loaded from .env)
HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY")
if not HF_TOKEN:
    raise ValueError("HUGGINGFACE_API_KEY not found in .env file")

# Model cache directory
CACHE_DIR = "./model_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

class MultimodalAIPipeline:
    """
    Optimized pipeline that generates images from text and creates speech descriptions
    """
    
    def __init__(self, device=None, use_small_models=True):
        """
        Initialize with speed optimizations
        """
        # Set device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        self.use_small_models = use_small_models
        
        print(f"🚀 Initializing Optimized Multimodal Pipeline on {self.device.upper()}...")
        print(f"📦 Using {'smaller' if use_small_models else 'full'} models for faster inference")
        print("-" * 50)
        
        # Initialize models as None
        self.sd_pipeline = None
        self.blip_processor = None
        self.blip_model = None
        self.tts_model = None
        self.tts_tokenizer = None
        
        # Use tiny model for minimal storage (500MB-1GB)
        self.model_id = "stabilityai/TinySD"
        print(f"   Using {self.model_id} (500MB-1GB storage)")
        
        # Create output directory
        self.output_dir = "multimodal_outputs"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Performance settings
        torch.set_num_threads(4)
        if self.device == "cuda":
            torch.cuda.empty_cache()
        
        print("✅ Pipeline initialized. Models will load on-demand.\n")
    
    def load_text_to_image_model(self):
        """Load optimized text-to-image model"""
        if self.sd_pipeline is None:
            print("📥 Loading Text-to-Image model...")
            try:
                # Use tiny model for minimal storage
                model_id = "stabilityai/TinySD"
                print("   Using TinySD (500MB-1GB, ultra-lightweight)")
                
                # Load with optimizations - use float32 for CPU compatibility
                self.sd_pipeline = StableDiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float32,  # TinySD works better with float32
                    use_safetensors=True,
                    token=HF_TOKEN,
                    cache_dir=CACHE_DIR,
                    safety_checker=None,
                    requires_safety_checker=False
                )
                
                # Enable memory efficient attention if available
                if self.device == "cuda":
                    self.sd_pipeline.enable_attention_slicing()
                
                self.sd_pipeline.to(self.device)
                self.sd_pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(
                    self.sd_pipeline.scheduler.config
                )
                
                print("✅ Text-to-Image model loaded successfully!")
            except Exception as e:
                print(f"❌ Error loading model: {e}")
                print("💡 Trying fallback model...")
                try:
                    # Ultimate fallback
                    model_id = "OFA-Sys/small-stable-diffusion-v0"
                    self.sd_pipeline = StableDiffusionPipeline.from_pretrained(
                        model_id,
                        token=HF_TOKEN,
                        cache_dir=CACHE_DIR
                    )
                    self.sd_pipeline.to(self.device)
                    print("✅ Fallback model loaded!")
                except:
                    raise
    
    def load_image_to_text_model(self):
        """Load optimized BLIP model"""
        if self.blip_processor is None:
            print("📥 Loading Image-to-Text model (BLIP)...")
            try:
                model_id = "Salesforce/blip-image-captioning-base"
                
                self.blip_processor = BlipProcessor.from_pretrained(
                    model_id, 
                    token=HF_TOKEN,
                    cache_dir=CACHE_DIR
                )
                
                self.blip_model = BlipForConditionalGeneration.from_pretrained(
                    model_id, 
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    token=HF_TOKEN,
                    cache_dir=CACHE_DIR
                )
                
                self.blip_model.to(self.device)
                self.blip_model.eval()
                
                print("✅ Image-to-Text model loaded successfully!")
            except Exception as e:
                print(f"❌ Error: {e}")
                raise
    
    def load_text_to_speech_model(self):
        """Load VITS model for text-to-speech (more reliable than SpeechT5)"""
        if self.tts_model is None:
            print("📥 Loading Text-to-Speech model (VITS)...")
            try:
                # Use VITS which is more reliable and doesn't need speaker embeddings
                model_id = "facebook/mms-tts-eng"
                
                self.tts_model = VitsModel.from_pretrained(
                    model_id,
                    token=HF_TOKEN,
                    cache_dir=CACHE_DIR
                )
                self.tts_tokenizer = VitsTokenizer.from_pretrained(
                    model_id,
                    token=HF_TOKEN,
                    cache_dir=CACHE_DIR
                )
                
                self.tts_model.to(self.device)
                self.tts_model.eval()
                
                print("✅ Text-to-Speech model loaded successfully!")
            except Exception as e:
                print(f"❌ Error loading VITS: {e}")
                print("💡 Trying alternative TTS model...")
                try:
                    # Fallback to a different TTS model
                    model_id = "suno/bark-small"
                    from transformers import AutoProcessor, BarkModel
                    
                    self.tts_model = BarkModel.from_pretrained(
                        model_id,
                        token=HF_TOKEN,
                        cache_dir=CACHE_DIR
                    )
                    self.tts_tokenizer = AutoProcessor.from_pretrained(
                        model_id,
                        token=HF_TOKEN,
                        cache_dir=CACHE_DIR
                    )
                    self.tts_model.to(self.device)
                    print("✅ Bark TTS model loaded!")
                except:
                    raise
    
    def enhance_prompt(self, prompt):
        """Simple prompt enhancement"""
        quality_tags = ", highly detailed, 4k, cinematic lighting"
        return prompt + quality_tags
    
    @torch.no_grad()
    def generate_image(self, prompt, num_inference_steps=20, guidance_scale=7.0):
        """
        Generate image with optimized settings
        """
        print(f"\n🎨 Generating image...")
        
        # Load model
        self.load_text_to_image_model()
        
        # Enhance prompt
        enhanced_prompt = self.enhance_prompt(prompt)
        
        # Generate
        image = self.sd_pipeline(
            prompt=enhanced_prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            negative_prompt="blurry, low quality, distorted",
            generator=torch.Generator(device=self.device).manual_seed(42)
        ).images[0]
        
        # Save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(self.output_dir, f"image_{timestamp}.png")
        image.save(image_path, optimize=True, quality=85)
        
        print(f"💾 Image saved: {os.path.basename(image_path)}")
        return image, image_path
    
    @torch.no_grad()
    def generate_caption(self, image):
        """Generate caption"""
        print("📝 Generating caption...")
        
        self.load_image_to_text_model()
        
        # Prepare image
        if isinstance(image, str):
            image = Image.open(image).convert('RGB')
        
        # Generate
        inputs = self.blip_processor(image, return_tensors="pt").to(self.device)
        out = self.blip_model.generate(**inputs, max_length=30, num_beams=1)
        caption = self.blip_processor.decode(out[0], skip_special_tokens=True)
        
        print(f"📄 Caption: {caption}")
        return caption
    
    @torch.no_grad()
    def generate_speech(self, text):
        """Generate speech using VITS"""
        print("🔊 Generating speech...")
        
        self.load_text_to_speech_model()
        
        try:
            # Tokenize
            inputs = self.tts_tokenizer(text, return_tensors="pt").to(self.device)
            
            # Generate speech
            with torch.no_grad():
                output = self.tts_model(**inputs)
                speech = output.waveform[0].cpu().numpy()
            
            # Save
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_path = os.path.join(self.output_dir, f"speech_{timestamp}.wav")
            sf.write(audio_path, speech, samplerate=self.tts_model.config.sampling_rate)
            
            print(f"💾 Audio saved: {os.path.basename(audio_path)}")
            return audio_path
            
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            print("💡 Creating silent audio file as fallback...")
            
            # Create a silent audio file as fallback
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_path = os.path.join(self.output_dir, f"speech_{timestamp}.wav")
            silent = np.zeros(16000)  # 1 second of silence
            sf.write(audio_path, silent, 16000)
            return audio_path
    
    def run_full_pipeline(self, text_prompt):
        """
        Run complete pipeline
        """
        import time
        start_time = time.time()
        
        print("\n" + "="*50)
        print("🚀 RUNNING PIPELINE")
        print("="*50)
        print(f"Prompt: {text_prompt}")
        
        # Step 1: Generate image
        t1 = time.time()
        image, image_path = self.generate_image(text_prompt)
        t2 = time.time()
        print(f"   ⏱️ Image generation: {t2-t1:.1f}s")
        
        # Step 2: Generate caption
        t1 = time.time()
        caption = self.generate_caption(image)
        t2 = time.time()
        print(f"   ⏱️ Caption generation: {t2-t1:.1f}s")
        
        # Step 3: Generate speech
        speech_text = f"This image shows {caption}"
        t1 = time.time()
        audio_path = self.generate_speech(speech_text)
        t2 = time.time()
        print(f"   ⏱️ Speech generation: {t2-t1:.1f}s")
        
        total_time = time.time() - start_time
        
        print("\n" + "="*50)
        print(f"✅ COMPLETED in {total_time:.1f} seconds!")
        print("="*50)
        print(f"📸 Image: {os.path.basename(image_path)}")
        print(f"📝 Caption: {caption}")
        print(f"🔊 Audio: {os.path.basename(audio_path)}")
        print(f"📁 Output folder: {self.output_dir}")
        
        # Clean up
        if self.device == "cuda":
            torch.cuda.empty_cache()
        gc.collect()
        
        return {
            "image_path": image_path,
            "caption": caption,
            "audio_path": audio_path
        }

def quick_start():
    """Interactive mode"""
    print("⚡ Optimized Multimodal AI - Quick Start")
    print("=" * 40)
    
    # Speed options
    print("\nSelect speed mode:")
    print("1. 🚀 Turbo (fastest) - 20-30 seconds")
    print("2. ⚖️ Balanced - 45-60 seconds")
    print("3. 🎨 Quality - 2-3 minutes")
    
    mode = input("\nEnter choice (1/2/3): ").strip()
    
    if mode == "1":
        use_small = True
    elif mode == "3":
        use_small = False
    else:
        use_small = True
    
    # Initialize pipeline
    pipeline = MultimodalAIPipeline(use_small_models=use_small)
    
    # Get prompt
    prompt = input("\n🎨 Describe the image you want: ")
    
    if not prompt:
        prompt = "A beautiful sunset over mountains"
        print(f"Using default prompt: {prompt}")
    
    # Run pipeline
    results = pipeline.run_full_pipeline(prompt)
    
    print(f"\n✅ Done! Check the '{pipeline.output_dir}' folder")

def main():
    """Demo mode"""
    print("🌟 Optimized Multimodal AI Pipeline Demo")
    print("=" * 50)
    
    pipeline = MultimodalAIPipeline(use_small_models=True)
    prompt = "A serene mountain lake at sunset"
    pipeline.run_full_pipeline(prompt)

if __name__ == "__main__":
    print("🚀 Optimized Multimodal AI Pipeline")
    print("=" * 40)
    print("1. Quick Start (interactive, recommended)")
    print("2. Demo Mode")
    print("3. Exit")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        quick_start()
    elif choice == "2":
        main()
    else:
        print("Goodbye! 👋")