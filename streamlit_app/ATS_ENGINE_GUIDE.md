# ATS Engine - Usage Guide

## Overview

The ATS Engine is a professional Applicant Tracking System that analyzes resumes with three operational modes. It outputs **ONLY valid JSON** with no markdown or explanations, behaving strictly like an ATS system.

## Installation

The ATS engine is already integrated into the ResumeMatchAI project. No additional dependencies are required beyond what's in `requirements.txt`.

## Modes

### 1. resume_only

Analyze resume quality from a general ATS perspective without a job description.

**Input:**

```python
{
  "mode": "resume_only",
  "resume_text": "<raw resume text>"
}
```

**Output:**

```json
{
  "mode": "resume_only",
  "final_ats_score": 75.3,
  "score_breakdown": {
    "structure_formatting": 80.0,
    "section_completeness": 75.0,
    "keyword_strength": 70.5,
    "skills_clarity": 85.0,
    "experience_quality": 72.0,
    "consistency": 80.0,
    "ats_readability": 75.0
  },
  "detected_sections": {
    "summary": true,
    "skills": true,
    "experience": true,
    "education": true,
    "projects": false
  },
  "strengths": [
    "Strong Structure Formatting (80/100)",
    "Strong Skills Clarity (85/100)"
  ],
  "weaknesses": ["Weak Keyword Strength (71/100)"],
  "improvement_suggestions": [
    "Incorporate more industry-relevant keywords throughout your resume",
    "Quantify achievements with metrics and use strong action verbs"
  ]
}
```

### 2. resume_job_match

Match resume against a specific job description.

**Input:**

```python
{
  "mode": "resume_job_match",
  "resume_text": "<raw resume text>",
  "job_description": "<raw job description text>"
}
```

**Output:**

```json
{
  "mode": "resume_job_match",
  "final_ats_score": 68.5,
  "job_keywords": {
    "technical_skills": ["python", "javascript", "react"],
    "soft_skills": ["communication", "leadership"],
    "tools_technologies": ["aws", "docker", "kubernetes"],
    "required_experience": ["5 years experience"]
  },
  "resume_keyword_match": {
    "matched_keywords": ["python", "javascript", "aws"],
    "partial_matches": ["react", "docker"],
    "missing_keywords": ["kubernetes", "leadership"]
  },
  "score_breakdown": {
    "keyword_match": 65.0,
    "experience_alignment": 75.0,
    "skills_relevance": 70.0,
    "semantic_similarity": 60.0
  },
  "match_analysis": {
    "strengths": [
      "Good keyword match with 8 matched terms",
      "Solid work history with 3 positions"
    ],
    "gaps": [
      "Missing 5 key job requirements",
      "Limited work experience history"
    ]
  },
  "recommendations": [
    "Add these critical keywords to your resume: kubernetes, leadership",
    "Emphasize skills that directly match the job description"
  ]
}
```

### 3. resume_builder

Resume improvement assistance (not implemented).

**Input:**

```python
{
  "mode": "resume_builder"
}
```

**Output:**

```json
{
  "mode": "resume_builder",
  "status": "not_implemented",
  "message": "Resume builder functionality is not available yet."
}
```

## Usage Examples

### Python API

```python
from utils.ats_engine import process_ats_request

# Example 1: Resume-only analysis
result = process_ats_request({
    "mode": "resume_only",
    "resume_text": "Your resume text here..."
})
print(result)

# Example 2: Resume-job match
result = process_ats_request({
    "mode": "resume_job_match",
    "resume_text": "Your resume text here...",
    "job_description": "Job description here..."
})
print(result)
```

### Command Line

```bash
# Run examples
python ats_engine_examples.py

# Run tests
python test_ats_engine.py
```

## Integration with Streamlit App

To integrate the ATS engine into the Streamlit app, add a new page or section:

```python
from utils.ats_engine import process_ats_request

def page_ats_engine():
    st.title("ATS Engine - JSON Mode")

    mode = st.selectbox("Select Mode", ["resume_only", "resume_job_match", "resume_builder"])
    resume_text = st.text_area("Resume Text")

    if mode == "resume_job_match":
        job_description = st.text_area("Job Description")

    if st.button("Analyze"):
        input_data = {"mode": mode, "resume_text": resume_text}
        if mode == "resume_job_match":
            input_data["job_description"] = job_description

        result = process_ats_request(input_data)
        st.json(result)
```

## Error Handling

The engine returns error messages in JSON format:

```json
{
  "error": "Resume text is required",
  "mode": "resume_only",
  "final_ats_score": 0
}
```

Common errors:

- Missing mode
- Invalid mode
- Missing resume text
- Missing job description (for resume_job_match mode)

## Scoring Methodology

### Resume-Only Mode Weights:

- Structure & Formatting: 15%
- Section Completeness: 15%
- Keyword Strength: 15%
- Skills Clarity: 15%
- Experience Quality: 20%
- Consistency: 10%
- ATS Readability: 10%

### Resume-Job Match Mode Weights:

- Keyword Match: 40%
- Experience Alignment: 25%
- Skills Relevance: 25%
- Semantic Similarity: 10%

## Files

- `utils/ats_engine.py` - Main ATS engine implementation
- `test_ats_engine.py` - Comprehensive test suite
- `ats_engine_examples.py` - Usage examples
- `ATS_ENGINE_GUIDE.md` - This documentation

## Testing

Run the test suite to verify functionality:

```bash
cd "/Users/dhruv/code/Machine Learning/Projects/ResumeMatchAI/streamlit_app"
python test_ats_engine.py
```

Tests include:

- All three modes
- Error handling
- JSON validity
- Score range validation (0-100)
- Schema compliance
