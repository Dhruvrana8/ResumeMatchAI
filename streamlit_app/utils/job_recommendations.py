"""
Job Recommendations Module

This module provides job position recommendations based on user resume analysis.
It uses a curated dataset of job positions and a matching algorithm to suggest
suitable positions based on skills, experience, and education.
"""

from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

# Curated job positions dataset
JOB_POSITIONS = [
    {
        "title": "Software Engineer",
        "industry": "Technology",
        "experience_level": "entry",
        "required_skills": ["python", "java", "javascript", "git", "sql", "api", "rest", "debugging", "testing", "agile"],
        "preferred_skills": ["react", "node.js", "docker", "aws", "mongodb"],
        "education": ["bachelor"],
        "salary_range": "$70,000 - $100,000",
        "description": "Develop and maintain software applications, write clean code, and collaborate with cross-functional teams."
    },
    {
        "title": "Senior Software Engineer",
        "industry": "Technology",
        "experience_level": "senior",
        "required_skills": ["python", "java", "javascript", "architecture", "system design", "leadership", "mentoring", "ci/cd", "microservices", "cloud"],
        "preferred_skills": ["kubernetes", "aws", "azure", "terraform", "graphql"],
        "education": ["bachelor", "master"],
        "salary_range": "$120,000 - $180,000",
        "description": "Lead technical projects, mentor junior developers, design scalable systems, and drive technical excellence."
    },
    {
        "title": "Data Scientist",
        "industry": "Technology",
        "experience_level": "mid",
        "required_skills": ["python", "machine learning", "statistics", "data analysis", "sql", "pandas", "numpy", "scikit-learn", "visualization", "jupyter"],
        "preferred_skills": ["tensorflow", "pytorch", "deep learning", "nlp", "computer vision"],
        "education": ["bachelor", "master", "phd"],
        "salary_range": "$90,000 - $140,000",
        "description": "Analyze complex datasets, build predictive models, and provide data-driven insights to drive business decisions."
    },
    {
        "title": "Machine Learning Engineer",
        "industry": "Technology",
        "experience_level": "mid",
        "required_skills": ["python", "machine learning", "deep learning", "tensorflow", "pytorch", "model deployment", "mlops", "docker", "kubernetes", "cloud"],
        "preferred_skills": ["aws sagemaker", "mlflow", "kubeflow", "spark", "distributed computing"],
        "education": ["bachelor", "master"],
        "salary_range": "$100,000 - $160,000",
        "description": "Design and deploy machine learning models at scale, optimize model performance, and build ML infrastructure."
    },
    {
        "title": "Frontend Developer",
        "industry": "Technology",
        "experience_level": "entry",
        "required_skills": ["html", "css", "javascript", "react", "responsive design", "git", "rest api", "ui/ux", "debugging", "testing"],
        "preferred_skills": ["typescript", "vue.js", "angular", "webpack", "sass"],
        "education": ["bachelor", "bootcamp"],
        "salary_range": "$65,000 - $95,000",
        "description": "Build responsive and interactive user interfaces, collaborate with designers, and ensure great user experiences."
    },
    {
        "title": "Backend Developer",
        "industry": "Technology",
        "experience_level": "mid",
        "required_skills": ["python", "java", "node.js", "sql", "nosql", "api design", "rest", "microservices", "docker", "testing"],
        "preferred_skills": ["graphql", "redis", "rabbitmq", "kafka", "aws"],
        "education": ["bachelor"],
        "salary_range": "$85,000 - $130,000",
        "description": "Design and implement server-side logic, manage databases, and build scalable backend systems."
    },
    {
        "title": "Full Stack Developer",
        "industry": "Technology",
        "experience_level": "mid",
        "required_skills": ["javascript", "react", "node.js", "python", "sql", "rest api", "git", "docker", "agile", "testing"],
        "preferred_skills": ["typescript", "mongodb", "aws", "ci/cd", "graphql"],
        "education": ["bachelor"],
        "salary_range": "$90,000 - $135,000",
        "description": "Work on both frontend and backend development, build end-to-end features, and maintain full application stack."
    },
    {
        "title": "DevOps Engineer",
        "industry": "Technology",
        "experience_level": "mid",
        "required_skills": ["linux", "docker", "kubernetes", "ci/cd", "aws", "terraform", "ansible", "monitoring", "scripting", "git"],
        "preferred_skills": ["jenkins", "prometheus", "grafana", "helm", "python"],
        "education": ["bachelor"],
        "salary_range": "$95,000 - $145,000",
        "description": "Automate infrastructure, manage deployments, ensure system reliability, and optimize development workflows."
    },
    {
        "title": "Data Analyst",
        "industry": "Technology",
        "experience_level": "entry",
        "required_skills": ["sql", "excel", "data visualization", "python", "statistics", "tableau", "power bi", "data cleaning", "reporting", "analytics"],
        "preferred_skills": ["r", "pandas", "numpy", "business intelligence", "etl"],
        "education": ["bachelor"],
        "salary_range": "$60,000 - $85,000",
        "description": "Analyze business data, create reports and dashboards, and provide actionable insights to stakeholders."
    },
    {
        "title": "Product Manager",
        "industry": "Technology",
        "experience_level": "mid",
        "required_skills": ["product strategy", "roadmap", "stakeholder management", "agile", "user research", "analytics", "communication", "prioritization", "jira", "data-driven"],
        "preferred_skills": ["sql", "a/b testing", "ux design", "market research", "technical background"],
        "education": ["bachelor", "master", "mba"],
        "salary_range": "$100,000 - $150,000",
        "description": "Define product vision and strategy, prioritize features, work with engineering teams, and drive product success."
    },
    {
        "title": "UX/UI Designer",
        "industry": "Technology",
        "experience_level": "mid",
        "required_skills": ["figma", "sketch", "adobe xd", "user research", "wireframing", "prototyping", "user testing", "design systems", "responsive design", "accessibility"],
        "preferred_skills": ["html", "css", "javascript", "animation", "illustration"],
        "education": ["bachelor", "bootcamp"],
        "salary_range": "$75,000 - $120,000",
        "description": "Design intuitive user interfaces, conduct user research, create prototypes, and ensure excellent user experiences."
    },
    {
        "title": "Cloud Architect",
        "industry": "Technology",
        "experience_level": "senior",
        "required_skills": ["aws", "azure", "cloud architecture", "security", "networking", "terraform", "kubernetes", "microservices", "scalability", "cost optimization"],
        "preferred_skills": ["gcp", "serverless", "multi-cloud", "compliance", "disaster recovery"],
        "education": ["bachelor", "master"],
        "salary_range": "$130,000 - $190,000",
        "description": "Design cloud infrastructure, ensure security and compliance, optimize costs, and lead cloud migration projects."
    },
    {
        "title": "Security Engineer",
        "industry": "Technology",
        "experience_level": "mid",
        "required_skills": ["cybersecurity", "penetration testing", "vulnerability assessment", "networking", "encryption", "security protocols", "incident response", "compliance", "linux", "scripting"],
        "preferred_skills": ["python", "cloud security", "siem", "threat intelligence", "certifications"],
        "education": ["bachelor"],
        "salary_range": "$90,000 - $140,000",
        "description": "Protect systems and data, conduct security assessments, respond to incidents, and ensure compliance with security standards."
    },
    {
        "title": "Mobile Developer",
        "industry": "Technology",
        "experience_level": "mid",
        "required_skills": ["ios", "android", "swift", "kotlin", "mobile ui", "rest api", "git", "testing", "app store", "debugging"],
        "preferred_skills": ["react native", "flutter", "firebase", "push notifications", "ci/cd"],
        "education": ["bachelor"],
        "salary_range": "$85,000 - $130,000",
        "description": "Develop mobile applications for iOS and Android, optimize performance, and deliver great mobile experiences."
    },
    {
        "title": "QA Engineer",
        "industry": "Technology",
        "experience_level": "entry",
        "required_skills": ["testing", "test automation", "selenium", "bug tracking", "test cases", "regression testing", "api testing", "agile", "jira", "quality assurance"],
        "preferred_skills": ["python", "java", "ci/cd", "performance testing", "security testing"],
        "education": ["bachelor"],
        "salary_range": "$60,000 - $90,000",
        "description": "Ensure software quality through testing, create test plans, automate tests, and identify and report bugs."
    },
    {
        "title": "Business Analyst",
        "industry": "Business",
        "experience_level": "mid",
        "required_skills": ["requirements gathering", "business process", "stakeholder management", "documentation", "sql", "data analysis", "communication", "agile", "jira", "problem solving"],
        "preferred_skills": ["python", "tableau", "process improvement", "project management", "domain expertise"],
        "education": ["bachelor", "master", "mba"],
        "salary_range": "$75,000 - $110,000",
        "description": "Bridge business and technology, gather requirements, analyze processes, and drive business improvements."
    },
    {
        "title": "AI Research Scientist",
        "industry": "Technology",
        "experience_level": "senior",
        "required_skills": ["machine learning", "deep learning", "research", "python", "tensorflow", "pytorch", "nlp", "computer vision", "mathematics", "publications"],
        "preferred_skills": ["phd", "reinforcement learning", "transformers", "gans", "research papers"],
        "education": ["master", "phd"],
        "salary_range": "$120,000 - $200,000",
        "description": "Conduct cutting-edge AI research, publish papers, develop novel algorithms, and push the boundaries of AI."
    },
    {
        "title": "Site Reliability Engineer",
        "industry": "Technology",
        "experience_level": "mid",
        "required_skills": ["linux", "kubernetes", "monitoring", "incident management", "automation", "scripting", "cloud", "networking", "troubleshooting", "on-call"],
        "preferred_skills": ["python", "go", "prometheus", "grafana", "terraform"],
        "education": ["bachelor"],
        "salary_range": "$100,000 - $150,000",
        "description": "Ensure system reliability and uptime, automate operations, respond to incidents, and improve infrastructure."
    },
    {
        "title": "Technical Writer",
        "industry": "Technology",
        "experience_level": "entry",
        "required_skills": ["technical writing", "documentation", "api documentation", "communication", "markdown", "git", "editing", "research", "user guides", "attention to detail"],
        "preferred_skills": ["programming knowledge", "cms", "video tutorials", "localization", "seo"],
        "education": ["bachelor"],
        "salary_range": "$55,000 - $85,000",
        "description": "Create clear technical documentation, write user guides, document APIs, and help users understand products."
    },
    {
        "title": "Blockchain Developer",
        "industry": "Technology",
        "experience_level": "mid",
        "required_skills": ["blockchain", "smart contracts", "solidity", "ethereum", "web3", "cryptography", "distributed systems", "javascript", "testing", "security"],
        "preferred_skills": ["rust", "hyperledger", "defi", "nfts", "layer 2"],
        "education": ["bachelor"],
        "salary_range": "$95,000 - $160,000",
        "description": "Develop blockchain applications, write smart contracts, ensure security, and build decentralized solutions."
    }
]


