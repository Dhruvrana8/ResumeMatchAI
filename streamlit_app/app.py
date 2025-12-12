import streamlit as st
import sys
import os
from io import BytesIO
import pdfplumber
import docx2txt

from utils.keywords_extraction import get_keywords
from utils.resume_keywords import get_personal_info, get_websites, get_job_info, get_comprehensive_job_info, get_comprehensive_resume_info
from utils.ats_scoring import calculate_ats_score
from utils.llama_model import analyze_resume_and_job_description

# Add streamlit_app directory to path for imports
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Version information
__version__ = "1.0.0"
__author__ = "ResumeMatchAI Team"


# Page configuration
st.set_page_config(
    page_title="ResumeMatchAI — Advanced ATS Resume Scanner",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "ResumeMatchAI - Advanced ATS Resume Scanner with comprehensive scoring and personalized recommendations."
    }
)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 1
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""
if 'resume_file' not in st.session_state:
    st.session_state.resume_file = None
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = None
if 'jd_keywords' not in st.session_state:
    st.session_state.jd_keywords = None
if 'resume_keywords' not in st.session_state:
    st.session_state.resume_keywords = None
if 'results' not in st.session_state:
    st.session_state.results = None
if 'personal_info' not in st.session_state:
    st.session_state.personal_info = None
if 'websites' not in st.session_state:
    st.session_state.websites = None
if 'job_info' not in st.session_state:
    st.session_state.job_info = None
if 'comprehensive_job_info' not in st.session_state:
    st.session_state.comprehensive_job_info = None
if 'comprehensive_resume_info' not in st.session_state:
    st.session_state.comprehensive_resume_info = None
if 'ats_score' not in st.session_state:
    st.session_state.ats_score = None
if 'llm_analysis' not in st.session_state:
    st.session_state.llm_analysis = None

def page_1_job_description():
    """PAGE 1: Job Description Input"""
    st.title("ResumeMatchAI — ATS Resume Scanner")
    st.subheader("Step 1 — Paste the Job Description")
    
    st.markdown("---")
    
    # Large text area for job description
    job_desc = st.text_area(
        "Job Description",
        value=st.session_state.job_description,
        height=400,
        placeholder="Paste the complete job description here...",
        help="Copy and paste the full job description including requirements, skills, and qualifications."
    )
    
    st.session_state.job_description = job_desc
    
    # Word count display and validation
    word_count = len(job_desc.split()) if job_desc.strip() else 0
    max_words = 1000
    
    # Display word count with color coding
    if word_count > max_words:
        st.error(f"Word count: {word_count:,} / {max_words:,} words (exceeds limit by {word_count - max_words:,} words)")
    elif word_count > max_words * 0.9:  # Warning at 90%
        st.warning(f"Word count: {word_count:,} / {max_words:,} words")
    else:
        st.info(f"Word count: {word_count:,} / {max_words:,} words")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Next →", type="primary", use_container_width=True):
            if not job_desc.strip():
                st.error("Please enter a job description before proceeding.")
            elif word_count > max_words:
                st.error(f"Job description exceeds the maximum limit of {max_words:,} words. Please shorten it by {word_count - max_words:,} words.")
            else:
                st.session_state.page = 2
                st.rerun()

def page_2_resume_upload():
    """PAGE 2: Resume Upload"""
    st.title("Upload Your Resume")
    
    # Back button
    if st.button("← Back", type="secondary"):
        st.session_state.page = 1
        st.rerun()
    
    st.markdown("---")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a resume file",
        type=['pdf', 'docx'],
        help="Upload your resume in PDF or DOCX format (max 100MB)"
    )
    
    if uploaded_file is not None:
        # Check file size (100MB = 100 * 1024 * 1024 bytes)
        max_size = 100 * 1024 * 1024
        if uploaded_file.size > max_size:
            st.error(f"File size ({uploaded_file.size / (1024*1024):.2f} MB) exceeds maximum allowed size (100 MB)")
        else:
            st.session_state.resume_file = uploaded_file
            # Need to Read the Resume File
            if uploaded_file.type == "application/pdf":
                # Use pdfplumber for better text extraction
                with pdfplumber.open(BytesIO(uploaded_file.read())) as pdf:
                    # Preserve newlines by joining pages with newlines
                    page_texts = []
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            page_texts.append(page_text)
                    st.session_state.resume_text = "\n".join(page_texts)
                uploaded_file.seek(0)  # Reset file pointer
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                # Use docx2txt for better text extraction
                text = docx2txt.process(BytesIO(uploaded_file.read()))
                st.session_state.resume_text = text if text else ""
                uploaded_file.seek(0)  # Reset file pointer
            st.success(f"File uploaded: {uploaded_file.name} ({uploaded_file.size / 1024:.2f} KB)")
    
    st.markdown("---")
    
    # Run Keyword Extraction button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Run Keyword Extraction", type="primary", use_container_width=True):
            if st.session_state.job_description.strip() and st.session_state.resume_file is not None:
                with st.spinner("Extracting keywords from job description and resume... This may take a moment."):
                    try:
                        st.session_state.page = 3
                        st.rerun()
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                        st.exception(e)
            else:
                if not st.session_state.job_description.strip():
                    st.error("Please provide a job description first.")
                if st.session_state.resume_file is None:
                    st.error("Please upload a resume file.")

    
