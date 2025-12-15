import os
import torch
import logging
from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Model configuration
# Using a smaller model or the same one as before? 
# The user's code had "meta-llama/Llama-3.2-3B-Instruct".
MODEL_ID = "meta-llama/Llama-3.2-3B-Instruct"

_pipe = None

def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    elif torch.backends.mps.is_available():
        return torch.device("mps")
    else:
        return torch.device("cpu")

def get_llama_pipeline():
    """Get or create the Llama pipeline with lazy loading"""
    global _pipe

    if _pipe is not None:
        return _pipe

    device = get_device()
    hf_token = os.environ.get("HUGGING_FACE_API")

    if not hf_token:
        # Fallback to checking google colab userdata style if needed, but this is backend
        logger.warning("HUGGING_FACE_API not set. LLM may fail to load if model is gated.")

    logger.info(f"Loading Llama model: {MODEL_ID} on {device}")

    try:
        # dtype fix for MPS/CPU models
        dtype = torch.float16 if device.type == "cuda" else torch.float32
        
        _pipe = pipeline(
            "text-generation",
            model=MODEL_ID,
            torch_dtype=dtype,
            device=device,
            token=hf_token
        )
        logger.info("Successfully loaded model")
        
    except Exception as e:
        logger.error(f"Failed to load LLM pipeline: {e}")
        raise RuntimeError(f"Could not load Llama model: {e}")

    return _pipe

def generate_response(prompt: str, max_new_tokens: int = 2048, temperature: float = 0.1) -> str:
    """
    Generate a response from the LLM.
    """
    try:
        pipe = get_llama_pipeline()
        
        outputs = pipe(
            prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=True if temperature > 0 else False,
            pad_token_id=pipe.tokenizer.eos_token_id,
            num_return_sequences=1,
            return_full_text=False
        )
        
        return outputs[0]["generated_text"].strip()
        
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        # Identify if it's an OOM or connection error?
        # For now, re-raise to be handled by caller
        raise e
