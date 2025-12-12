"""
User Profile Extractor using LLM
"""

import os
import logging
import json
import re
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def extract_user_profile_with_llm(resume_text: str) -> Dict[str, Any]:
    """
    Extract structured user profile from resume using LLM
    
    Args:
        resume_text: Full text content of the resume
    
    Returns:
        dict: Structured user profile data
    """
    try:
        from utils.llama_model import get_llama_pipeline
        
        pipe = get_llama_pipeline()
        
        # Create prompt for profile extraction
        prompt = f"""Extract the following information from this resume in JSON format. Return ONLY valid JSON, no additional text.

RESUME:
{resume_text[:1500]}

Extract and return a JSON object with this exact structure:
{{
  "personal_info": {{
    "name": "full name",
    "email": "email address",
    "phone": "phone number",
    "location": "city, state/country",
    "linkedin": "linkedin url if present",
    "github": "github url if present",
    "website": "personal website if present"
  }},
  "summary": "professional summary or objective",
  "skills": ["skill1", "skill2", "skill3"],
  "experience": [
    {{
      "title": "job title",
      "company": "company name",
      "location": "location",
      "start_date": "start date",
      "end_date": "end date or 'Present'",
      "description": "job description"
    }}
  ],
  "education": [
    {{
      "degree": "degree name",
      "institution": "school/university name",
      "location": "location",
      "graduation_date": "graduation year",
      "gpa": "GPA if mentioned"
    }}
  ],
  "certifications": ["certification1", "certification2"],
  "projects": [
    {{
      "name": "project name",
      "description": "project description",
      "technologies": ["tech1", "tech2"]
    }}
  ],
  "languages": ["language1", "language2"],
  "awards": ["award1", "award2"]
}}

Return ONLY the JSON object:"""

        logger.info("Extracting user profile with LLM...")
        
        # Generate profile extraction
        outputs = pipe(
            prompt,
            max_new_tokens=1024,
            temperature=0.1,  # Low temperature for structured output
            do_sample=False,  # Greedy decoding for consistency
            pad_token_id=pipe.tokenizer.eos_token_id,
            num_return_sequences=1,
            return_full_text=False
        )
        
        # Extract generated text
        if isinstance(outputs, list) and len(outputs) > 0:
            generated_text = outputs[0].get('generated_text', '')
        else:
            generated_text = str(outputs)
        
        # Clean and extract JSON
        profile_json = _extract_json_from_text(generated_text)
        
        if profile_json:
            logger.info("User profile extracted successfully")
            return profile_json
        else:
            logger.warning("Failed to extract valid JSON, using fallback extraction")
            return _fallback_extraction(resume_text)
            
    except Exception as e:
        logger.error(f"LLM profile extraction failed: {str(e)}")
        return _fallback_extraction(resume_text)

def _extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON object from LLM response"""
    try:
        # Try to find JSON in the text
        # Look for content between { and }
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(0)
            # Try to parse JSON
            profile_data = json.loads(json_str)
            return profile_data
        else:
            # Try parsing the entire text
            profile_data = json.loads(text.strip())
            return profile_data
            
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parsing failed: {str(e)}")
        logger.debug(f"Text that failed to parse: {text[:500]}")
        return None
    except Exception as e:
        logger.error(f"Error extracting JSON: {str(e)}")
        return None

def _fallback_extraction(resume_text: str) -> Dict[str, Any]:
    """Fallback extraction using regex patterns if LLM fails"""
    logger.info("Using fallback extraction method")
    
    # Basic regex patterns for extraction
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    
    emails = re.findall(email_pattern, resume_text)
    phones = re.findall(phone_pattern, resume_text)
    
    # Extract basic structure
    profile = {
        "personal_info": {
            "email": emails[0] if emails else "",
            "phone": phones[0] if phones else "",
            "name": "",
            "location": "",
            "linkedin": "",
            "github": "",
            "website": ""
        },
        "summary": "",
        "skills": [],
        "experience": [],
        "education": [],
        "certifications": [],
        "projects": [],
        "languages": [],
        "awards": []
    }
    
    return profile

def validate_profile(profile: Dict[str, Any]) -> tuple[bool, list]:
    """
    Validate user profile structure
    
    Returns:
        tuple: (is_valid, list_of_errors)
    """
    errors = []
    required_fields = ["personal_info", "skills", "experience", "education"]
    
    for field in required_fields:
        if field not in profile:
            errors.append(f"Missing required field: {field}")
    
    if "personal_info" in profile:
        if not isinstance(profile["personal_info"], dict):
            errors.append("personal_info must be a dictionary")
    
    if "skills" in profile:
        if not isinstance(profile["skills"], list):
            errors.append("skills must be a list")
    
    return len(errors) == 0, errors
