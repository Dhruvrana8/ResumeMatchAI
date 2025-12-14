import streamlit as st
import os
import sys
import logging
import pdfplumber
import docx2txt

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add module path
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(app_dir)

# Import Utilities
from utils.keywords_extraction import get_keywords
from utils.resume_keywords import get_comprehensive_resume_info, get_comprehensive_job_info
from utils.ats_scoring import calculate_ats_score
from utils.ats_engine import process_ats_request

__version__ = "2.1.0"

st.set_page_config(
    page_title="Resume ATS Scanner",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Session State
if 'ats_result' not in st.session_state:
    st.session_state.ats_result = None
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""

def extract_text_from_file(uploaded_file):
    try:
        text = ""
        if uploaded_file.type == "application/pdf":
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = docx2txt.process(uploaded_file)
        return text
    except Exception as e:
        logger.error(f"Error extracting text: {e}")
        return None

def main():
    # --- Custom CSS for basic styling improvements ---
    st.markdown("""
        <style>
        .stApp {
            background-color: #f8f9fa;
        }
        .main-header {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1e293b;
            text-align: center;
            margin-bottom: 1rem;
        }
        .sub-header {
            font-size: 1.1rem;
            color: #64748b;
            text-align: center;
            margin-bottom: 2rem;
        }
        .card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Header & Hero ---
    st.markdown('<div class="main-header">Resume ATS Scanner</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Optimize your resume with AI-powered ATS analysis</div>', unsafe_allow_html=True)

    # --- Mode Selection ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        mode = st.radio(
            "Analysis Mode",
            ["Resume vs Job Description", "Resume Only"],
            horizontal=True,
            help="Choose 'Resume vs Job Description' to compare your resume against a specific job."
        )

    st.markdown("---")

    # --- Inputs ---
    # Using st.container for grouping
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📄 Upload Resume")
            uploaded_file = st.file_uploader("Upload PDF or DOCX", type=['pdf', 'docx'], label_visibility="collapsed")

        with col2:
            st.subheader("💼 Job Description")
            jd_text = st.text_area(
                "Paste Job Description", 
                height=200, 
                placeholder="Paste the job description here...",
                disabled=(mode == "Resume Only"),
                label_visibility="collapsed"
            )

        # Analyze Button
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            analyze_clicked = st.button("🚀 Analyze Resume", type="primary", use_container_width=True)

    # --- Processing ---
    if analyze_clicked:
        if not uploaded_file:
            st.error("⚠️ Please upload a resume file first.")
        else:
            with st.spinner("Processing your resume..."):
                # Extract Text
                resume_text = extract_text_from_file(uploaded_file)
                st.session_state.resume_text = resume_text
                
                if not resume_text:
                    st.error("❌ Could not extract text. Please try a different file.")
                else:
                    # Prepare Data
                    analysis_mode = "resume_job_match" if mode == "Resume vs Job Description" else "resume_only"
                    
                    if analysis_mode == "resume_job_match" and not jd_text.strip():
                        st.error("⚠️ Job description is required for comparison mode.")
                    else:
                        # Call ATS Engine
                        input_data = {
                            "mode": analysis_mode,
                            "resume_text": resume_text,
                            "job_description": jd_text if analysis_mode == "resume_job_match" else ""
                        }
                        
                        try:
                            result = process_ats_request(input_data)
                            st.session_state.ats_result = result
                            st.success("Analysis Complete!")
                        except Exception as e:
                            st.error(f"Analysis failed: {str(e)}")

    # --- Results Dashboard ---
    if st.session_state.ats_result:
        res = st.session_state.ats_result
        st.markdown("---")
        st.header("📊 Analysis Results")
        
        # 1. Top Level Metrics
        score = res.get('final_ats_score', 0)
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("ATS Score", f"{score}/100", delta=f"{score-70}" if score > 70 else f"{score-70}")
        
        with m2:
            if 'resume_keyword_match' in res:
                matched = len(res['resume_keyword_match'].get('matched_keywords', []))
                st.metric("Keywords Matched", matched, delta="Count", delta_color="off")
            else:
                st.metric("Strengths Identified", len(res.get('strengths', [])), delta="Count")
                
        with m3:
            if 'resume_keyword_match' in res:
                missing = len(res['resume_keyword_match'].get('missing_keywords', []))
                st.metric("Missing Keywords", missing, delta="Critical", delta_color="inverse")
            else:
                st.metric("Improvements Needed", len(res.get('weaknesses', [])), delta="Count", delta_color="inverse")

        # 2. Detailed Breakdown
        st.markdown("### 📝 Detailed Breakdown")
        
        tab1, tab2, tab3 = st.tabs(["Keywords & Skills", "Gaps & Improvements", "Full Report"])
        
        with tab1:
            if 'resume_keyword_match' in res:
                matches = res['resume_keyword_match'].get('matched_keywords', [])
                st.success(f"✅ **Matched Keywords ({len(matches)})**")
                st.write(", ".join(matches))
                
                partials = res['resume_keyword_match'].get('partial_matches', [])
                if partials:
                    st.warning(f"⚠️ **Partial Matches ({len(partials)})**")
                    st.write(", ".join(partials))
            else:
                st.success("✅ **Strengths**")
                for s in res.get('strengths', []):
                    st.write(f"- {s}")
                    
        with tab2:
            if 'resume_keyword_match' in res:
                missing = res['resume_keyword_match'].get('missing_keywords', [])
                st.error(f"❌ **Missing Keywords ({len(missing)})**")
                st.write(", ".join(missing))
                
                if 'recommendations' in res:
                    st.markdown("#### 💡 Recommendations")
                    for rec in res['recommendations']:
                        st.info(rec)
            else:
                st.error("⚠️ **Weaknesses**")
                for w in res.get('weaknesses', []):
                    st.write(f"- {w}")
                    
                if 'improvement_suggestions' in res:
                    st.markdown("#### 💡 Suggestions")
                    for s in res['improvement_suggestions']:
                        st.info(s)
                        
        with tab3:
            st.json(res)

if __name__ == "__main__":
    main()