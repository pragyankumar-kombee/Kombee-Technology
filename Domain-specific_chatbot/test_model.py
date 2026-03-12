import sys
import logging

logging.basicConfig(level=logging.INFO)

def test_imports():
    """Test if all required packages import correctly"""
    try:
        import torch  # type: ignore
        print(f"✅ torch: {torch.__version__}")
    except ImportError as e:
        print(f"❌ torch: {e}")
    
    try:
        import transformers  # type: ignore
        print(f"✅ transformers: {transformers.__version__}")
    except ImportError as e:
        print(f"❌ transformers: {e}")
    
    try:
        import flask  # type: ignore
        print(f"✅ flask: {flask.__version__}")
    except ImportError as e:
        print(f"❌ flask: {e}")

if __name__ == "__main__":
    test_imports()