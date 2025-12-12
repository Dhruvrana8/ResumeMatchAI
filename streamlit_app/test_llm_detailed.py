#!/usr/bin/env python3
"""
Detailed test script for LLM analysis functionality with diagnostics
"""

import os
import sys
import traceback

def test_dependencies():
    """Test if all required dependencies are available"""
    print("🔍 Testing dependencies...")

    try:
        import torch
        print(f"✅ torch {torch.__version__} available")
        print(f"   CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   CUDA version: {torch.version.cuda}")
    except ImportError as e:
        print(f"❌ torch not available: {e}")
        return False

    try:
        import transformers
        print(f"✅ transformers {transformers.__version__} available")
    except ImportError as e:
        print(f"❌ transformers not available: {e}")
        return False

    try:
        import accelerate
        print(f"✅ accelerate available")
    except ImportError as e:
        print(f"❌ accelerate not available: {e}")
        return False

    try:
        import bitsandbytes
        print(f"✅ bitsandbytes available")
    except ImportError as e:
        print(f"⚠️  bitsandbytes not available (optional for quantization)")

    return True

def test_model_loading():
    """Test if the model can be loaded"""
    print("\n🔍 Testing model loading...")

    if not os.environ.get("HUGGING_FACE_API"):
        print("⚠️  HUGGING_FACE_API environment variable not set")
        print("💡 Skipping model loading test. Set your token to test fully:")
        print("   export HUGGING_FACE_API='your_token_here'")
        return True

    try:
        from utils.llama_model import get_llama_pipeline
        print("🔄 Attempting to load Llama model...")
        pipe = get_llama_pipeline()
        print("✅ Model loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        print(f"🔍 Full traceback:\n{traceback.format_exc()}")
        return False

def test_simple_generation():
    """Test simple text generation"""
    print("\n🔍 Testing simple generation...")

    if not os.environ.get("HUGGING_FACE_API"):
        print("⚠️  Skipping generation test (no API token)")
        return True

    try:
        from utils.llama_model import get_llama_pipeline
        pipe = get_llama_pipeline()

        # Very simple test
        test_prompt = "Hello, how are you?"
        print(f"Testing with prompt: '{test_prompt}'")

        outputs = pipe(
            test_prompt,
            max_new_tokens=20,
            temperature=0.1,
            do_sample=False,
            pad_token_id=pipe.tokenizer.eos_token_id
        )

        if outputs and len(outputs) > 0:
            response = outputs[0].get('generated_text', '')
            print(f"✅ Generation successful: '{response[:100]}...'")
            return True
        else:
            print("❌ Empty response from model")
            return False

    except Exception as e:
        print(f"❌ Generation failed: {e}")
        print(f"🔍 Full traceback:\n{traceback.format_exc()}")
        return False

def test_resume_analysis():
    """Test resume analysis with sample data"""
    print("\n🔍 Testing resume analysis...")

    if not os.environ.get("HUGGING_FACE_API"):
        print("⚠️  Skipping analysis test (no API token)")
        return True

    try:
        from utils.llama_model import analyze_resume_and_job_description

        # Very short sample data to minimize issues
        resume = "John Doe. Software Engineer with Python experience."
        job_desc = "Looking for Python developer with 2 years experience."

        print("Testing with sample resume and job description...")
        result = analyze_resume_and_job_description(resume, job_desc, max_new_tokens=100)

        if result and not result.startswith("Error"):
            print(f"✅ Analysis successful (length: {len(result)} characters)")
            print(f"📄 Preview: {result[:200]}...")
            return True
        else:
            print(f"❌ Analysis failed: {result}")
            return False

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        print(f"🔍 Full traceback:\n{traceback.format_exc()}")
        return False

def main():
    """Run all tests"""
    print("🧪 Detailed LLM Analysis Test Suite")
    print("=" * 50)

    all_passed = True

    # Test dependencies
    all_passed &= test_dependencies()

    # Test model loading
    all_passed &= test_model_loading()

    # Test simple generation
    all_passed &= test_simple_generation()

    # Test resume analysis
    all_passed &= test_resume_analysis()

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed!")
    else:
        print("💥 Some tests failed!")
        print("\n🔧 Troubleshooting tips:")
        print("1. Update all packages: pip install --upgrade torch transformers accelerate bitsandbytes")
        print("2. Check your Hugging Face API token")
        print("3. Try restarting your Python session")
        print("4. If using GPU, try CPU-only mode (set CUDA_VISIBLE_DEVICES='')")
        print("5. Check available RAM (model needs ~2-4GB)")

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)