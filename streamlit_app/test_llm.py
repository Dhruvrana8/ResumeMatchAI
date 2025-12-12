#!/usr/bin/env python3
"""
Test script for LLM analysis functionality
"""

import os
import sys
sys.path.append('.')

def test_llm_import():
    """Test if LLM model can be imported"""
    try:
        # Just test basic imports without loading the model
        try:
            import torch
            from transformers import pipeline
            print("✅ Basic dependencies (torch, transformers) imported successfully")
            print(f"   torch version: {torch.__version__}")
            deps_available = True
        except ImportError:
            print("⚠️  Basic dependencies (torch, transformers) not available")
            print("💡 To enable full functionality, install: pip install torch transformers accelerate")
            deps_available = False

        # Test if we can import our functions (but not call them)
        from utils.llama_model import analyze_resume_and_job_description
        print("✅ LLM module functions imported successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to import LLM module: {e}")
        return False

def test_llm_analysis():
    """Test LLM analysis with sample data"""
    try:
        # Sample resume
        resume = """
        John Doe
        Software Engineer
        5 years experience in Python, JavaScript, React
        Bachelor's in Computer Science
        Skills: Python, JavaScript, React, Node.js, SQL
        """

        # Sample job description
        job_desc = """
        Senior Software Engineer
        Requirements: 3+ years Python, React experience
        Preferred: Node.js, SQL knowledge
        """

        print("🔄 Testing LLM analysis (this may take a few minutes)...")

        # Only test if HUGGING_FACE_API is set
        if not os.environ.get("HUGGING_FACE_API"):
            print("⚠️  HUGGING_FACE_API environment variable not set. Skipping actual LLM test.")
            print("💡 To test the full functionality, set your Hugging Face API token:")
            print("   export HUGGING_FACE_API='your_token_here'")
            print("✅ Test skipped due to missing API token (this is expected)")
            return True

        from utils.llama_model import analyze_resume_and_job_description
        result = analyze_resume_and_job_description(resume, job_desc)
        print("✅ LLM analysis completed successfully")
        print(f"📄 Analysis length: {len(result)} characters")
        return True

    except Exception as e:
        print(f"❌ LLM analysis failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing LLM functionality...\n")

    success = True
    success &= test_llm_import()
    success &= test_llm_analysis()

    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)