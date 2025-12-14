"""
Home Page: Main landing page with workflow selection
"""

import streamlit as st


def render():
    """Render Home Page with workflow selection"""
    st.title("🎯 ResumeMatchAI")
    st.subheader("Advanced ATS Resume Scanner & Job Matching Platform")
    
    st.markdown("---")
    
    # Introduction
    st.markdown("""
    ### Welcome to ResumeMatchAI!
    
    Choose your workflow to get started:
    """)
    
    st.markdown("")
    
    # Create three columns for the workflow options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📊 Full ATS Analysis")
        st.markdown("""
        **Complete Resume Analysis**
        
        Get comprehensive ATS scoring with:
        - Keyword matching & density
        - Personal info completeness
        - Skills & experience alignment
        - Detailed recommendations
        - AI-powered profile extraction
        - Job recommendations
        
        *Best for: Job seekers wanting detailed feedback*
        """)
        
        if st.button("Start Full Analysis", type="primary", use_container_width=True, key="full_analysis"):
            st.session_state.workflow = "full_analysis"
            st.session_state.page = 1  # Go to job description page
            st.rerun()
    
    with col2:
        st.markdown("### 🤖 ATS Engine (JSON)")
        st.markdown("""
        **Quick JSON Analysis**
        
        Get pure JSON output for:
        - Resume-only scoring
        - Resume-job matching
        - API integration
        - Automated systems
        
        *Best for: Developers & automated workflows*
        """)
        
        if st.button("Use ATS Engine", type="primary", use_container_width=True, key="ats_engine"):
            st.session_state.workflow = "ats_engine"
            st.session_state.page = 6  # Go directly to ATS engine page
            st.rerun()
    
    with col3:
        st.markdown("### 💼 Job Recommendations")
        st.markdown("""
        **Find Matching Jobs**
        
        Discover job positions that match your:
        - Skills & experience
        - Education level
        - Career goals
        - Industry preferences
        
        *Best for: Exploring career opportunities*
        """)
        
        if st.button("Get Recommendations", type="primary", use_container_width=True, key="job_recs"):
            st.session_state.workflow = "job_recommendations"
            st.session_state.page = 2  # Go to resume upload
            st.rerun()
    
    st.markdown("---")
    
    # Features section
    st.markdown("## ✨ Key Features")
    
    feature_col1, feature_col2 = st.columns(2)
    
    with feature_col1:
        st.markdown("""
        **🎯 ATS Compatibility Scoring**
        - Industry-standard ATS algorithms
        - Keyword matching & optimization
        - Format & structure analysis
        
        **🤖 AI-Powered Analysis**
        - LLM-based profile extraction
        - Semantic keyword matching
        - Intelligent recommendations
        """)
    
    with feature_col2:
        st.markdown("""
        **📊 Comprehensive Reports**
        - Detailed score breakdowns
        - Actionable improvement tips
        - Visual analytics
        
        **🔒 Privacy First**
        - No data storage (unless you opt-in)
        - Secure processing
        - Local analysis
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p><strong>ResumeMatchAI v1.0.0</strong></p>
            <p>Made with ❤️ for job seekers and recruiters | Powered by AI & NLP</p>
            <p style='font-size: 0.9em; margin-top: 10px;'>
                💡 Tip: Start with "Full ATS Analysis" for the most comprehensive feedback
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
