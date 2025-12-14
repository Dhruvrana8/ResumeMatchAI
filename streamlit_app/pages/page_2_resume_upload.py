"""
Page 2: Resume Upload
"""

import streamlit as st
from io import BytesIO
import pdfplumber
import docx2txt


def render():
    """Render Page 2: Resume Upload"""
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