def normalize_skill(skill: str) -> str:
    """Normalize skill name for comparison."""
    return skill.lower().strip().replace("-", " ").replace("_", " ")


def calculate_skill_match(resume_skills: List[str], required_skills: List[str], preferred_skills: List[str]) -> Tuple[float, List[str], List[str], List[str]]:
    """
    Calculate skill match score between resume and job requirements.
    
    Args:
        resume_skills: List of skills from resume
        required_skills: List of required skills for the job
        preferred_skills: List of preferred skills for the job
    
    Returns:
        Tuple of (match_score, matched_required, matched_preferred, missing_required)
    """
    # Normalize all skills
    normalized_resume = set(normalize_skill(s) for s in resume_skills)
    normalized_required = [normalize_skill(s) for s in required_skills]
    normalized_preferred = [normalize_skill(s) for s in preferred_skills]
    
    # Find matches
    matched_required = []
    missing_required = []
    
    for i, req_skill in enumerate(normalized_required):
        # Check for exact match or partial match (skill contains keyword or vice versa)
        is_match = False
        for resume_skill in normalized_resume:
            if req_skill in resume_skill or resume_skill in req_skill:
                is_match = True
                break
        
        if is_match:
            matched_required.append(required_skills[i])
        else:
            missing_required.append(required_skills[i])
    
    matched_preferred = []
    for i, pref_skill in enumerate(normalized_preferred):
        for resume_skill in normalized_resume:
            if pref_skill in resume_skill or resume_skill in pref_skill:
                matched_preferred.append(preferred_skills[i])
                break
    
    # Calculate score
    required_score = (len(matched_required) / len(required_skills) * 100) if required_skills else 0
    preferred_score = (len(matched_preferred) / len(preferred_skills) * 20) if preferred_skills else 0
    
    # Total score: 80% weight on required, 20% weight on preferred
    total_score = min(required_score * 0.8 + preferred_score, 100)
    
    return total_score, matched_required, matched_preferred, missing_required


