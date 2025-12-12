"""
ATS Scoring System for Resume Match AI
Calculates comprehensive ATS (Applicant Tracking System) compatibility scores
based on keyword matching, personal info completeness, and other factors.
"""

import re
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import spacy
from difflib import SequenceMatcher
from utils.keywords_extraction import get_keywords, enhanced_keyword_match_score

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    spacy.cli.download('en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')

class ATSScorer:
    """
    Comprehensive ATS scoring system with weighted criteria.
    """

    # Weight configuration for different scoring components
    WEIGHTS = {
        'keyword_match': 0.40,      # 40% - Most important
        'keyword_density': 0.15,    # 15% - Keyword distribution
        'personal_info': 0.15,      # 15% - Complete contact info
        'skills_alignment': 0.10,   # 10% - Skills section quality
        'experience_match': 0.10,   # 10% - Experience relevance
        'education_match': 0.05,    # 5% - Education alignment
        'formatting': 0.05          # 5% - Resume formatting quality
    }

    # Keywords that indicate sections in resumes
    SECTION_KEYWORDS = {
        'experience': ['experience', 'work experience', 'professional experience', 'employment',
                      'work history', 'career history', 'professional background'],
        'education': ['education', 'academic background', 'qualifications', 'degrees',
                     'certifications', 'academic credentials'],
        'skills': ['skills', 'technical skills', 'core competencies', 'expertise',
                  'proficiencies', 'abilities', 'competencies'],
        'summary': ['summary', 'professional summary', 'objective', 'profile',
                   'career objective', 'personal statement']
    }

    def __init__(self):
        self.stemmer = self._load_stemmer()

    def _load_stemmer(self):
        """Load NLTK stemmer with fallback."""
        try:
            from nltk.stem import PorterStemmer
            return PorterStemmer()
        except ImportError:
            # Fallback stemmer if NLTK not available
            return lambda x: x.lower()

    def calculate_overall_score(self, resume_text: str, job_keywords: List[str],
                              personal_info: Dict, job_info: Dict) -> Dict:
        """
        Calculate comprehensive ATS score with breakdown using enhanced extraction.

        Args:
            resume_text: Full resume text
            job_keywords: Keywords extracted from job description
            personal_info: Personal information dict (can be comprehensive or basic)
            job_info: Job information dict (can be comprehensive or basic)

        Returns:
            Dictionary with overall score and detailed breakdown
        """
        scores = {}

        # Calculate individual component scores
        scores['keyword_match'] = self._calculate_keyword_match_score(resume_text, job_keywords)
        scores['keyword_density'] = self._calculate_keyword_density_score(resume_text, job_keywords)
        scores['personal_info'] = self._calculate_personal_info_score(personal_info)
        scores['skills_alignment'] = self._calculate_skills_alignment_score(resume_text, job_keywords)
        scores['experience_match'] = self._calculate_experience_match_score(resume_text, job_keywords)
        scores['education_match'] = self._calculate_education_match_score(resume_text, job_keywords)
        scores['formatting'] = self._calculate_formatting_score(resume_text)

        # Calculate weighted overall score
        overall_score = sum(scores[component] * self.WEIGHTS[component] for component in scores)

        # Generate recommendations
        recommendations = self._generate_recommendations(scores, resume_text, job_keywords)

        # Get enhanced keyword analysis
        keyword_analysis = self._get_enhanced_keyword_analysis(resume_text, job_keywords)

        # Get comprehensive job and resume analysis
        job_analysis = self._analyze_job_requirements(job_info)
        resume_analysis = self._analyze_resume_content(personal_info, resume_text)

        return {
            'overall_score': round(overall_score, 1),
            'component_scores': {k: round(v, 1) for k, v in scores.items()},
            'recommendations': recommendations,
            'grade': self._get_grade_letter(overall_score),
            'ats_compatibility': self._get_compatibility_level(overall_score),
            'keyword_analysis': keyword_analysis,
            'job_analysis': job_analysis,
            'resume_analysis': resume_analysis
        }

    def _calculate_keyword_match_score(self, resume_text: str, job_keywords: List[str]) -> float:
        """Calculate enhanced keyword matching score (0-100) with similarity matching."""
        if not job_keywords or not resume_text:
            return 0.0

        # Use enhanced keyword matching with similarity
        match_result = enhanced_keyword_match_score(job_keywords, resume_text, use_similarity=True)
        match_percentage = match_result['score']

        # Apply diminishing returns for very high matches (avoid keyword stuffing detection)
        if match_percentage > 80:
            match_percentage = 80 + (match_percentage - 80) * 0.5

        return min(match_percentage, 100.0)

    def _calculate_keyword_density_score(self, resume_text: str, job_keywords: List[str]) -> float:
        """Calculate keyword density score - rewards balanced distribution."""
        if not job_keywords or not resume_text:
            return 0.0

        # Count total words in resume
        total_words = len(resume_text.split())
        if total_words == 0:
            return 0.0

        # Count keyword occurrences
        keyword_count = 0
        resume_lower = resume_text.lower()

        for keyword in job_keywords:
            keyword_count += resume_lower.count(keyword.lower())

        # Calculate density (keywords per 100 words)
        density = (keyword_count / total_words) * 100

        # Optimal density is 3-8 keywords per 100 words
        if 3 <= density <= 8:
            score = 100.0
        elif density < 3:
            score = (density / 3) * 100
        else:
            # Penalize keyword stuffing
            score = max(0, 100 - (density - 8) * 10)

        return score

    def _calculate_personal_info_score(self, personal_info: Dict) -> float:
        """Calculate personal information completeness score (0-100)."""
        required_fields = ['name', 'email', 'phone_number']
        optional_fields = ['province', 'major_city']

        score = 0
        max_score = 100

        # Required fields (60% of score)
        required_score = 0
        for field in required_fields:
            if personal_info.get(field):
                required_score += 20  # 20 points each for 3 fields = 60 points

        # Optional fields (40% of score)
        optional_score = 0
        for field in optional_fields:
            if personal_info.get(field):
                optional_score += 20  # 20 points each for 2 fields = 40 points

        total_score = required_score + optional_score

        # Bonus for having all information (10 points)
        if required_score == 60 and optional_score == 40:
            total_score += 10

        return min(total_score, 100.0)

    def _calculate_skills_alignment_score(self, resume_text: str, job_keywords: List[str]) -> float:
        """Calculate skills section alignment score."""
        skills_section = self._extract_section_text(resume_text, 'skills')
        if not skills_section:
            return 30.0  # Penalty for no skills section

        # Count job keywords in skills section
        skills_lower = skills_section.lower()
        matched_skills = sum(1 for keyword in job_keywords if keyword.lower() in skills_lower)

        # Calculate alignment score
        if matched_skills == 0:
            return 20.0
        elif matched_skills <= 3:
            return 60.0
        elif matched_skills <= 6:
            return 80.0
        else:
            return 95.0

    def _calculate_experience_match_score(self, resume_text: str, job_keywords: List[str]) -> float:
        """Calculate experience section relevance score."""
        experience_section = self._extract_section_text(resume_text, 'experience')
        if not experience_section:
            return 40.0  # Moderate penalty for no experience section

        # Look for job-related keywords in experience section
        exp_lower = experience_section.lower()
        relevant_keywords = [k for k in job_keywords if any(term in k.lower()
                            for term in ['experience', 'year', 'skill', 'project', 'team'])]

        matched_exp = sum(1 for keyword in relevant_keywords if keyword.lower() in exp_lower)

        if len(relevant_keywords) == 0:
            return 70.0  # Neutral score if no relevant keywords to match

        match_ratio = matched_exp / len(relevant_keywords)
        return min(match_ratio * 100, 100.0)

    def _calculate_education_match_score(self, resume_text: str, job_keywords: List[str]) -> float:
        """Calculate education section alignment score."""
        education_section = self._extract_section_text(resume_text, 'education')
        if not education_section:
            return 50.0  # Moderate penalty for no education section

        # Look for education-related keywords
        edu_keywords = [k for k in job_keywords if any(term in k.lower()
                       for term in ['degree', 'education', 'university', 'college', 'graduate'])]

        if not edu_keywords:
            return 75.0  # Good score if education not required

        edu_lower = education_section.lower()
        matched_edu = sum(1 for keyword in edu_keywords if keyword.lower() in edu_lower)

        match_ratio = matched_edu / len(edu_keywords)
        return min(match_ratio * 100, 100.0)

    def _calculate_formatting_score(self, resume_text: str) -> float:
        """Calculate resume formatting quality score."""
        score = 100.0

        # Check for proper structure (sections)
        sections_found = 0
        for section_type, keywords in self.SECTION_KEYWORDS.items():
            if any(keyword in resume_text.lower() for keyword in keywords):
                sections_found += 1

        # Bonus for having multiple sections
        if sections_found >= 4:
            score += 10
        elif sections_found >= 2:
            score += 5

        # Check for bullet points (good formatting indicator)
        bullet_indicators = ['•', '-', '*', '·']
        has_bullets = any(indicator in resume_text for indicator in bullet_indicators)
        if has_bullets:
            score += 5

        # Check length (too short or too long is bad)
        word_count = len(resume_text.split())
        if word_count < 100:
            score -= 20  # Too short
        elif word_count > 800:
            score -= 10  # Too long
        elif 300 <= word_count <= 600:
            score += 5  # Optimal length

        return max(0, min(score, 100.0))

    def _extract_section_text(self, resume_text: str, section_type: str) -> str:
        """Extract text from a specific section of the resume."""
        lines = resume_text.split('\n')
        section_keywords = self.SECTION_KEYWORDS.get(section_type, [])

        section_text = []
        in_section = False

        for line in lines:
            line_lower = line.lower().strip()

            # Check if this line starts a section
            if any(keyword in line_lower for keyword in section_keywords):
                in_section = True
                continue
            elif in_section and line.strip():
                # Check if we've reached the next section
                all_section_keywords = []
                for keywords in self.SECTION_KEYWORDS.values():
                    all_section_keywords.extend(keywords)

                if any(keyword in line_lower for keyword in all_section_keywords):
                    break

                section_text.append(line)

        return ' '.join(section_text)

    def _get_enhanced_keyword_analysis(self, resume_text: str, job_keywords: List[str]) -> Dict:
        """Get detailed keyword analysis with categorization."""
        try:
            match_result = enhanced_keyword_match_score(job_keywords, resume_text, use_similarity=True)
            return match_result
        except Exception as e:
            print(f"Error in enhanced keyword analysis: {e}")
            return {
                'score': 0.0,
                'exact_matches': [],
                'similar_matches': {},
                'categorized_matches': {},
                'keyword_analysis': {}
            }

    def _analyze_job_requirements(self, job_info: Dict) -> Dict:
        """Analyze job requirements comprehensively."""
        analysis = {
            'has_salary_info': bool(job_info.get('salary_info')),
            'experience_level': job_info.get('experience_level', 'Not specified'),
            'work_type': job_info.get('work_type', 'Not specified'),
            'employment_type': job_info.get('employment_type', 'Not specified'),
            'education_requirements': job_info.get('education_requirements', []),
            'benefits_offered': job_info.get('benefits', []),
            'key_skills_required': job_info.get('key_skills', []),
            'company_info': {
                'name': job_info.get('company_name'),
                'website': job_info.get('website'),
                'industry': job_info.get('industry')
            }
        }
        return analysis

    def _analyze_resume_content(self, personal_info: Dict, resume_text: str) -> Dict:
        """Analyze resume content comprehensively."""
        try:
            from utils.resume_keywords import get_comprehensive_resume_info
            comprehensive_info = get_comprehensive_resume_info(resume_text)

            analysis = {
                'contact_completeness': self._calculate_contact_completeness(personal_info),
                'has_summary': bool(comprehensive_info.get('professional_summary')),
                'experience_entries': len(comprehensive_info.get('work_experience', [])),
                'education_entries': len(comprehensive_info.get('education', [])),
                'certifications_count': len(comprehensive_info.get('certifications', [])),
                'projects_count': len(comprehensive_info.get('projects', [])),
                'skills_count': len(comprehensive_info.get('skills', [])),
                'languages_known': comprehensive_info.get('languages', []),
                'achievements_count': len(comprehensive_info.get('achievements', [])),
                'websites_count': len(comprehensive_info.get('websites', [])),
                'sections_found': self._analyze_resume_sections(comprehensive_info)
            }
            return analysis
        except Exception as e:
            print(f"Error in resume content analysis: {e}")
            return {
                'contact_completeness': 0,
                'has_summary': False,
                'experience_entries': 0,
                'education_entries': 0,
                'sections_found': []
            }

    def _calculate_contact_completeness(self, personal_info: Dict) -> float:
        """Calculate how complete the contact information is."""
        fields = ['name', 'email', 'phone_number']
        if isinstance(personal_info, dict) and 'name' in personal_info:
            # It's the basic format
            completed = sum(1 for field in fields if personal_info.get(field))
        else:
            # It might be comprehensive format
            completed = 0
            if personal_info.get('name') or personal_info.get('personal_info', {}).get('name'):
                completed += 1
            if personal_info.get('email') or personal_info.get('personal_info', {}).get('email'):
                completed += 1
            if personal_info.get('phone_number') or personal_info.get('personal_info', {}).get('phone_number'):
                completed += 1

        return (completed / 3) * 100

    def _analyze_resume_sections(self, comprehensive_info: Dict) -> list[str]:
        """Analyze which sections are present in the resume."""
        sections = []
        if comprehensive_info.get('professional_summary'):
            sections.append('Professional Summary')
        if comprehensive_info.get('work_experience'):
            sections.append('Work Experience')
        if comprehensive_info.get('education'):
            sections.append('Education')
        if comprehensive_info.get('certifications'):
            sections.append('Certifications')
        if comprehensive_info.get('projects'):
            sections.append('Projects')
        if comprehensive_info.get('skills'):
            sections.append('Skills')
        if comprehensive_info.get('achievements'):
            sections.append('Achievements')
        if comprehensive_info.get('websites'):
            sections.append('Websites')
        return sections

    def _generate_recommendations(self, scores: Dict, resume_text: str, job_keywords: List[str]) -> List[str]:
        """Generate detailed, personalized recommendations for improving ATS score."""
        recommendations = []
        overall_score = sum(scores[k] * self.WEIGHTS[k] for k in scores)

        # Critical issues (high priority)
        if scores['personal_info'] < 60:
            recommendations.append("🚨 CRITICAL: Add complete contact information (name, email, phone) at the top of your resume")

        if scores['keyword_match'] < 40:
            missing_keywords = [k for k in job_keywords[:8] if k.lower() not in resume_text.lower()]
            if missing_keywords:
                recommendations.append(f"🚨 CRITICAL: Incorporate these key skills naturally: {', '.join(missing_keywords[:4])}")

        # High priority recommendations
        if scores['keyword_match'] < 60:
            missing_keywords = [k for k in job_keywords if k.lower() not in resume_text.lower()][:6]
            if missing_keywords:
                recommendations.append(f"📈 HIGH: Add these missing keywords: {', '.join(missing_keywords[:3])}")

        if scores['keyword_density'] < 40:
            recommendations.append("📈 HIGH: Increase relevant keyword usage - aim for 3-8 job-related terms per 100 words")

        if scores['keyword_density'] > 95:
            recommendations.append("📈 HIGH: Reduce keyword repetition - ATS may flag over-optimization")

        # Medium priority recommendations
        if scores['skills_alignment'] < 60:
            recommendations.append("🔧 MEDIUM: Create or enhance skills section with job-specific technologies and tools")

        if scores['experience_match'] < 60:
            recommendations.append("🔧 MEDIUM: Quantify achievements and use action verbs in experience section")

        if scores['personal_info'] < 80 and scores['personal_info'] >= 60:
            recommendations.append("🔧 MEDIUM: Add location information to improve geographical matching")

        # Low priority recommendations
        if scores['formatting'] < 70:
            recommendations.append("💡 LOW: Use standard section headers (Experience, Skills, Education) and bullet points")

        if scores['education_match'] < 70:
            recommendations.append("💡 LOW: Ensure education section includes relevant degrees and certifications")

        # Overall score-based recommendations
        if overall_score < 40:
            recommendations.append("🚨 OVERALL: Major resume revision needed - consider professional resume writing services")
        elif overall_score < 60:
            recommendations.append("📊 OVERALL: Significant improvements needed - focus on keywords and personal info")
        elif overall_score < 75:
            recommendations.append("📊 OVERALL: Good foundation - focus on fine-tuning keyword usage and formatting")
        elif overall_score < 85:
            recommendations.append("✨ OVERALL: Very good - minor optimizations can achieve excellence")
        elif overall_score >= 85:
            recommendations.append("🎉 OVERALL: Excellent ATS optimization! Your resume should perform well")

        # Sort recommendations by priority (critical first, then high, medium, low, overall)
        priority_order = {'🚨 CRITICAL': 0, '🚨 OVERALL': 1, '📈 HIGH': 2, '🔧 MEDIUM': 3, '💡 LOW': 4, '📊 OVERALL': 5, '✨ OVERALL': 6, '🎉 OVERALL': 7}

        recommendations.sort(key=lambda x: priority_order.get(x.split(':')[0], 99))

        return recommendations[:7]  # Return top 7 most relevant recommendations

    def _get_grade_letter(self, score: float) -> str:
        """Convert numerical score to letter grade."""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

    def _get_compatibility_level(self, score: float) -> str:
        """Get detailed human-readable compatibility description with pass rates."""
        if score >= 90:
            return "Exceptional - 95%+ chance of passing ATS filters"
        elif score >= 85:
            return "Excellent - 85%+ chance of passing most ATS systems"
        elif score >= 75:
            return "Very Good - 75%+ chance, strong candidate"
        elif score >= 65:
            return "Good - 65%+ chance, likely to pass standard filters"
        elif score >= 55:
            return "Fair - 55%+ chance, may pass some systems"
        elif score >= 45:
            return "Below Average - 45%+ chance, needs improvement"
        elif score >= 35:
            return "Poor - 35%+ chance, significant work needed"
        else:
            return "Critical - <35% chance, major revisions required"

# Convenience function for easy scoring
def calculate_ats_score(resume_text: str, job_keywords: List[str],
                       personal_info: Dict, job_info: Dict) -> Dict:
    """
    Calculate ATS score using the comprehensive scorer.

    Args:
        resume_text: Full resume text
        job_keywords: Keywords from job description
        personal_info: Personal information dictionary
        job_info: Job information dictionary

    Returns:
        Dictionary with ATS score and breakdown
    """
    scorer = ATSScorer()
    return scorer.calculate_overall_score(resume_text, job_keywords, personal_info, job_info)