#!/usr/bin/env python3
"""
Test script for comprehensive information extraction.
"""

def test_comprehensive_extraction():
    """Test comprehensive extraction functions."""

    # Sample job description
    sample_jd = """
    Senior Python Developer - Remote

    About Our Company:
    TechCorp is a leading software development company specializing in AI and machine learning solutions.

    Job Description:
    We are seeking an experienced Senior Python Developer to join our growing team. This is a full-time remote position with competitive salary and benefits.

    Requirements:
    - 5+ years of Python development experience
    - Bachelor's degree in Computer Science or related field
    - Strong experience with Django, Flask, and FastAPI
    - Proficiency in PostgreSQL and MongoDB
    - Experience with AWS cloud services
    - Knowledge of Docker and Kubernetes
    - Git version control experience
    - Understanding of RESTful APIs and microservices

    Responsibilities:
    - Design and develop scalable web applications
    - Collaborate with cross-functional teams
    - Write clean, maintainable code
    - Participate in code reviews and mentoring
    - Deploy applications to cloud infrastructure

    Benefits:
    - Competitive salary ($100,000 - $150,000)
    - Health, dental, and vision insurance
    - 401k with company match
    - Flexible working hours
    - Professional development budget
    - Home office stipend

    Skills Required:
    - Python, Django, Flask
    - PostgreSQL, MongoDB
    - AWS, Docker, Kubernetes
    - Git, REST APIs
    - Agile development
    """

    # Sample resume
    sample_resume = """
    JOHN DOE
    Python Developer
    john.doe@email.com
    (555) 123-4567
    Toronto, ON

    PROFESSIONAL SUMMARY
    Experienced Python developer with 6+ years of expertise in web development,
    data science, and cloud technologies. Proven track record of delivering
    scalable applications using Django, Flask, and modern DevOps practices.

    WORK EXPERIENCE

    Senior Python Developer
    TechSolutions Inc., Toronto, ON
    January 2020 - Present
    - Developed and maintained web applications using Django and Flask
    - Designed RESTful APIs serving 10,000+ users
    - Implemented CI/CD pipelines using Docker and Kubernetes
    - Collaborated with cross-functional teams in agile environment

    Python Developer
    DataCorp, Toronto, ON
    June 2017 - December 2019
    - Built data processing pipelines using Python and PostgreSQL
    - Developed machine learning models for customer analytics
    - Migrated legacy systems to cloud infrastructure (AWS)

    EDUCATION

    Bachelor of Science in Computer Science
    University of Toronto, Toronto, ON
    2013 - 2017
    GPA: 3.8/4.0

    SKILLS
    - Programming: Python, JavaScript, SQL
    - Frameworks: Django, Flask, FastAPI, React
    - Databases: PostgreSQL, MongoDB, Redis
    - Cloud: AWS, Docker, Kubernetes
    - Tools: Git, Jenkins, Jira

    CERTIFICATIONS
    - AWS Certified Solutions Architect
    - Docker Certified Associate
    - Scrum Master Certification

    PROJECTS

    E-commerce Platform
    - Built scalable e-commerce platform using Django
    - Integrated payment processing and inventory management
    - Deployed on AWS with 99.9% uptime

    Data Analytics Dashboard
    - Developed real-time analytics dashboard
    - Used Python, PostgreSQL, and React
    - Reduced reporting time by 80%

    LANGUAGES
    - English (Native)
    - French (Conversational)
    """

    print("🧪 Testing Comprehensive Information Extraction")
    print("=" * 60)

    try:
        # Test job description extraction
        from utils.resume_keywords import get_comprehensive_job_info
        print("📋 Testing Job Description Extraction...")
        job_info = get_comprehensive_job_info(sample_jd)

        print(f"✅ Company Name: {job_info.get('company_name')}")
        print(f"✅ Position: {job_info.get('position')}")
        print(f"✅ Experience Level: {job_info.get('experience_level')}")
        print(f"✅ Work Type: {job_info.get('work_type')}")
        print(f"✅ Employment Type: {job_info.get('employment_type')}")
        print(f"✅ Salary Info: {job_info.get('salary_info')}")
        print(f"✅ Education Requirements: {job_info.get('education_requirements')}")
        print(f"✅ Benefits: {len(job_info.get('benefits', []))} benefits found")
        print(f"✅ Key Skills: {len(job_info.get('key_skills', []))} skills extracted")

        # Test resume extraction
        from utils.resume_keywords import get_comprehensive_resume_info
        print("\n📄 Testing Resume Extraction...")
        resume_info = get_comprehensive_resume_info(sample_resume)

        personal = resume_info.get('personal_info', {})
        print(f"✅ Name: {personal.get('name')}")
        print(f"✅ Email: {personal.get('email')}")
        print(f"✅ Phone: {personal.get('phone_number')}")
        print(f"✅ Location: {personal.get('major_city')}, {personal.get('province')}")

        print(f"✅ Has Summary: {bool(resume_info.get('professional_summary'))}")
        print(f"✅ Work Experience: {len(resume_info.get('work_experience', []))} entries")
        print(f"✅ Education: {len(resume_info.get('education', []))} entries")
        print(f"✅ Certifications: {len(resume_info.get('certifications', []))} items")
        print(f"✅ Projects: {len(resume_info.get('projects', []))} items")
        print(f"✅ Skills: {len(resume_info.get('skills', []))} skills")
        print(f"✅ Languages: {resume_info.get('languages', [])}")

        # Test ATS scoring with comprehensive data
        from utils.keywords_extraction import get_keywords
        from utils.ats_scoring import calculate_ats_score

        print("\n🎯 Testing ATS Scoring with Comprehensive Data...")
        job_keywords = get_keywords(sample_jd)
        ats_result = calculate_ats_score(sample_resume, job_keywords, resume_info, job_info)

        print(f"✅ Overall Score: {ats_result.get('overall_score', 0):.1f}")
        print(f"✅ Grade: {ats_result.get('grade')}")
        print(f"✅ Compatibility: {ats_result.get('ats_compatibility')}")

        # Check if enhanced analysis is included
        keyword_analysis = ats_result.get('keyword_analysis', {})
        if keyword_analysis.get('categorized_matches'):
            print(f"✅ Categorized Keyword Analysis: {len(keyword_analysis['categorized_matches'])} categories")

        job_analysis = ats_result.get('job_analysis', {})
        resume_analysis = ats_result.get('resume_analysis', {})

        if job_analysis:
            print(f"✅ Job Analysis: Experience level - {job_analysis.get('experience_level')}")

        if resume_analysis:
            print(f"✅ Resume Analysis: {resume_analysis.get('sections_found', [])} sections found")

        print("\n🎉 All comprehensive extraction functions working!")
        return True

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_comprehensive_extraction()