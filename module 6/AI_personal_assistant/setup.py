import os
import sys
import subprocess

def setup():
    print("🔧 Setting up AI Personal Assistant...")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists('venv'):
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'])
    
    # Determine pip path
    if sys.platform == 'win32':
        pip_path = os.path.join('venv', 'Scripts', 'pip')
        python_path = os.path.join('venv', 'Scripts', 'python')
    else:
        pip_path = os.path.join('venv', 'bin', 'pip')
        python_path = os.path.join('venv', 'bin', 'python')
    
    # Install requirements
    print("📥 Installing requirements...")
    subprocess.run([pip_path, 'install', '-r', 'requirements.txt'])
    
    # Check for .env file
    if not os.path.exists('.env'):
        print("📝 Creating .env file...")
        with open('.env', 'w') as f:
            f.write("""# Flask settings
SECRET_KEY=your-secret-key-here-change-in-production
FLASK_DEBUG=True
PORT=5000

# Hugging Face API (get your token from https://huggingface.co/settings/tokens)
HUGGINGFACE_API_TOKEN=your-huggingface-api-token-here
""")
        print("⚠️  Please edit the .env file and add your Hugging Face API token!")
    
    print("✅ Setup complete!")
    print("\nTo run the application:")
    if sys.platform == 'win32':
        print("venv\\Scripts\\python run.py")
    else:
        print("source venv/bin/activate && python run.py")

if __name__ == '__main__':
    setup()
