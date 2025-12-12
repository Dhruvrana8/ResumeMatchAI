import streamlit as st
import sys
import os
import logging
from io import BytesIO
import pdfplumber
import docx2txt

# Set up logging
logger = logging.getLogger(__name__)

from utils.keywords_extraction import get_keywords
from utils.resume_keywords import get_personal_info, get_websites, get_job_info, get_comprehensive_job_info, get_comprehensive_resume_info
from utils.ats_scoring import calculate_ats_score
from utils.llama_model import extract_user_profile
from utils.postgres_client import save_user_profile, test_connection

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
if 'profile_id' not in st.session_state:
    st.session_state.profile_id = None

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
    if not st.session_state.resume_file or not st.session_state.job_description:
        st.error("Resume file and job description are required for LLM analysis. Please go back and complete the previous steps.")
        return

    st.markdown("""
    ### 🤖 User Profile Extraction with Llama 3.2-1B

    This feature extracts structured user profile information from your resume using Meta's Llama 3.2-1B model:
    - **Personal Information**: Name, email, phone, location, social links
    - **Professional Summary**: Career objective or summary
    - **Skills**: Technical and soft skills
    - **Work Experience**: Job history with details
    - **Education**: Academic qualifications
    - **Certifications, Projects, Languages, Awards**

    The extracted profile will be saved to PostgreSQL for future reference.
    """)

    # PostgreSQL Connection Status
    postgres_status = test_connection()
    if not postgres_status:
        st.warning("⚠️ **PostgreSQL Connection**: Not connected. Profile will be extracted but not saved. Set POSTGRES_URI environment variable to enable saving.")
    
    # Run Profile Extraction Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Extract & Save Profile", type="primary", use_container_width=True):
            with st.spinner("🤖 Extracting user profile from resume... This may take a few minutes."):
                try:
                    # Extract text from resume file
                    import tempfile
                    import os
                    from io import BytesIO
                    import pdfplumber
                    import docx2txt

                    # Determine file extension
                    file_ext = os.path.splitext(st.session_state.resume_file.name)[1].lower()
                    
                    # Extract text from file
                    resume_text_extracted = ""
                    
                    if file_ext == '.pdf':
                        # Try OCR first if available, otherwise use regular extraction
                        try:
                            from utils.document_analyzer import DocumentAnalyzer
                            analyzer = DocumentAnalyzer()
                            
                            # Save file temporarily for OCR
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                                tmp_file.write(st.session_state.resume_file.read())
                                temp_path = tmp_file.name
                            
                            try:
                                ocr_result = analyzer.analyze_document(temp_path, method="ocr")
                                # Extract text from OCR result if successful
                                if "OCR Analysis Not Available" not in ocr_result and "Error" not in ocr_result:
                                    # Parse OCR result to extract text
                                    if "Extracted Text Length:" in ocr_result:
                                        # Extract the text portion from OCR result
                                        parts = ocr_result.split("Full Text:")
                                        if len(parts) > 1:
                                            resume_text_extracted = parts[1].strip()
                            finally:
                                if os.path.exists(temp_path):
                                    os.unlink(temp_path)
                            
                            # Reset file pointer
                            st.session_state.resume_file.seek(0)
                        except Exception as ocr_error:
                            logger.warning(f"OCR failed, using regular extraction: {ocr_error}")
                            # Fall back to regular PDF extraction
                            pass
                    
                    # If OCR didn't work or for DOCX, use regular extraction
                    if not resume_text_extracted:
                        if file_ext == '.pdf':
                            with pdfplumber.open(BytesIO(st.session_state.resume_file.read())) as pdf:
                                page_texts = []
                                for page in pdf.pages:
                                    page_text = page.extract_text()
                                    if page_text:
                                        page_texts.append(page_text)
                                resume_text_extracted = "\n".join(page_texts)
                            st.session_state.resume_file.seek(0)
                        elif file_ext == '.docx':
                            resume_text_extracted = docx2txt.process(BytesIO(st.session_state.resume_file.read()))
                            st.session_state.resume_file.seek(0)
                        else:
                            resume_text_extracted = st.session_state.resume_text or ""
                    
                    # Debug: Show extracted text info
                    if resume_text_extracted:
                        st.info(f"📄 Extracted {len(resume_text_extracted)} characters from resume")
                        st.info(f"📝 Word count: {len(resume_text_extracted.split())} words")
                    
                    # Extract user profile using LLM
                    if resume_text_extracted and len(resume_text_extracted.strip()) > 50:
                        profile = extract_user_profile(resume_text_extracted)
                        
                        # Check if profile has actual data
                        if "error" in profile:
                            st.error(f"❌ Profile extraction error: {profile['error']}")
                        elif not profile.get('personal_info', {}).get('email') and not profile.get('skills'):
                            st.warning("⚠️ Profile extracted but appears to be empty. The LLM may not have parsed the resume correctly.")
                            st.info("💡 **Tip**: Try a resume with clearer formatting or more standard structure.")
                        
                        # Save to PostgreSQL if connected
                        profile_id = None
                        if postgres_status:
                            profile_id = save_user_profile(profile)
                            if profile_id:
                                st.success(f"✅ Profile saved to PostgreSQL with ID: {profile_id}")
                            else:
                                st.warning("⚠️ Profile extracted but failed to save to PostgreSQL")
                        else:
                            st.info("ℹ️ Profile extracted but not saved (PostgreSQL not connected)")
                        
                        # Store in session state
                        st.session_state.llm_analysis = profile
                        st.session_state.profile_id = profile_id
                    elif not resume_text_extracted:
                        st.error("❌ Error: Could not extract text from resume file.")
                        st.info("💡 **Possible causes:**")
                        st.info("• PDF is image-based (scanned) - needs OCR")
                        st.info("• File is corrupted or password-protected")
                        st.info("• Unsupported file format")
                        st.session_state.llm_analysis = {"error": "Could not extract text from resume file"}
                    else:
                        st.error("❌ Error: Extracted text is too short (less than 50 characters).")
                        st.info(f"📄 Only extracted {len(resume_text_extracted)} characters")
                        st.info("💡 This usually means the PDF is image-based and needs OCR.")
                        st.session_state.llm_analysis = {"error": "Extracted text too short"}
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"Profile extraction failed: {str(e)}")
                    if "HUGGING_FACE_API" in str(e):
                        st.info("💡 **Setup Required:** Make sure you have set the HUGGING_FACE_API environment variable with your Hugging Face API token.")
                    elif "PostgreSQL" in str(e) or "psycopg2" in str(e):
                        st.info("💡 **PostgreSQL Setup:** Install psycopg2-binary and set POSTGRES_URI environment variable. Profile will still be extracted but not saved.")
                    else:
                        st.info("💡 **Note:** Check the setup guide for troubleshooting tips.")

    # Display profile results if available
    if st.session_state.llm_analysis:
        st.markdown("---")
        st.markdown("## 📊 Extracted User Profile")
        
        profile = st.session_state.llm_analysis
        
        # Check if it's an error
        if isinstance(profile, dict) and "error" in profile:
            st.error(f"❌ {profile['error']}")
        else:
            # Display profile in structured format
            import json
            
            # Personal Information
            if "personal_info" in profile:
                st.markdown("### 👤 Personal Information")
                personal = profile["personal_info"]
                col1, col2 = st.columns(2)
                
                with col1:
                    if personal.get("name"):
                        st.markdown(f"**Name:** {personal['name']}")
                    if personal.get("email"):
                        st.markdown(f"**Email:** {personal['email']}")
                    if personal.get("phone"):
                        st.markdown(f"**Phone:** {personal['phone']}")
                
                with col2:
                    if personal.get("location"):
                        st.markdown(f"**Location:** {personal['location']}")
                    if personal.get("linkedin"):
                        st.markdown(f"**LinkedIn:** {personal['linkedin']}")
                    if personal.get("github"):
                        st.markdown(f"**GitHub:** {personal['github']}")
            
            # Summary
            if profile.get("summary"):
                st.markdown("### 📝 Professional Summary")
                st.info(profile["summary"])
            
            # Skills
            if profile.get("skills") and len(profile["skills"]) > 0:
                st.markdown("### 🛠️ Skills")
                skills_str = ", ".join(profile["skills"])
                st.write(skills_str)
            
            # Experience
            if profile.get("experience") and len(profile["experience"]) > 0:
                st.markdown("### 💼 Work Experience")
                for exp in profile["experience"]:
                    with st.expander(f"{exp.get('title', 'N/A')} at {exp.get('company', 'N/A')}"):
                        if exp.get("location"):
                            st.write(f"📍 {exp['location']}")
                        if exp.get("start_date") or exp.get("end_date"):
                            dates = f"{exp.get('start_date', '')} - {exp.get('end_date', '')}"
                            st.write(f"📅 {dates}")
                        if exp.get("description"):
                            st.write(exp["description"])
            
            # Education
            if profile.get("education") and len(profile["education"]) > 0:
                st.markdown("### 🎓 Education")
                for edu in profile["education"]:
                    with st.expander(f"{edu.get('degree', 'N/A')} - {edu.get('institution', 'N/A')}"):
                        if edu.get("location"):
                            st.write(f"📍 {edu['location']}")
                        if edu.get("graduation_date"):
                            st.write(f"📅 Graduated: {edu['graduation_date']}")
                        if edu.get("gpa"):
                            st.write(f"📊 GPA: {edu['gpa']}")
            
            # Certifications
            if profile.get("certifications") and len(profile["certifications"]) > 0:
                st.markdown("### 🏆 Certifications")
                for cert in profile["certifications"]:
                    st.write(f"• {cert}")
            
            # Projects
            if profile.get("projects") and len(profile["projects"]) > 0:
                st.markdown("### 🚀 Projects")
                for proj in profile["projects"]:
                    with st.expander(proj.get("name", "Project")):
                        if proj.get("description"):
                            st.write(proj["description"])
                        if proj.get("technologies"):
                            st.write(f"**Technologies:** {', '.join(proj['technologies'])}")
            
            # Languages
            if profile.get("languages") and len(profile["languages"]) > 0:
                st.markdown("### 🌐 Languages")
                st.write(", ".join(profile["languages"]))
            
            # Awards
            if profile.get("awards") and len(profile["awards"]) > 0:
                st.markdown("### 🏅 Awards")
                for award in profile["awards"]:
                    st.write(f"• {award}")
            
            # Show PostgreSQL ID if saved
            if st.session_state.get("profile_id"):
                st.markdown("---")
                st.success(f"✅ **Profile saved to PostgreSQL** with ID: `{st.session_state.profile_id}`")
            
            # Show raw JSON
            with st.expander("📄 View Raw JSON"):
                st.json(profile)

        # Action buttons
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("📋 Copy Profile JSON", use_container_width=True):
                # Create a copyable text area
                import json
                profile_json = json.dumps(st.session_state.llm_analysis, indent=2)
                st.text_area(
                    "Copy the profile JSON below:",
                    value=profile_json,
                    height=200,
                    key="copy_profile"
                )
                st.success("Profile JSON is ready to copy!")

        with col2:
            if st.button("🔄 Extract New Profile", use_container_width=True):
                st.session_state.llm_analysis = None
                st.session_state.profile_id = None
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