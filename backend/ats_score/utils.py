import logging
import json
import re
from fastapi import UploadFile, HTTPException
from .llm import generate_response
from .text_extract import extract_text_from_file

logger = logging.getLogger(__name__)

def fix_json_str(s: str) -> str:
    """Clean JSON to prevent model formatting issues"""
    s = s.strip()
    s = s.replace("“", "\"").replace("”", "\"")
    # Remove trailing commas in arrays/objects
    s = re.sub(r',\s*([\]}])', r'\1', s)
    s = s.replace("'", "\"")
    return s

def extract_json(text: str) -> dict:
    """
    Extract the first valid JSON object from a text string.
    """
    try:
        # Quick attempt
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found in response")

    # Stack based parsing to find the matching closing brace
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
            try:
                return json.loads(fix_json_str(json_str))
            except json.JSONDecodeError as e:
                # Try one more time with more aggressive cleanup?
                # For now just raise
                raise ValueError(f"Found JSON block but failed to parse: {e}")

    raise ValueError("Incomplete JSON object found")

async def analyze_resume(file: UploadFile, job_description: str, mode: str) -> dict:
    """
    Analyze the resume based on the selected mode.
    """
    # 1. Extract Text
    try:
        resume_text = await extract_text_from_file(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not resume_text:
        raise HTTPException(status_code=400, detail="Could not extract text from resume.")

    # 2. Select Prompt based on Mode
    if mode == "resume_ats":
        prompt = f"""
You are an intelligent and strict ATS (Applicant Tracking System) engine.
Your task is to analyze resumes based on the selected MODE.

--------------------
GLOBAL RULES:
--------------------
- Use ONLY the provided inputs.
- Do NOT hallucinate or assume missing information.
- If data is not found, return null or empty arrays.
- Return ONLY valid JSON.
- Do NOT include explanations, comments, or extra text.
- Follow the JSON schema EXACTLY as defined below.

--------------------
MODE: "resume_ats"
Purpose: Extract structured personal information and skills from the resume.

Required Output JSON Schema:
{{
    "personal_information": {{
    "full_name": null,
    "email": null,
    "phone": null,
    "location": null,
    "linkedin": null,
    "github": null,
    "portfolio": null
    }},
    "skills": {{
    "technical_skills": [],
    "soft_skills": []
    }}
}}

--------------------
INPUT DATA:
--------------------
RESUME TEXT:
\"\"\"
{resume_text[:10000]}
\"\"\"
"""
    elif mode == "resume_vs_jd":
        if not job_description:
             raise HTTPException(status_code=400, detail="Job description is required for 'resume_vs_jd' mode.")
        
        prompt = f"""
You are an intelligent and strict ATS (Applicant Tracking System) engine.
Your task is to analyze resumes based on the selected MODE.

--------------------
GLOBAL RULES:
--------------------
- Use ONLY the provided inputs.
- Do NOT hallucinate or assume missing information.
- If data is not found, return null or empty arrays.
- Return ONLY valid JSON.
- Do NOT include explanations, comments, or extra text.
- Follow the JSON schema EXACTLY as defined below.

--------------------
MODE: "resume_vs_jd"
Purpose: Compare the resume against a job description and evaluate ATS compatibility.

Analysis Requirements:
- Extract important keywords from the job description.
- Match them against the resume (exact and closely related terms).
- Evaluate overall relevance and role alignment.
- Evaluate ATS-friendly formatting.

Required Output JSON Schema:
{{
    "ats_score": 0,
    "keyword_match": {{
    "matched_count": 0,
    "total_keywords": 0,
    "matched_keywords": [],
    "missing_keywords": []
    }},
    "formatting_score": 0
}}

--------------------
INPUT DATA:
--------------------
RESUME TEXT:
\"\"\"
{resume_text[:10000]}
\"\"\"

JOB DESCRIPTION:
\"\"\"
{job_description[:5000]}
\"\"\"
"""
    else:
        raise HTTPException(status_code=400, detail=f"Invalid mode: {mode}")

    # 3. Call LLM
    try:
        response_text = generate_response(prompt)
        # logger.info(f"LLM Response: {response_text}") # Debug logging
        result = extract_json(response_text)
        return result
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze resume.")
