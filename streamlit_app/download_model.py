#!/usr/bin/env python3
"""
Helper script to download the Llama model for offline use.
Run this once with internet connection to cache the model locally.
"""

import os
import sys
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_id = "meta-llama/Llama-3.2-3B-Instruct"
token = os.environ.get("HUGGING_FACE_API", None)

if not token:
    print("ERROR: HUGGING_FACE_API environment variable not set!")
    print("\nPlease:")
    print("1. Get a token from https://huggingface.co/settings/tokens")
    print("2. Run: export HUGGING_FACE_API='your_token_here'")
    print("3. Accept the license at https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct")
    sys.exit(1)

print(f"Downloading model: {model_id}")
print("This may take several minutes depending on your connection...")

try:
    # Download tokenizer
    print("\n[1/2] Downloading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        model_id,
        token=token
    )
    print("✓ Tokenizer downloaded successfully")
    
    # Download model
    print("\n[2/2] Downloading model...")
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        token=token,
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True
    )
    print("✓ Model downloaded successfully")
    
    print("\n" + "="*60)
    print("SUCCESS! Model cached locally.")
    print("You can now use the model offline.")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nTroubleshooting:")
    print("1. Check your internet connection")
    print("2. Verify your Hugging Face token is valid")
    print("3. Ensure you've accepted the model license")
    print("4. Check Hugging Face status: https://status.huggingface.co/")
    sys.exit(1)