def match_experience_level(resume_info: Dict, job_level: str) -> Tuple[float, str]:
    """
    Match experience level between resume and job.
    
    Args:
        resume_info: Comprehensive resume information
        job_level: Required experience level (entry, mid, senior)
    
    Returns:
        Tuple of (match_score, explanation)
    """
    work_experience = resume_info.get('work_experience', [])
    years_of_experience = len(work_experience)
    
    # Define experience level ranges
    level_ranges = {
        'entry': (0, 2),
        'mid': (2, 7),
        'senior': (7, 100)
    }
    
    min_years, max_years = level_ranges.get(job_level, (0, 100))
    
    if min_years <= years_of_experience <= max_years:
        score = 100
        explanation = f"Your experience level ({years_of_experience} positions) matches the {job_level}-level requirement."
    elif years_of_experience > max_years:
        score = 80
        explanation = f"You're overqualified ({years_of_experience} positions) for this {job_level}-level role, but could be a great fit."
    else:
        score = 60
        explanation = f"You have {years_of_experience} position(s), slightly below the typical {job_level}-level requirement."
    
    return score, explanation


def match_education(resume_info: Dict, required_education: List[str]) -> Tuple[float, str]:
    """
    Match education requirements.
    
    Args:
        resume_info: Comprehensive resume information
        required_education: List of acceptable education levels
    
    Returns:
        Tuple of (match_score, explanation)
    """
    education = resume_info.get('education', [])
    
    if not required_education:
        return 100, "No specific education requirement."
    
    if not education:
        return 50, "Education information not found in resume."
    
    # Simple check - if any education entry exists, consider it a match
    # This is simplified; could be enhanced to check degree levels
    education_levels = ['bachelor', 'master', 'phd', 'associate', 'bootcamp']
    
    for edu in education:
        degree = edu.get('degree', '').lower()
        for level in education_levels:
            if level in degree and level in [e.lower() for e in required_education]:
                return 100, f"Your {edu.get('degree', 'degree')} meets the education requirement."
    
    return 70, "Education level may differ from typical requirement, but experience can compensate."


