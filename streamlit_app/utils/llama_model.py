import os
import logging
import torch
import torch.backends.mps
import re
import json
from dotenv import load_dotenv
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model configuration
model_id = "meta-llama/Llama-3.2-3B-Instruct"
HUGGING_FACE_API = os.environ.get("HUGGING_FACE_API", None)

_pipe = None

# Device setup
if torch.cuda.is_available():
    device = torch.device("cuda")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")


def get_llama_pipeline():
    """Get or create the Llama pipeline with lazy loading"""
    global _pipe

    if _pipe is None:
        try:
            from transformers import pipeline

            logger.info(f"Loading Llama model: {model_id}")

            # dtype fix for MPS/CPU models (FP16 breaks output)
            dtype = torch.float16 if device.type == "cuda" else torch.float32

            # Try loading from local cache first (offline mode)
            try:
                logger.info("Attempting to load model from local cache...")
                _pipe = pipeline(
                    "text-generation",
                    model=model_id,
                    torch_dtype=dtype,
                    device_map="auto",
                    token=HUGGING_FACE_API,
                    model_kwargs={"load_in_8bit": device.type == "cuda"}
                )
                logger.info("Successfully loaded model from local cache")
            except Exception as e1:
                logger.warning(f"Local cache load failed: {e1}")
                logger.info(
                    "Attempting to download model from Hugging Face...")

                # Check if token is set
                if not HUGGING_FACE_API:
                    logger.error(
                        "HUGGING_FACE_API token not set. Please set it as an environment variable.")
                    raise RuntimeError(
                        "Hugging Face token required. Please:\n"
                        "1. Get a token from https://huggingface.co/settings/tokens\n"
                        "2. Set environment variable: export HUGGING_FACE_API='your_token_here'\n"
                        "3. Accept the model license at https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct"
                    )

                try:
                    # Try downloading with token
                    _pipe = pipeline(
                        "text-generation",
                        model=model_id,
                        torch_dtype=dtype,
                        device_map="auto",
                        token=HUGGING_FACE_API,
                        model_kwargs={"load_in_8bit": device.type == "cuda"}
                    )
                    logger.info("Successfully downloaded and loaded model")
                except Exception as e2:
                    logger.warning(f"Primary load failed: {e2}")
                    logger.info("Attempting CPU fallback...")
                    # Fallback to CPU
                    _pipe = pipeline(
                        "text-generation",
                        model=model_id,
                        torch_dtype=torch.float32,
                        device_map="cpu",
                        token=HUGGING_FACE_API
                    )
                    logger.info("Successfully loaded model on CPU")

        except Exception as e:
            logger.error(f"Pipeline load error: {e}")
            error_msg = (
                f"Unable to load LLAMA model. Error: {str(e)}\n\n"
                "Troubleshooting steps:\n"
                "1. Check your internet connection\n"
                "2. Ensure HUGGING_FACE_API environment variable is set\n"
                "3. Accept the model license at https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct\n"
                "4. Try downloading the model manually first\n"
                "5. Check Hugging Face status: https://status.huggingface.co/"
            )
            raise RuntimeError(error_msg)

    return _pipe


# --- JSON FIXERS --------------------------------------------------------------

def fix_json_str(s: str):
    """Clean JSON to prevent model formatting issues"""
    s = s.strip()
    s = s.replace("“", "\"").replace("”", "\"")
    s = re.sub(r',\s*([\]}])', r'\1', s)
    s = s.replace("'", "\"")
    return s


def extract_json(text: str):
    """Extract the first valid JSON object from text"""
    # Capture deeply nested JSON
    pattern = r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}'
    match = re.search(pattern, text, re.DOTALL)

    if not match:
        raise ValueError("JSON not found in output.")

    cleaned = fix_json_str(match.group(0))
    return json.loads(cleaned)


# --- PROFILE EXTRACTION -------------------------------------------------------

def extract_user_profile(resume_text: str, max_new_tokens: int = 512) -> dict:
    if not resume_text.strip():
        return {"error": "Resume text is required"}

    resume_text = resume_text[:30000]

    try:
        pipe = get_llama_pipeline()

        prompt = f"""
Extract structured data from this resume. 
Return ONLY valid JSON. No explanation.

Resume:
{resume_text}

JSON Format:
{{
  "name": "",
  "email": "",
  "phone": "",
  "location": "",
  "links": {{
    "linkedin": "",
    "github": "",
    "website": ""
  }},
  "summary": "",
  "skills": [],
  "experience": [],
  "education": [],
  "projects": []
}}

Return JSON only:
"""

        logger.info("Extracting user profile...")

        outputs = pipe(
            prompt,
            max_new_tokens=max_new_tokens,
            temperature=0.1,
            do_sample=False,
            pad_token_id=pipe.tokenizer.eos_token_id,
            num_return_sequences=1,
            return_full_text=False
        )

        generated = outputs[0].get("generated_text", "")

        return extract_json(generated)

    except Exception as e:
        logger.error(f"LLM JSON extraction failed: {e}")
        return fallback_profile_extraction(resume_text)


# --- FALLBACK -----------------------------------------------------------------

def fallback_profile_extraction(resume_text: str) -> dict:
    """Basic fallback when LLM fails"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'

    emails = re.findall(email_pattern, resume_text)
    phones = re.findall(phone_pattern, resume_text)

    return {
        "name": "",
        "email": emails[0] if emails else "",
        "phone": phones[0] if phones else "",
        "location": "",
        "links": {"linkedin": "", "github": "", "website": ""},
        "summary": "",
        "skills": [],
        "experience": [],
        "education": [],
        "projects": []
    }


# --- RESUME ANALYSIS ----------------------------------------------------------

def analyze_resume_and_job_description(resume_text, job_description, max_new_tokens=256):
    if not resume_text.strip() or not job_description.strip():
        return "Error: resume and job description are required."

    resume_text = resume_text[:2000]
    job_description = job_description[:2000]

    try:
        pipe = get_llama_pipeline()

        prompt = f"""
You are an HR expert. Analyze this resume against the job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Return analysis with:
- Match % (0-100)
- Strengths
- Weaknesses
- Recommendations
"""

        outputs = pipe(
            prompt,
            max_new_tokens=max_new_tokens,
            temperature=0.3,
            do_sample=True,
            top_p=0.9,
            top_k=50,
            repetition_penalty=1.1,
            pad_token_id=pipe.tokenizer.eos_token_id,
            return_full_text=False,
        )

        return outputs[0]["generated_text"].strip()

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return "Error analyzing resume."


# --- Placeholder --------------------------------------------------------------

def analyze_resume_file(file_path, job_description, max_new_tokens=256):
    return "PDF/DOCX analysis not implemented yet."


# Multimodal models (future)
MULTIMODAL_MODELS = {
    "llava": {"model_id": "llava-hf/llava-1.5-7b-hf"},
    "gpt4v": {"model_id": "gpt-4-vision-preview"}
}
