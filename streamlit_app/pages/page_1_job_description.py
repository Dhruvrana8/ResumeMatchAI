"""
Page 1: Job Description Input
"""

import streamlit as st


def render():
    """Render Page 1: Job Description Input"""
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