def get_job_recommendations(resume_info: Dict, top_n: int = 10) -> List[Dict]:
    """
    Get job recommendations based on resume analysis.
    
    Args:
        resume_info: Comprehensive resume information from get_comprehensive_resume_info
        top_n: Number of top recommendations to return
    
    Returns:
        List of recommended jobs with match scores and details
    """
    if not resume_info:
        logger.warning("No resume information provided for job recommendations")
        return []
    
    # Extract resume skills
    resume_skills = resume_info.get('skills', [])
    
    if not resume_skills:
        logger.warning("No skills found in resume for matching")
        # Still return recommendations but with lower scores
        resume_skills = []
    
    recommendations = []
    
    for job in JOB_POSITIONS:
        # Calculate skill match
        skill_score, matched_req, matched_pref, missing_req = calculate_skill_match(
            resume_skills,
            job['required_skills'],
            job['preferred_skills']
        )
        
        # Calculate experience match
        exp_score, exp_explanation = match_experience_level(
            resume_info,
            job['experience_level']
        )
        
        # Calculate education match
        edu_score, edu_explanation = match_education(
            resume_info,
            job['education']
        )
        
        # Calculate overall match score
        # Weights: Skills 60%, Experience 25%, Education 15%
        overall_score = (skill_score * 0.6) + (exp_score * 0.25) + (edu_score * 0.15)
        
        # Create recommendation
        recommendation = {
            'job': job,
            'match_score': round(overall_score, 1),
            'skill_match_score': round(skill_score, 1),
            'experience_match_score': round(exp_score, 1),
            'education_match_score': round(edu_score, 1),
            'matched_required_skills': matched_req,
            'matched_preferred_skills': matched_pref,
            'missing_required_skills': missing_req,
            'experience_explanation': exp_explanation,
            'education_explanation': edu_explanation,
            'insights': _generate_insights(job, matched_req, missing_req, exp_score, edu_score)
        }
        
        recommendations.append(recommendation)
    
    # Sort by match score
    recommendations.sort(key=lambda x: x['match_score'], reverse=True)
    
    return recommendations[:top_n]


def _generate_insights(job: Dict, matched_skills: List[str], missing_skills: List[str], exp_score: float, edu_score: float) -> List[str]:
    """Generate actionable insights for a job recommendation."""
    insights = []
    
    # Skill insights
    if len(matched_skills) >= 7:
        insights.append(f"✅ Strong skill match! You have {len(matched_skills)} of the required skills.")
    elif len(matched_skills) >= 4:
        insights.append(f"👍 Good skill match with {len(matched_skills)} required skills.")
    else:
        insights.append(f"⚠️ Limited skill match. Consider developing more relevant skills.")
    
    # Missing skills insights
    if missing_skills:
        if len(missing_skills) <= 3:
            insights.append(f"📚 Skills to develop: {', '.join(missing_skills[:3])}")
        else:
            insights.append(f"📚 Key skills to develop: {', '.join(missing_skills[:3])} and {len(missing_skills) - 3} more")
    
    # Experience insights
    if exp_score >= 100:
        insights.append("✅ Your experience level is a perfect match for this role.")
    elif exp_score >= 80:
        insights.append("💼 Your experience level aligns well with this position.")
    
    # Education insights
    if edu_score >= 100:
        insights.append("🎓 Your education meets the requirements.")
    
    return insights
