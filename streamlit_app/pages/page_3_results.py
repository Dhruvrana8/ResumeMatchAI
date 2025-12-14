"""
Page 3: ATS Results and Analysis
"""

import streamlit as st
from utils.keywords_extraction import get_keywords
from utils.resume_keywords import (
    get_personal_info,
    get_websites,
    get_job_info,
    get_comprehensive_job_info,
    get_comprehensive_resume_info
)
from utils.ats_scoring import calculate_ats_score

# Version info (imported from main app)
__version__ = "1.0.0"


def render():
    """Render Page 3: ATS Compatibility Results"""
    st.title("ResumeMatchAI — ATS Compatibility Results")
    st.subheader("Step 3 — ATS Score & Analysis")

    # Back button
    if st.button("← Back", type="secondary"):
        st.session_state.page = 2
        st.rerun()

    st.markdown("---")

    # Extract all information if not already extracted
    if st.session_state.jd_keywords is None:
        with st.spinner("Extracting keywords from job description..."):
            st.session_state.jd_keywords = get_keywords(st.session_state.job_description)
            
    if st.session_state.resume_keywords is None:
        with st.spinner("Extracting keywords from resume..."):
            st.session_state.resume_keywords = get_keywords(st.session_state.resume_text)
    
    if st.session_state.personal_info is None:
        with st.spinner("Extracting personal information..."):
            st.session_state.personal_info = get_personal_info(st.session_state.resume_text)
    
    if st.session_state.websites is None:
        with st.spinner("Extracting websites..."):
            st.session_state.websites = get_websites(st.session_state.resume_text)
    
    if st.session_state.job_info is None:
        with st.spinner("Extracting basic job information..."):
            st.session_state.job_info = get_job_info(st.session_state.job_description)

    if st.session_state.comprehensive_job_info is None:
        with st.spinner("Extracting comprehensive job information..."):
            st.session_state.comprehensive_job_info = get_comprehensive_job_info(st.session_state.job_description)

    if st.session_state.comprehensive_resume_info is None:
        with st.spinner("Extracting comprehensive resume information..."):
            st.session_state.comprehensive_resume_info = get_comprehensive_resume_info(st.session_state.resume_text)

    # Calculate ATS score if not already calculated
    if st.session_state.ats_score is None:
        with st.spinner("Calculating ATS compatibility score..."):
            st.session_state.ats_score = calculate_ats_score(
                st.session_state.resume_text,
                st.session_state.jd_keywords,
                st.session_state.comprehensive_resume_info,
                st.session_state.comprehensive_job_info
            )

    # Display ATS Score prominently at the top
    ats_score = st.session_state.ats_score
    st.markdown("## 🎯 ATS Compatibility Score")

    # Main score display
    col_score, col_grade, col_compat = st.columns([2, 1, 2])

    with col_score:
        score = ats_score['overall_score']
        if score >= 80:
            st.success(f"### {score:.1f}/100")
        elif score >= 60:
            st.warning(f"### {score:.1f}/100")
        else:
            st.error(f"### {score:.1f}/100")

    with col_grade:
        grade = ats_score['grade']
        grade_colors = {'A': '🟢', 'B': '🟡', 'C': '🟠', 'D': '🔴', 'F': '🔴'}
        st.markdown(f"### {grade_colors.get(grade, '⚪')} Grade {grade}")

    with col_compat:
        compatibility = ats_score['ats_compatibility']
        st.info(f"**{compatibility}**")

    # Score breakdown
    st.markdown("### 📊 Score Breakdown")
    components = ats_score['component_scores']

    # Create a nice progress bar layout
    cols = st.columns(2)
    component_names = {
        'keyword_match': 'Keyword Match (40%)',
        'keyword_density': 'Keyword Density (15%)',
        'personal_info': 'Personal Info (15%)',
        'skills_alignment': 'Skills Alignment (10%)',
        'experience_match': 'Experience Match (10%)',
        'education_match': 'Education Match (5%)',
        'formatting': 'Formatting (5%)'
    }

    for i, (component, score) in enumerate(components.items()):
        with cols[i % 2]:
            st.markdown(f"**{component_names[component]}**")
            st.progress(score / 100)
            st.caption(f"{score:.1f}/100")

    # Recommendations
    if ats_score['recommendations']:
        st.markdown("### 💡 Recommendations to Improve Your Score")

        # Group recommendations by priority
        priority_groups = {
            '🚨': 'Critical Issues',
            '📈': 'High Priority',
            '🔧': 'Medium Priority',
            '💡': 'Low Priority',
            '📊': 'Overall Assessment',
            '✨': 'Fine Tuning',
            '🎉': 'Excellent Performance'
        }

        current_group = None
        for rec in ats_score['recommendations']:
            priority_icon = rec.split()[0]
            if priority_icon in priority_groups and priority_icon != current_group:
                current_group = priority_icon
                st.markdown(f"**{priority_groups[priority_icon]}**")

            # Remove the priority icon from the display text
            display_text = ' '.join(rec.split()[1:])
            if priority_icon in ['🚨', '📈', '🔧', '💡']:
                st.markdown(f"• {display_text}")
            else:
                st.info(display_text)

    st.markdown("---")

    # Display all information in organized sections
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📋 Job Description Keywords")
        if st.session_state.jd_keywords:
            keywords_str = ", ".join(st.session_state.jd_keywords[:50])
            st.write(keywords_str)
            if len(st.session_state.jd_keywords) > 50:
                st.caption(f"... and {len(st.session_state.jd_keywords) - 50} more keywords")
            st.caption(f"Total: {len(st.session_state.jd_keywords)} keywords")
        else:
            st.warning("No keywords extracted from job description.")

    with col2:
        st.markdown("### 📄 Resume Keywords")
        if st.session_state.resume_keywords:
            keywords_str = ", ".join(st.session_state.resume_keywords[:50])
            st.write(keywords_str)
            if len(st.session_state.resume_keywords) > 50:
                st.caption(f"... and {len(st.session_state.resume_keywords) - 50} more keywords")
            st.caption(f"Total: {len(st.session_state.resume_keywords)} keywords")
        else:
            st.warning("No keywords extracted from resume.")

    st.markdown("---")

    # Job Information Section
    st.markdown("### 💼 Job Information")
    job_info = st.session_state.job_info
    
    if job_info:
        job_col1, job_col2 = st.columns(2)
        
        with job_col1:
            st.markdown("**Company Name:**")
            st.write(job_info.get("company_name", "Not found") or "Not found")
            
            st.markdown("**Position:**")
            st.write(job_info.get("position", "Not found") or "Not found")
        
        with job_col2:
            st.markdown("**Location:**")
            st.write(job_info.get("location", "Not found") or "Not found")
            
            st.markdown("**Website:**")
            website = job_info.get("website", None)
            if website:
                st.write(website)
            else:
                st.write("Not found")
    else:
        st.warning("No job information could be extracted from the job description.")

    st.markdown("---")

    # Personal Information Section
    st.markdown("### 👤 Personal Information")
    personal_info = st.session_state.personal_info
    
    if personal_info:
        info_col1, info_col2 = st.columns(2)
        
        with info_col1:
            st.markdown("**Name:**")
            st.write(personal_info.get("name", "Not found") or "Not found")
            
            st.markdown("**Email:**")
            st.write(personal_info.get("email", "Not found") or "Not found")
        
        with info_col2:
            st.markdown("**Phone Number:**")
            st.write(personal_info.get("phone_number", "Not found") or "Not found")
            
            if personal_info.get("major_city") or personal_info.get("province"):
                st.markdown("**Location:**")
                location_parts = []
                if personal_info.get("major_city"):
                    location_parts.append(personal_info["major_city"].title())
                if personal_info.get("province"):
                    location_parts.append(personal_info["province"].upper())
                st.write(", ".join(location_parts) if location_parts else "Not found")
    else:
        st.warning("No personal information could be extracted from the resume.")

    st.markdown("---")
    
    # Job Description Keywords Section
    st.markdown("### 📋 Job Description Keywords")
    jd_keywords = st.session_state.jd_keywords
    if jd_keywords:
        st.write(jd_keywords)
    else:
        st.warning("No keywords extracted from job description.")

    # Websites Section
    st.markdown("### 🌐 Websites Found in Resume")
    websites = st.session_state.websites
    
    if websites:
        st.write(f"Found {len(websites)} website(s):")
        for i, website in enumerate(websites, 1):
            st.write(f"{i}. {website}")
    else:
        st.info("No websites found in the resume.")

    st.markdown("---")

    # Action buttons
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        if st.button("🤖 AI Analysis", type="secondary", use_container_width=True):
            st.session_state.page = 4
            st.rerun()
    
    with col2:
        if st.button("📊 ATS Engine", type="secondary", use_container_width=True):
            st.session_state.page = 6
            st.rerun()

    with col3:
        if st.button("🔄 Start Over", type="primary", use_container_width=True):
            # Reset session state
            st.session_state.page = 1
            st.session_state.job_description = ""
            st.session_state.resume_file = None
            st.session_state.resume_text = None
            st.session_state.jd_keywords = None
            st.session_state.resume_keywords = None
            st.session_state.personal_info = None
            st.session_state.websites = None
            st.session_state.job_info = None
            st.session_state.comprehensive_job_info = None
            st.session_state.comprehensive_resume_info = None
            st.session_state.ats_score = None
            st.session_state.llm_analysis = None
            st.session_state.profile_id = None
            st.rerun()

    # Display Keyword Analysis Details
    keyword_analysis = ats_score.get('keyword_analysis', {})
    if keyword_analysis and keyword_analysis.get('categorized_matches'):
        st.markdown("### 🔍 Keyword Category Analysis")
        categorized = keyword_analysis['categorized_matches']

        # Display category scores
        cat_cols = st.columns(min(len(categorized), 3))
        for i, (category, data) in enumerate(list(categorized.items())[:3]):
            with cat_cols[i]:
                score = data.get('score', 0)
                st.metric(
                    f"{category.replace('_', ' ').title()}",
                    f"{score:.1f}%",
                    help=f"Matching score for {category}"
                )

    # Display Comprehensive Analysis
    st.markdown("---")
    st.markdown("## 📊 Detailed Analysis")

    # Get comprehensive information
    job_comp = st.session_state.comprehensive_job_info or {}
    resume_comp = st.session_state.comprehensive_resume_info or {}

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 💼 Job Requirements Analysis")
        if job_comp:
            st.markdown(f"**Experience Level:** {job_comp.get('experience_level', 'Not specified')}")
            st.markdown(f"**Work Type:** {job_comp.get('work_type', 'Not specified')}")
            st.markdown(f"**Employment Type:** {job_comp.get('employment_type', 'Not specified')}")

            if job_comp.get('salary_info'):
                st.markdown(f"**Salary Info:** {job_comp['salary_info']}")

            if job_comp.get('education_requirements'):
                st.markdown(f"**Education:** {', '.join(job_comp['education_requirements'][:3])}")

            if job_comp.get('benefits'):
                st.markdown(f"**Benefits:** {', '.join(job_comp['benefits'][:3])}")

            if job_comp.get('key_skills'):
                st.markdown("**Key Skills Required:**")
                st.write(", ".join(job_comp['key_skills'][:10]))
        else:
            st.info("Basic job information extracted only")

    with col2:
        st.markdown("### 📄 Resume Content Analysis")
        if resume_comp:
            st.markdown(f"**Contact Completeness:** {ats_score.get('resume_analysis', {}).get('contact_completeness', 0):.0f}%")
            st.markdown(f"**Experience Entries:** {len(resume_comp.get('work_experience', []))}")
            st.markdown(f"**Education Entries:** {len(resume_comp.get('education', []))}")
            st.markdown(f"**Certifications:** {len(resume_comp.get('certifications', []))}")
            st.markdown(f"**Projects:** {len(resume_comp.get('projects', []))}")
            st.markdown(f"**Skills Listed:** {len(resume_comp.get('skills', []))}")

            if resume_comp.get('languages'):
                st.markdown(f"**Languages:** {', '.join(resume_comp['languages'][:3])}")

            sections = resume_comp.get('sections_found', [])
            if sections:
                st.markdown(f"**Sections Found:** {', '.join(sections)}")
        else:
            st.info("Basic resume information extracted only")

    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; color: #666; padding: 10px;'>
            <p><strong>ResumeMatchAI v{__version__}</strong> — Advanced ATS Resume Scanner</p>
            <p>Made with ❤️ for job seekers and recruiters | Powered by AI & NLP</p>
        </div>
        """,
        unsafe_allow_html=True
    )