def page_3_keywords_extraction_and_results():
    """PAGE 3: Display ATS Score and All Extracted Information"""
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
                st.session_state.comprehensive_resume_info,  # Use comprehensive resume info
                st.session_state.comprehensive_job_info      # Use comprehensive job info
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
            # Display keywords as tags
            keywords_str = ", ".join(st.session_state.jd_keywords[:50])  # Show first 50
            st.write(keywords_str)
            if len(st.session_state.jd_keywords) > 50:
                st.caption(f"... and {len(st.session_state.jd_keywords) - 50} more keywords")
            st.caption(f"Total: {len(st.session_state.jd_keywords)} keywords")
        else:
            st.warning("No keywords extracted from job description.")

    with col2:
        st.markdown("### 📄 Resume Keywords")
        if st.session_state.resume_keywords:
            keywords_str = ", ".join(st.session_state.resume_keywords[:50])  # Show first 50
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
    
    # # Just need to see the PDF Content
    # st.write(st.session_state.resume_text)

    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🤖 AI Analysis", type="secondary", use_container_width=True):
            st.session_state.page = 4
            st.rerun()

    with col2:
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
            personal = resume_comp.get('personal_info', {})
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

def page_4_llm_analysis():
    """PAGE 4: LLM Analysis"""
    st.title("ResumeMatchAI — LLM Analysis")
    st.subheader("Step 4 — AI-Powered Comprehensive Analysis")

    # Back button
    if st.button("← Back", type="secondary"):
        st.session_state.page = 3
        st.rerun()

    st.markdown("---")

    # Check if we have the required data
    if not st.session_state.resume_text or not st.session_state.job_description:
        st.error("Resume and job description are required for LLM analysis. Please go back and complete the previous steps.")
        return

    st.markdown("""
    ### 🤖 AI Analysis with Llama 3.2-1B

    This advanced analysis uses Meta's Llama 3.2-1B model to provide:
    - **Overall match assessment** with specific percentage
    - **Detailed strengths and weaknesses** analysis
    - **Actionable improvement recommendations**
    - **Interview preparation guidance**
    - **Salary negotiation insights**

    The AI analyzes your resume against the job description to give you professional HR-level feedback.
    """)

    # Run Analysis Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Run AI Analysis", type="primary", use_container_width=True):
            with st.spinner("🤖 AI is analyzing your resume and job description... This may take a few minutes."):
                try:
                    # Perform LLM analysis
                    analysis = analyze_resume_and_job_description(
                        st.session_state.resume_text,
                        st.session_state.job_description
                    )
                    st.session_state.llm_analysis = analysis
                    st.rerun()
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
                    st.info("💡 **Troubleshooting:** Make sure you have set the HUGGING_FACE_API environment variable with your Hugging Face API token.")

    # Display analysis results if available
    if st.session_state.llm_analysis:
        st.markdown("---")
        st.markdown("## 📊 AI Analysis Results")

        # Analysis content in a nice box
        st.markdown("""
        <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #1f77b4;'>
        """, unsafe_allow_html=True)

        # Display the analysis with proper formatting
        analysis_text = st.session_state.llm_analysis

        # Try to format numbered sections nicely
        lines = analysis_text.split('\n')
        formatted_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Format numbered sections
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.')):
                parts = line.split('.', 1)
                if len(parts) == 2:
                    number = parts[0]
                    content = parts[1].strip()
                    formatted_lines.append(f"**{number}. {content}**")
                    continue

            # Format bullet points
            if line.startswith('- ') or line.startswith('• '):
                formatted_lines.append(f"• {line[2:]}")
                continue

            # Format percentage lines
            if '%' in line and any(char.isdigit() for char in line):
                formatted_lines.append(f"**{line}**")
                continue

            formatted_lines.append(line)

        # Display formatted analysis
        for line in formatted_lines:
            st.markdown(line)

        st.markdown("</div>", unsafe_allow_html=True)

        # Action buttons
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("📋 Copy Analysis", use_container_width=True):
                # Create a copyable text area
                st.text_area(
                    "Copy the analysis below:",
                    value=st.session_state.llm_analysis,
                    height=200,
                    key="copy_analysis"
                )
                st.success("Analysis text is ready to copy!")

        with col2:
            if st.button("🔄 New Analysis", use_container_width=True):
                st.session_state.llm_analysis = None
                st.rerun()

        with col3:
            if st.button("🏠 Start Over", use_container_width=True):
                # Reset all session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

    # Information about the model
    st.markdown("---")
    st.markdown("""
    ### 🧠 About the AI Model

    **Model:** Meta Llama 3.2-1B  
    **Purpose:** Advanced natural language understanding for resume-job matching  
    **Analysis Type:** Comprehensive HR-level assessment  

    *Note: This analysis provides AI-generated insights to supplement the ATS scoring. Always consider multiple factors in your job search.*
    """)

    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; color: #666; padding: 10px;'>
            <p><strong>ResumeMatchAI v{__version__}</strong> — Advanced ATS Resume Scanner with AI Analysis</p>
            <p>Made with ❤️ for job seekers and recruiters | Powered by AI & NLP</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    

# Main app logic
def main():
    if st.session_state.page == 1:
        page_1_job_description()
    elif st.session_state.page == 2:
        page_2_resume_upload()
    elif st.session_state.page == 3:
        page_3_keywords_extraction_and_results()
    elif st.session_state.page == 4:
        page_4_llm_analysis()
    else:
        st.session_state.page = 1
        st.rerun()

if __name__ == "__main__":
    main()