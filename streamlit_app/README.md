# ResumeMatchAI — ATS Resume Scanner

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Streamlit-1.28+-red.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/spaCy-3.7+-green.svg" alt="spaCy">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</div>

## 🎯 Overview

**ResumeMatchAI** is an advanced Applicant Tracking System (ATS) resume scanner that analyzes resumes against job descriptions to provide comprehensive compatibility scores and actionable improvement recommendations. Using natural language processing and machine learning, it helps job seekers optimize their resumes for better ATS performance.

### ✨ Key Features

- **🔍 Advanced ATS Scoring**: Comprehensive scoring algorithm with 7 weighted factors
- **📊 Keyword Analysis**: Intelligent keyword matching with similarity detection
- **👤 Enhanced Personal Info Extraction**: Accurate name, email, phone, and location detection
- **🎯 Smart Recommendations**: Prioritized, actionable feedback for resume improvement
- **📄 Multi-Format Support**: PDF and DOCX resume processing
- **🌐 Web-Friendly Interface**: Clean Streamlit web application
- **⚡ Real-time Analysis**: Instant results with detailed breakdowns

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Virtual environment (recommended)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/ResumeMatchAI.git
   cd ResumeMatchAI/streamlit_app
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy language model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

### Running the Application

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501` to access the application.

## 📋 How It Works

### 1. **Job Description Input**

Paste the complete job description you're applying for. The system will extract key requirements and skills.

### 2. **Resume Upload**

Upload your resume in PDF or DOCX format. The system supports text extraction from various document formats.

### 3. **ATS Analysis**

The system performs comprehensive analysis including:

- **Keyword Matching**: Exact and similar keyword detection
- **Personal Information**: Name, contact details, and location extraction
- **Skills Alignment**: Technical skills assessment
- **Experience Relevance**: Work experience analysis
- **Formatting Quality**: Resume structure evaluation

### 4. **Results & Recommendations**

Receive a detailed ATS compatibility report with:

- Overall score (0-100) with letter grade
- Component breakdown with visual progress bars
- Prioritized improvement recommendations
- Pass rate predictions

## 🎯 ATS Scoring System

### Scoring Components & Weights

| Component            | Weight | Description                         |
| -------------------- | ------ | ----------------------------------- |
| **Keyword Match**    | 40%    | Exact and similar keyword detection |
| **Keyword Density**  | 15%    | Balanced keyword distribution       |
| **Personal Info**    | 15%    | Contact information completeness    |
| **Skills Alignment** | 10%    | Technical skills matching           |
| **Experience Match** | 10%    | Relevant experience assessment      |
| **Education Match**  | 5%     | Qualifications alignment            |
| **Formatting**       | 5%     | Resume structure quality            |

### Score Interpretation

- **90-100 (A)**: Exceptional - 95%+ chance of passing ATS
- **80-89 (B)**: Excellent - 85%+ chance of passing ATS
- **70-79 (C)**: Very Good - 75%+ chance of passing ATS
- **60-69 (D)**: Good - 65%+ chance of passing ATS
- **50-59 (F)**: Fair - 55%+ chance of passing ATS
- **Below 50**: Poor - Significant improvements needed

## 🛠️ Technology Stack

### Core Technologies

- **Python 3.11+**: Primary programming language
- **Streamlit**: Web application framework
- **spaCy**: Natural language processing
- **NLTK**: Text processing and stemming

### Libraries

- **pdfplumber**: PDF text extraction
- **python-docx**: DOCX file processing
- **Pandas**: Data manipulation
- **NumPy**: Numerical computations

### Machine Learning

- **Transformers**: For advanced NLP tasks
- **Torch**: Deep learning framework
- **Accelerate**: Model optimization

## 📁 Project Structure

```
ResumeMatchAI/
├── streamlit_app/
│   ├── app.py                 # Main Streamlit application
│   ├── main.py               # Entry point
│   ├── requirements.txt      # Python dependencies
│   ├── pyproject.toml        # Project configuration
│   ├── README.md            # This file
│   └── utils/
│       ├── __init__.py
│       ├── ats_scoring.py    # ATS scoring algorithm
│       ├── keywords_extraction.py  # Keyword processing
│       └── resume_keywords.py      # Personal info extraction
├── .python-version           # Python version specification
├── uv.lock                   # Dependency lock file
└── .gitignore               # Git ignore rules
```

## 🔧 Configuration

### Environment Variables

No environment variables are required for basic functionality. However, you can customize:

- **MAX_FILE_SIZE**: Maximum resume file size (default: 100MB)
- **WORD_LIMIT**: Job description word limit (default: 1000)
- **SIMILARITY_THRESHOLD**: Keyword similarity threshold (default: 0.7)

### Customization

The scoring weights and thresholds can be adjusted in `utils/ats_scoring.py`:

```python
WEIGHTS = {
    'keyword_match': 0.40,
    'keyword_density': 0.15,
    'personal_info': 0.15,
    'skills_alignment': 0.10,
    'experience_match': 0.10,
    'education_match': 0.05,
    'formatting': 0.05
}
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and commit: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black .
isort .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **spaCy** for powerful NLP capabilities
- **Streamlit** for the amazing web app framework
- **NLTK** for text processing utilities
- Open source community for inspiration and tools

## 📞 Support

If you have questions or need help:

- **Issues**: [GitHub Issues](https://github.com/yourusername/ResumeMatchAI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ResumeMatchAI/discussions)
- **Email**: support@resumematchai.com

---

<div align="center">
  <p><strong>Made with ❤️ for job seekers and recruiters</strong></p>
  <p>
    <a href="#resume">Resume</a> •
    <a href="#ats-scoring-system">ATS Scoring</a> •
    <a href="#contributing">Contributing</a> •
    <a href="#license">License</a>
  </p>
</div>
