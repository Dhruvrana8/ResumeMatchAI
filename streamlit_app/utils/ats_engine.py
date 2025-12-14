"""
ATS Engine - Professional Applicant Tracking System
Behaves strictly like an ATS system, NOT a conversational assistant.
Outputs ONLY valid JSON with no markdown or explanations.
"""

import json
import re
from typing import Dict, List, Optional
from collections import defaultdict

# Import existing utilities
from utils.keywords_extraction import (
    get_keywords,
    categorize_keywords,
    enhanced_keyword_match_score,
    extract_structured_keywords
)
from utils.resume_keywords import get_comprehensive_resume_info
from utils.ats_scoring import ATSScorer


class ATSEngine:
    """
    Professional ATS Engine with three operational modes:
    - resume_only: Analyze resume quality without job description
    - resume_job_match: Match resume against job description
    - resume_builder: Resume improvement assistance (not implemented)
    """
    
    def __init__(self):
        self.scorer = ATSScorer()
    
    def process_request(self, input_data: dict) -> dict:
        """
        Main entry point for ATS engine.
        
        Args:
            input_data: Dictionary with mode, resume_text, and optional job_description
            
        Returns:
            Dictionary with ATS analysis results (JSON-serializable)
        """
        # Validate input
        if not isinstance(input_data, dict):
            return {"error": "Input must be a dictionary"}
        
        mode = input_data.get("mode")
        if not mode:
            return {"error": "Mode is required"}
        
        # Route to appropriate handler
        if mode == "resume_only":
            return self._analyze_resume_only(input_data)
        elif mode == "resume_job_match":
            return self._analyze_resume_job_match(input_data)
        elif mode == "resume_builder":
            return self._analyze_resume_builder(input_data)
        else:
            return {"error": f"Invalid mode: {mode}. Supported modes: resume_only, resume_job_match, resume_builder"}
    
    def _analyze_resume_only(self, input_data: dict) -> dict:
        """
        Analyze resume quality from a general ATS perspective.
        
        Evaluation Criteria:
        1. Resume structure & formatting
        2. Section completeness
        3. Generic industry keyword strength
        4. Skill clarity & categorization
        5. Experience quality (impact, action verbs, metrics)
        6. Consistency (dates, roles, formatting)
        7. ATS readability & parsing compatibility
        """
        resume_text = input_data.get("resume_text", "")
        
        if not resume_text or not resume_text.strip():
            return {
                "mode": "resume_only",
                "error": "Resume text is required",
                "final_ats_score": 0
            }
        
        # Extract comprehensive resume information
        try:
            resume_info = get_comprehensive_resume_info(resume_text)
        except Exception as e:
            resume_info = {}
        
        # Extract keywords for analysis
        resume_keywords = get_keywords(resume_text)
        
        # Calculate component scores
        structure_score = self._calculate_structure_formatting(resume_text, resume_info)
        section_score = self._calculate_section_completeness(resume_info)
        keyword_score = self._calculate_keyword_strength(resume_keywords, resume_text)
        skills_score = self._calculate_skills_clarity(resume_info, resume_text)
        experience_score = self._calculate_experience_quality(resume_info, resume_text)
        consistency_score = self._calculate_consistency(resume_text, resume_info)
        readability_score = self._calculate_ats_readability(resume_text)
        
        # Calculate weighted final score
        weights = {
            'structure_formatting': 0.15,
            'section_completeness': 0.15,
            'keyword_strength': 0.15,
            'skills_clarity': 0.15,
            'experience_quality': 0.20,
            'consistency': 0.10,
            'ats_readability': 0.10
        }
        
        final_score = (
            structure_score * weights['structure_formatting'] +
            section_score * weights['section_completeness'] +
            keyword_score * weights['keyword_strength'] +
            skills_score * weights['skills_clarity'] +
            experience_score * weights['experience_quality'] +
            consistency_score * weights['consistency'] +
            readability_score * weights['ats_readability']
        )
        
        # Detect sections
        detected_sections = {
            "summary": bool(resume_info.get('professional_summary')),
            "skills": bool(resume_info.get('skills')),
            "experience": bool(resume_info.get('work_experience')),
            "education": bool(resume_info.get('education')),
            "projects": bool(resume_info.get('projects'))
        }
        
        # Generate strengths and weaknesses
        strengths, weaknesses = self._generate_strengths_weaknesses(
            {
                'structure_formatting': structure_score,
                'section_completeness': section_score,
                'keyword_strength': keyword_score,
                'skills_clarity': skills_score,
                'experience_quality': experience_score,
                'consistency': consistency_score,
                'ats_readability': readability_score
            },
            resume_info,
            resume_text
        )
        
        # Generate improvement suggestions
        suggestions = self._generate_improvement_suggestions(
            {
                'structure_formatting': structure_score,
                'section_completeness': section_score,
                'keyword_strength': keyword_score,
                'skills_clarity': skills_score,
                'experience_quality': experience_score,
                'consistency': consistency_score,
                'ats_readability': readability_score
            },
            detected_sections
        )
        
        return {
            "mode": "resume_only",
            "final_ats_score": round(final_score, 1),
            "score_breakdown": {
                "structure_formatting": round(structure_score, 1),
                "section_completeness": round(section_score, 1),
                "keyword_strength": round(keyword_score, 1),
                "skills_clarity": round(skills_score, 1),
                "experience_quality": round(experience_score, 1),
                "consistency": round(consistency_score, 1),
                "ats_readability": round(readability_score, 1)
            },
            "detected_sections": detected_sections,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "improvement_suggestions": suggestions
        }
    
    def _analyze_resume_job_match(self, input_data: dict) -> dict:
        """
        Evaluate how well the resume matches the provided job description.
        
        Steps:
        1. Extract key requirements and keywords from job description
        2. Match them against resume content (exact + semantic)
        3. Identify missing critical skills or experience
        4. Evaluate role alignment and seniority match
        """
        resume_text = input_data.get("resume_text", "")
        job_description = input_data.get("job_description", "")
        
        if not resume_text or not resume_text.strip():
            return {
                "mode": "resume_job_match",
                "error": "Resume text is required",
                "final_ats_score": 0
            }
        
        if not job_description or not job_description.strip():
            return {
                "mode": "resume_job_match",
                "error": "Job description is required",
                "final_ats_score": 0
            }
        
        # Extract job keywords and categorize them
        job_keywords = get_keywords(job_description)
        job_categories = categorize_keywords(job_keywords)
        
        # Extract resume keywords
        resume_keywords = get_keywords(resume_text)
        
        # Get comprehensive resume info
        try:
            resume_info = get_comprehensive_resume_info(resume_text)
        except Exception:
            resume_info = {}
        
        # Perform enhanced keyword matching
        match_result = enhanced_keyword_match_score(job_keywords, resume_text, use_similarity=True)
        
        # Extract job requirements
        job_analysis = self._extract_job_requirements(job_description, job_keywords)
        
        # Calculate component scores
        keyword_match_score = match_result['score']
        experience_alignment_score = self._calculate_experience_alignment(resume_info, job_description)
        skills_relevance_score = self._calculate_skills_relevance(resume_info, job_keywords, job_categories)
        semantic_similarity_score = self._calculate_semantic_similarity(resume_text, job_description)
        
        # Calculate weighted final score
        weights = {
            'keyword_match': 0.40,
            'experience_alignment': 0.25,
            'skills_relevance': 0.25,
            'semantic_similarity': 0.10
        }
        
        final_score = (
            keyword_match_score * weights['keyword_match'] +
            experience_alignment_score * weights['experience_alignment'] +
            skills_relevance_score * weights['skills_relevance'] +
            semantic_similarity_score * weights['semantic_similarity']
        )
        
        # Identify matched, partial, and missing keywords
        matched_keywords = match_result['exact_matches']
        partial_matches = [kw for kw, matches in match_result['similar_matches'].items() if matches]
        missing_keywords = [kw for kw in job_keywords if kw not in matched_keywords and kw not in partial_matches]
        
        # Generate match analysis
        strengths, gaps = self._generate_match_analysis(
            matched_keywords,
            missing_keywords,
            resume_info,
            job_analysis
        )
        
        # Generate recommendations
        recommendations = self._generate_job_specific_recommendations(
            {
                'keyword_match': keyword_match_score,
                'experience_alignment': experience_alignment_score,
                'skills_relevance': skills_relevance_score,
                'semantic_similarity': semantic_similarity_score
            },
            missing_keywords,
            gaps
        )
        
        return {
            "mode": "resume_job_match",
            "final_ats_score": round(final_score, 1),
            "job_keywords": {
                "technical_skills": job_categories.get('technical_skills', [])[:15],
                "soft_skills": job_categories.get('soft_skills', [])[:10],
                "tools_technologies": job_categories.get('tools_technologies', [])[:15],
                "required_experience": job_analysis.get('experience_requirements', [])[:10]
            },
            "resume_keyword_match": {
                "matched_keywords": matched_keywords[:20],
                "partial_matches": partial_matches[:15],
                "missing_keywords": missing_keywords[:20]
            },
            "score_breakdown": {
                "keyword_match": round(keyword_match_score, 1),
                "experience_alignment": round(experience_alignment_score, 1),
                "skills_relevance": round(skills_relevance_score, 1),
                "semantic_similarity": round(semantic_similarity_score, 1)
            },
            "match_analysis": {
                "strengths": strengths,
                "gaps": gaps
            },
            "recommendations": recommendations
        }
    
    def _analyze_resume_builder(self, input_data: dict) -> dict:
        """
        Resume builder mode - not implemented.
        """
        return {
            "mode": "resume_builder",
            "status": "not_implemented",
            "message": "Resume builder functionality is not available yet."
        }
    
    # Helper methods for resume_only mode
    
    def _calculate_structure_formatting(self, resume_text: str, resume_info: dict) -> float:
        """Calculate resume structure and formatting score."""
        score = 50.0  # Base score
        
        # Check for proper sections
        sections_found = 0
        section_keywords = {
            'experience': ['experience', 'work experience', 'employment'],
            'education': ['education', 'academic'],
            'skills': ['skills', 'competencies'],
            'summary': ['summary', 'objective', 'profile']
        }
        
        resume_lower = resume_text.lower()
        for section_type, keywords in section_keywords.items():
            if any(kw in resume_lower for kw in keywords):
                sections_found += 1
                score += 10
        
        # Check for bullet points
        if any(char in resume_text for char in ['•', '-', '*', '·']):
            score += 10
        
        # Check for proper length
        word_count = len(resume_text.split())
        if 300 <= word_count <= 800:
            score += 10
        elif word_count < 200:
            score -= 20
        
        # Check for consistent formatting (dates, etc.)
        date_patterns = re.findall(r'\b\d{4}\b|\b\d{1,2}/\d{4}\b', resume_text)
        if len(date_patterns) >= 2:
            score += 10
        
        return min(max(score, 0), 100)
    
    def _calculate_section_completeness(self, resume_info: dict) -> float:
        """Calculate section completeness score."""
        required_sections = {
            'personal_info': 20,
            'work_experience': 25,
            'education': 20,
            'skills': 25,
            'professional_summary': 10
        }
        
        score = 0
        for section, weight in required_sections.items():
            if resume_info.get(section):
                if isinstance(resume_info[section], (list, dict)):
                    if len(resume_info[section]) > 0:
                        score += weight
                elif resume_info[section]:
                    score += weight
        
        return min(score, 100)
    
    def _calculate_keyword_strength(self, keywords: List[str], resume_text: str) -> float:
        """Calculate generic keyword strength."""
        if not keywords:
            return 20.0
        
        # Count unique keywords
        keyword_count = len(keywords)
        
        # Calculate keyword density
        total_words = len(resume_text.split())
        if total_words == 0:
            return 0.0
        
        density = (keyword_count / total_words) * 100
        
        # Optimal density is 5-15%
        if 5 <= density <= 15:
            score = 100.0
        elif density < 5:
            score = (density / 5) * 70
        else:
            score = max(30, 100 - (density - 15) * 5)
        
        return min(score, 100)
    
    def _calculate_skills_clarity(self, resume_info: dict, resume_text: str) -> float:
        """Calculate skills clarity and categorization score."""
        skills = resume_info.get('skills', [])
        
        if not skills:
            return 30.0
        
        score = 50.0
        
        # Reward having multiple skills
        if len(skills) >= 5:
            score += 20
        if len(skills) >= 10:
            score += 15
        if len(skills) >= 15:
            score += 15
        
        # Check for categorization (technical vs soft skills)
        categories = categorize_keywords(skills)
        if categories.get('technical_skills'):
            score += 10
        if categories.get('soft_skills'):
            score += 5
        
        return min(score, 100)
    
    def _calculate_experience_quality(self, resume_info: dict, resume_text: str) -> float:
        """Calculate experience quality score."""
        work_experience = resume_info.get('work_experience', [])
        
        if not work_experience:
            return 40.0
        
        score = 50.0
        
        # Reward multiple experiences
        score += min(len(work_experience) * 10, 30)
        
        # Check for action verbs
        action_verbs = ['led', 'managed', 'developed', 'created', 'implemented', 'designed',
                       'achieved', 'improved', 'increased', 'reduced', 'built', 'launched']
        resume_lower = resume_text.lower()
        action_verb_count = sum(1 for verb in action_verbs if verb in resume_lower)
        score += min(action_verb_count * 2, 20)
        
        # Check for metrics/numbers
        metrics = re.findall(r'\d+%|\$\d+|\d+\+', resume_text)
        if len(metrics) >= 3:
            score += 15
        elif len(metrics) >= 1:
            score += 10
        
        return min(score, 100)
    
    def _calculate_consistency(self, resume_text: str, resume_info: dict) -> float:
        """Calculate consistency score."""
        score = 70.0  # Base score
        
        # Check date consistency
        dates = re.findall(r'\b\d{4}\b', resume_text)
        if len(dates) >= 2:
            score += 15
        
        # Check for consistent formatting
        bullet_types = [char for char in ['•', '-', '*', '·'] if char in resume_text]
        if len(bullet_types) == 1:
            score += 15
        elif len(bullet_types) > 1:
            score -= 10
        
        return min(max(score, 0), 100)
    
    def _calculate_ats_readability(self, resume_text: str) -> float:
        """Calculate ATS readability and parsing compatibility."""
        score = 60.0
        
        # Check for problematic characters
        problematic_chars = ['@', '#', '$', '%', '^', '&', '*', '(', ')']
        char_count = sum(resume_text.count(char) for char in problematic_chars)
        if char_count < 10:
            score += 20
        elif char_count > 30:
            score -= 20
        
        # Check for standard sections
        standard_sections = ['experience', 'education', 'skills']
        resume_lower = resume_text.lower()
        sections_found = sum(1 for section in standard_sections if section in resume_lower)
        score += sections_found * 7
        
        return min(max(score, 0), 100)
    
    def _generate_strengths_weaknesses(self, scores: dict, resume_info: dict, resume_text: str) -> tuple:
        """Generate strengths and weaknesses lists."""
        strengths = []
        weaknesses = []
        
        for component, score in scores.items():
            component_name = component.replace('_', ' ').title()
            if score >= 80:
                strengths.append(f"Strong {component_name} ({score:.0f}/100)")
            elif score < 50:
                weaknesses.append(f"Weak {component_name} ({score:.0f}/100)")
        
        # Add specific strengths
        if resume_info.get('certifications') and len(resume_info['certifications']) > 0:
            strengths.append(f"Has {len(resume_info['certifications'])} certification(s)")
        
        if resume_info.get('projects') and len(resume_info['projects']) > 0:
            strengths.append(f"Includes {len(resume_info['projects'])} project(s)")
        
        # Add specific weaknesses
        if not resume_info.get('professional_summary'):
            weaknesses.append("Missing professional summary section")
        
        if not resume_info.get('skills') or len(resume_info.get('skills', [])) < 5:
            weaknesses.append("Insufficient skills listed")
        
        return strengths[:5], weaknesses[:5]
    
    def _generate_improvement_suggestions(self, scores: dict, detected_sections: dict) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []
        
        # Section-based suggestions
        if not detected_sections.get('summary'):
            suggestions.append("Add a professional summary at the top of your resume")
        
        if not detected_sections.get('skills'):
            suggestions.append("Create a dedicated skills section with relevant technical and soft skills")
        
        # Score-based suggestions
        if scores['structure_formatting'] < 70:
            suggestions.append("Improve resume formatting with clear section headers and bullet points")
        
        if scores['keyword_strength'] < 60:
            suggestions.append("Incorporate more industry-relevant keywords throughout your resume")
        
        if scores['experience_quality'] < 70:
            suggestions.append("Quantify achievements with metrics and use strong action verbs")
        
        if scores['ats_readability'] < 70:
            suggestions.append("Simplify formatting to improve ATS parsing compatibility")
        
        if scores['consistency'] < 70:
            suggestions.append("Ensure consistent date formats and bullet point styles")
        
        return suggestions[:7]
    
    # Helper methods for resume_job_match mode
    
    def _extract_job_requirements(self, job_description: str, job_keywords: List[str]) -> dict:
        """Extract job requirements from job description."""
        requirements = {
            'experience_requirements': [],
            'education_requirements': [],
            'required_skills': [],
            'preferred_skills': []
        }
        
        # Extract experience requirements
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)-(\d+)\s*years?\s*experience',
            r'minimum\s*(\d+)\s*years?'
        ]
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, job_description, re.IGNORECASE)
            if matches:
                requirements['experience_requirements'].extend([str(m) if isinstance(m, int) else ' '.join(m) for m in matches])
        
        # Extract education requirements
        edu_keywords = ['bachelor', 'master', 'phd', 'degree', 'diploma']
        job_lower = job_description.lower()
        for edu in edu_keywords:
            if edu in job_lower:
                requirements['education_requirements'].append(edu.title())
        
        # Categorize skills as required vs preferred
        if 'required' in job_lower or 'must have' in job_lower:
            requirements['required_skills'] = job_keywords[:10]
        if 'preferred' in job_lower or 'nice to have' in job_lower:
            requirements['preferred_skills'] = job_keywords[10:20]
        
        return requirements
    
    def _calculate_experience_alignment(self, resume_info: dict, job_description: str) -> float:
        """Calculate experience alignment score."""
        work_experience = resume_info.get('work_experience', [])
        
        if not work_experience:
            return 30.0
        
        score = 50.0
        
        # Count years of experience
        total_years = len(work_experience)
        
        # Extract required years from job description
        exp_match = re.search(r'(\d+)\+?\s*years?\s*(?:of\s*)?experience', job_description, re.IGNORECASE)
        if exp_match:
            required_years = int(exp_match.group(1))
            if total_years >= required_years:
                score += 40
            elif total_years >= required_years * 0.7:
                score += 25
            else:
                score += 10
        else:
            # No specific requirement, reward having experience
            score += min(total_years * 10, 40)
        
        return min(score, 100)
    
    def _calculate_skills_relevance(self, resume_info: dict, job_keywords: List[str], job_categories: dict) -> float:
        """Calculate skills relevance score."""
        resume_skills = resume_info.get('skills', [])
        
        if not resume_skills:
            return 25.0
        
        # Match resume skills against job keywords
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        job_keywords_lower = [kw.lower() for kw in job_keywords]
        
        matched_skills = [skill for skill in resume_skills_lower if skill in job_keywords_lower]
        
        if not job_keywords:
            return 50.0
        
        match_ratio = len(matched_skills) / len(job_keywords)
        score = match_ratio * 100
        
        # Bonus for having technical skills
        if job_categories.get('technical_skills'):
            tech_matches = sum(1 for skill in resume_skills_lower 
                             if any(tech.lower() in skill for tech in job_categories['technical_skills']))
            score += min(tech_matches * 5, 20)
        
        return min(score, 100)
    
    def _calculate_semantic_similarity(self, resume_text: str, job_description: str) -> float:
        """Calculate semantic similarity between resume and job description."""
        # Simple word overlap similarity
        resume_words = set(resume_text.lower().split())
        job_words = set(job_description.lower().split())
        
        if not job_words:
            return 0.0
        
        common_words = resume_words & job_words
        similarity = len(common_words) / len(job_words)
        
        return min(similarity * 100, 100)
    
    def _generate_match_analysis(self, matched_keywords: List[str], missing_keywords: List[str],
                                 resume_info: dict, job_analysis: dict) -> tuple:
        """Generate match analysis strengths and gaps."""
        strengths = []
        gaps = []
        
        # Analyze matched keywords
        if len(matched_keywords) >= 10:
            strengths.append(f"Strong keyword match with {len(matched_keywords)} matched terms")
        elif len(matched_keywords) >= 5:
            strengths.append(f"Good keyword match with {len(matched_keywords)} matched terms")
        
        # Analyze experience
        work_exp = resume_info.get('work_experience', [])
        if len(work_exp) >= 3:
            strengths.append(f"Solid work history with {len(work_exp)} positions")
        
        # Analyze skills
        skills = resume_info.get('skills', [])
        if len(skills) >= 10:
            strengths.append(f"Comprehensive skills section with {len(skills)} skills")
        
        # Identify gaps
        if len(missing_keywords) >= 10:
            gaps.append(f"Missing {len(missing_keywords)} key job requirements")
        
        if not resume_info.get('certifications') and 'certification' in ' '.join(missing_keywords).lower():
            gaps.append("No certifications listed while job may require them")
        
        if len(work_exp) < 2:
            gaps.append("Limited work experience history")
        
        if not resume_info.get('professional_summary'):
            gaps.append("Missing professional summary to highlight qualifications")
        
        return strengths[:5], gaps[:5]
    
    def _generate_job_specific_recommendations(self, scores: dict, missing_keywords: List[str], gaps: List[str]) -> List[str]:
        """Generate job-specific recommendations."""
        recommendations = []
        
        # Keyword-based recommendations
        if scores['keyword_match'] < 60 and missing_keywords:
            top_missing = missing_keywords[:5]
            recommendations.append(f"Add these critical keywords to your resume: {', '.join(top_missing)}")
        
        # Experience recommendations
        if scores['experience_alignment'] < 60:
            recommendations.append("Highlight relevant experience that aligns with job requirements")
        
        # Skills recommendations
        if scores['skills_relevance'] < 60:
            recommendations.append("Emphasize skills that directly match the job description")
        
        # Gap-based recommendations
        for gap in gaps[:3]:
            if "certification" in gap.lower():
                recommendations.append("Consider obtaining relevant certifications mentioned in the job posting")
            elif "experience" in gap.lower():
                recommendations.append("Expand work experience section with relevant projects or roles")
            elif "summary" in gap.lower():
                recommendations.append("Add a tailored professional summary highlighting your fit for this role")
        
        # General recommendations
        if scores['keyword_match'] >= 70 and scores['skills_relevance'] >= 70:
            recommendations.append("Strong match - consider customizing your summary to emphasize top qualifications")
        
        return recommendations[:7]


def process_ats_request(input_data: dict) -> dict:
    """
    Convenience function to process ATS requests.
    
    Args:
        input_data: Dictionary with mode, resume_text, and optional job_description
        
    Returns:
        Dictionary with ATS analysis results (JSON-serializable)
    """
    engine = ATSEngine()
    return engine.process_request(input_data)
