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

# Fix for MPS memory allocation on Mac
os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"


_pipe = None

# Device setup
if torch.cuda.is_available():
    device = torch.device("cuda")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")


if torch.cuda.is_available():
    from google.colab import userdata
    HUGGING_FACE_API = userdata.get("HUGGING_FACE_API", None)
else:
    HUGGING_FACE_API = os.environ.get("HUGGING_FACE_API", None)

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
                    device=device,
                    token=HUGGING_FACE_API
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
                        device=device,
                        token=HUGGING_FACE_API
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
                        device=torch.device("cpu"),
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


import json
import re

def extract_json(text: str):
    """
    Extract the first valid JSON object from a text string.
    Handles deeply nested JSON and ignores braces inside strings.
    """

    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found")

    brace_count = 0
    in_string = False
    escape = False

    for i in range(start, len(text)):
        char = text[i]

        if char == '"' and not escape:
            in_string = not in_string

        if char == "\\" and not escape:
            escape = True
            continue
        else:
            escape = False

        if not in_string:
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1

        if brace_count == 0 and i > start:
            json_str = text[start:i + 1]
            return json.loads(fix_json_str(json_str))

    raise ValueError("Incomplete JSON object found")



# --- PROFILE EXTRACTION -------------------------------------------------------

def extract_user_profile(resume_text: str, max_new_tokens: int = 1024) -> dict:
    if not resume_text.strip():
        return {"error": "Resume text is required"}

    resume_text = resume_text[:10000]

    try:
        pipe = get_llama_pipeline()

        prompt = f"""
## Structured Resume Data Extraction

**Objective:** Extract all available information from the provided resume text and map it precisely into the required JSON schema.

**Resume Text:**
{resume_text}

**Required Output Schema (JSON Format):**
Please adhere strictly to the following structure, including data types for each field.

```json
{{
  "name": "string (Full name)",
  "email": "string (Primary email address)",
  "phone": "string (Formatted phone number)",
  "location": "string (City, State/Province, Country if available)",
  "links": {{
    "linkedin": "string (URL or empty string)",
    "github": "string (URL or empty string)",
    "website": "string (URL or empty string)"
  }},
  "summary": "string (A concise, professional summary or objective statement)",
  "skills": [
    "string (List of key technical and soft skills)"
  ],
  "experience": [
    {{
      "title": "string (Your role/position)",
      "company": "string (Company name)",
      "startDate": "string (Start date, e.g., 'YYYY-MM' or 'Month YYYY')",
      "endDate": "string (End date or 'Present')",
      "description": [
        "string (Bullet point summarizing a key responsibility or achievement)"
      ]
    }}
  ],
  "education": [
    {{
      "institution": "string (University or School name)",
      "degree": "string (Degree, e.g., 'M.S. in Computer Science')",
      "fieldOfStudy": "string (Specific field, if applicable)",
      "startDate": "string (Start date, e.g., 'YYYY')",
      "endDate": "string (End date or 'Present')",
      "gpa": "string (GPA if explicitly mentioned, otherwise empty string)"
    }}
  ],
  "projects": [
    {{
      "name": "string (Project title)",
      "description": "string (Brief project description and technologies used)",
      "link": "string (Project URL or empty string)"
    }}
  ]
}}
```
"""
# end the prompt

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
        print("The generated text is ", generated)

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
