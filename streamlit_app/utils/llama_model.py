import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model configuration
model_id = "meta-llama/Llama-3.2-1B"
HUGGING_FACE_API = os.environ.get("HUGGING_FACE_API", None)

# Global variable to store the pipeline (lazy loading)
_pipe = None

def get_llama_pipeline():
    """Get or create the Llama pipeline with lazy loading"""
    global _pipe
    if _pipe is None:
        try:
            # Import here to handle cases where torch/transformers aren't available
            import torch
            from transformers import pipeline

            logger.info(f"Loading Llama model: {model_id}")

            # Try different configurations for better compatibility
            try:
                _pipe = pipeline(
                    "text-generation",
                    model=model_id,
                    torch_dtype=torch.float16,  # Use float16 instead of bfloat16 for better compatibility
                    device_map="auto",
                    token=HUGGING_FACE_API,
                    model_kwargs={"load_in_8bit": True}  # Use 8-bit quantization to save memory
                )
            except Exception as e1:
                logger.warning(f"Failed to load with quantization, trying standard config: {str(e1)}")
                try:
                    _pipe = pipeline(
                        "text-generation",
                        model=model_id,
                        torch_dtype=torch.float16,
                        device_map="auto",
                        token=HUGGING_FACE_API
                    )
                except Exception as e2:
                    logger.warning(f"Failed with float16, trying float32: {str(e2)}")
                    _pipe = pipeline(
                        "text-generation",
                        model=model_id,
                        torch_dtype=torch.float32,  # Fallback to float32
                        device_map="cpu",  # Force CPU if GPU issues
                        token=HUGGING_FACE_API
                    )

            logger.info("Llama model loaded successfully")
        except ImportError as e:
            logger.error(f"Missing required dependencies: {str(e)}")
            raise ImportError(f"Required packages not installed. Please install: pip install torch transformers accelerate bitsandbytes")
        except Exception as e:
            logger.error(f"Failed to load Llama model: {str(e)}")
            raise ValueError(f"Could not load Llama model. Please check your Hugging Face API token. Error: {str(e)}")
    return _pipe

def analyze_resume_and_job_description(resume_text, job_description, max_new_tokens=512):
    """
    Use Llama model to analyze resume against job description

    Args:
        resume_text (str): The full resume text
        job_description (str): The full job description text
        max_new_tokens (int): Maximum number of new tokens to generate

    Returns:
        str: LLM analysis result
    """

    if not resume_text.strip() or not job_description.strip():
        return "Error: Both resume and job description are required for analysis."

    # Limit input length to prevent issues (Llama 3.2-1B has token limits)
    max_input_length = 2000  # Conservative limit
    resume_text = resume_text[:max_input_length] if len(resume_text) > max_input_length else resume_text
    job_description = job_description[:max_input_length] if len(job_description) > max_input_length else job_description

    try:
        pipe = get_llama_pipeline()

        # Create a more focused prompt to reduce token usage
        prompt = f"""You are an HR expert. Analyze this resume against the job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Provide analysis with:
1. Match percentage (0-100%)
2. Key strengths
3. Weaknesses/gaps
4. Recommendations

Be concise and professional."""

        logger.info("Generating LLM analysis...")

        # Try multiple generation strategies for robustness
        try:
            # First try with conservative parameters
            outputs = pipe(
                prompt,
                max_new_tokens=min(max_new_tokens, 256),  # Reduce token limit
                temperature=0.3,  # Lower temperature for more stable generation
                do_sample=True,
                top_p=0.9,  # Add top_p for better sampling
                top_k=50,   # Add top_k for better sampling
                repetition_penalty=1.1,  # Prevent repetition
                pad_token_id=pipe.tokenizer.eos_token_id,
                num_return_sequences=1,
                return_full_text=False  # Don't return the input prompt
            )
        except Exception as gen_error:
            logger.warning(f"Primary generation failed, trying fallback: {str(gen_error)}")
            # Fallback with even more conservative parameters
            try:
                outputs = pipe(
                    prompt,
                    max_new_tokens=128,  # Very conservative token limit
                    temperature=0.1,  # Very low temperature
                    do_sample=False,  # Greedy decoding for stability
                    pad_token_id=pipe.tokenizer.eos_token_id,
                    num_return_sequences=1,
                    return_full_text=False
                )
            except Exception as fallback_error:
                logger.error(f"Fallback generation also failed: {str(fallback_error)}")
                return f"Error: Model generation failed even with conservative parameters. This might be due to model/tokenizer compatibility issues. Original error: {str(gen_error)}"

        # Extract the generated text
        if isinstance(outputs, list) and len(outputs) > 0:
            generated_text = outputs[0].get('generated_text', '')
        else:
            generated_text = str(outputs)

        # Clean up the analysis text
        analysis = generated_text.strip()

        # Remove any common artifacts
        if analysis.startswith(prompt):
            analysis = analysis[len(prompt):].strip()

        if not analysis:
            return "Error: Model generated empty response. This might indicate input processing issues."

        logger.info("LLM analysis completed successfully")
        return analysis

    except Exception as e:
        error_msg = f"Error during LLM analysis: {str(e)}"
        logger.error(error_msg)

        # Provide more helpful error messages
        if "probability tensor" in str(e).lower():
            return "Error: Probability tensor issue detected. This usually indicates model/tokenizer compatibility problems. Try updating your transformers and torch versions."
        elif "out of memory" in str(e).lower():
            return "Error: Out of memory. Try closing other applications or using a smaller model."
        elif "token" in str(e).lower():
            return "Error: Tokenization issue. Your input might be too complex for the model."

        return error_msg
