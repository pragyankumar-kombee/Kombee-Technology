import os
import argparse
from datetime import datetime
from utils import ImageGenerator, create_prompt_with_style
from config import API_URL  # Import to verify

def main():
    # Print debug info
    print(f"🔧 Using API URL: {API_URL}")
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Generate images from text prompts using Hugging Face API')
    parser.add_argument('prompt', type=str)
    parser.add_argument('--style', type=str, choices=['realistic', 'anime', 'oil_painting', 'sketch', 'watercolor'])
    parser.add_argument('--output', type=str,)
    parser.add_argument('--temperature', type=float, default=0.7)
    parser.add_argument('--max-tokens', type=int, default=100)
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    output_dir = "generated_images"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Enhance prompt with style if specified
    enhanced_prompt = create_prompt_with_style(args.prompt, args.style)
    print(f"Generating image for: '{enhanced_prompt}'")
    
    # Set generation parameters
    params = {
        "max_new_tokens": args.max_tokens,
        "temperature": args.temperature,
        "top_p": 0.9,
        "do_sample": True,
    }
    
    try:
        # Initialize generator
        generator = ImageGenerator()
        
        # Generate image
        print("Sending request to Hugging Face API...")
        image = generator.generate_image(enhanced_prompt, params)
        
        # Generate output filename
        if args.output:
            filename = args.output
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_image_{timestamp}.png"
        
        # Save image
        filepath = os.path.join(output_dir, filename)
        generator.save_image(image, filepath)
        
        print(f"✅ Image generated successfully!")
        print(f"📁 Location: {filepath}")
        
        # Display image info
        print(f"📏 Image size: {image.size}")
        print(f"🎨 Image mode: {image.mode}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()