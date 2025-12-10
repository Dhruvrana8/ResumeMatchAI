import streamlit as st
import sys
import os

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
            st.success(f"File uploaded: {uploaded_file.name} ({uploaded_file.size / 1024:.2f} KB)")
    
    st.markdown("---")
    
    # Run Keyword Extraction button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Run Keyword Extraction", type="primary", use_container_width=True):
            if st.session_state.job_description.strip() and st.session_state.resume_file is not None:
                with st.spinner("Extracting keywords from job description and resume... This may take a moment."):
                    try:
                        st.rerun()
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                        st.exception(e)
            else:
                if not st.session_state.job_description.strip():
                    st.error("Please provide a job description first.")
                if st.session_state.resume_file is None:
                    st.error("Please upload a resume file.")
# Main app logic
def main():
    if st.session_state.page == 1:
        page_1_job_description()
    elif st.session_state.page == 2:
        page_2_resume_upload()
    else:
        st.session_state.page = 1
        st.rerun()

if __name__ == "__main__":
    main()
