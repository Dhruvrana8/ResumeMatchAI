from pydantic import BaseModel
from typing import List, Optional, Any

# We don't use ATSRequest for input anymore as we use Form/File params directly
# But we can define response schemas for documentation

class PersonalInfo(BaseModel):
    full_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    linkedin: Optional[str]
    github: Optional[str]
    portfolio: Optional[str]

class Skills(BaseModel):
    technical_skills: List[str]
    soft_skills: List[str]

class ResumeATSResponse(BaseModel):
    personal_information: PersonalInfo
    skills: Skills

class KeywordMatch(BaseModel):
    matched_count: int
    total_keywords: int
    matched_keywords: List[str]
    missing_keywords: List[str]

class ResumeVsJDResponse(BaseModel):
    ats_score: int
    keyword_match: KeywordMatch
    formatting_score: int