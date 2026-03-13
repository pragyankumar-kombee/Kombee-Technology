# AI Personal Assistant - Setup Instructions

## Quick Start

### 1. Install Dependencies

First, uninstall any conflicting packages and reinstall from requirements.txt:

```bash
pip uninstall huggingface-hub transformers tokenizers -y
pip install -r requirements.txt
```

Or use the automated setup script:

```bash
python setup.py
```

### 2. Configure Environment Variables

Edit the `.env` file and add your Hugging Face API token:

```
HUGGINGFACE_API_TOKEN=your-actual-token-here
```

Get your token from: https://huggingface.co/settings/tokens

### 3. Run the Application

```bash
python run.py
```

The application will be available at: http://localhost:5000

## What Was Fixed

✅ Updated requirements.txt with compatible package versions
✅ Fixed app/__init__.py with proper Flask app factory pattern
✅ Updated routes.py with correct blueprint initialization
✅ Enhanced ai_assistant.py with better error handling
✅ Created history.html template for conversation history
✅ Updated setup.py for automated installation

## Features

- Chat interface with AI assistant
- Conversation history tracking
- Session management
- Error handling for API issues
- Model loading status messages

## Troubleshooting

If you see "The model is loading", wait a few seconds and try again. The first request to a Hugging Face model can take time to load.

For connection errors, check your internet connection and API token validity.
