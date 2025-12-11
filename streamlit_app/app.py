import streamlit as st
import sys
import os
from io import BytesIO
import pdfplumber
import docx2txt

from utils.keywords_extraction import get_keywords
from utils.resume_keywords import get_personal_info, get_websites, get_job_info

# Add streamlit_app directory to path for imports
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)


# Page configuration
st.set_page_config(
    page_title="ResumeMatchAI — ATS Resume Scanner",
    page_icon="📄",
    layout="wide"
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
    """PAGE 4: Display All Extracted Information"""
    st.title("Resume ATS Scanner — Results")
    st.subheader("Step 3 — All Extracted Information")

    # Back button
    if st.button("← Back", type="secondary"):
        st.session_state.page = 3
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
        with st.spinner("Extracting job information..."):
            st.session_state.job_info = get_job_info(st.session_state.job_description)

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
            st.rerun()

# Main app logic
def main():
    if st.session_state.page == 1:
        page_1_job_description()
    elif st.session_state.page == 2:
        page_2_resume_upload()
    elif st.session_state.page == 3:
        page_3_keywords_extraction_and_results()
    else:
        st.session_state.page = 1
        st.rerun()

if __name__ == "__main__":
    main()