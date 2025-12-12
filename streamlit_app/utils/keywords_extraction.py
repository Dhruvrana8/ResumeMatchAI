import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from nltk.stem import PorterStemmer
from typing import List, Dict
from difflib import SequenceMatcher

# Load spaCy model and NLTK stemmer once
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    print("Downloading spaCy model 'en_core_web_sm'. This may take a moment...")
    spacy.cli.download('en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')

ps = PorterStemmer()
stop_words = set(STOP_WORDS) # Use a set for faster lookup

min_len = 2

list_of_Job_descriptions_keywords = [
    'Education',
    'Experience',
    'Skills',
    'Responsibilities',
    'Requirements',
    'Qualifications',
    'Knowledge',
    'Certifications',
    'Achievements',
    'Objectives',
    'Job Title',
    'Position',
    'Role',
    'About Us',
    'Company Overview',
    'Key Responsibilities',
    'Technical Skills',
    'Soft Skills',
    'Competencies',
    'Preferred Qualifications',
    'Mandatory Skills',
    'Core Competencies',
    'Job Summary',
    'Role Description',
    'Work Environment',
    'Location',
    'Salary',
    'Benefits',
    'Perks',
    'Reporting To',
    'Team',
    'Project Details',
    'Performance Metrics',
    'Deliverables',
    'Expectations',
    'Professional Development',
    'Training',
    'Experience Level',
    'Industry Knowledge',
    'Tools',
    'Languages',
    'Travel Requirements',
    'Work Hours',
    'Shift',
    'Contract Type',
    'Internship',
    'Volunteer Work',
    'Extra-Curricular Activities',
    'Awards',
    'Publications',
]


def get_keywords(text: str, min_len: int = 2, with_nouns: bool = True, with_stopwords: bool = False) -> list[str]:
    """
    Extracts keywords from a given text (e.g., a job description).
    Filters nouns, proper nouns, verbs, removes stopwords, lemmatizes,
    and returns a sorted list of unique lemmatized keywords.
    """
    if not text or not text.strip():
        return []

    doc = nlp(text)
    processed_tokens = []

    for token in doc:
        # Only nouns, proper nouns, and verbs of sufficient length
        if with_nouns and token.pos_ not in ["NOUN", "PROPN", "VERB"]:
            continue

        # Skip punctuation and non-alphanumeric tokens
        if not token.is_alpha:
            continue

        word = token.text.lower()
        if len(word) < min_len:
            continue

        if not with_stopwords and word in stop_words:
            continue

        # Lemmatize (better than stemming for keyword matching)
        lemma = token.lemma_.lower()

        # Skip very common lemmas that aren't useful keywords
        if lemma in {'be', 'have', 'do', 'make', 'get', 'go', 'know', 'take', 'see', 'come', 'want', 'use', 'find', 'give', 'tell', 'work', 'call', 'try', 'ask', 'need', 'feel', 'become', 'leave', 'put', 'mean', 'keep', 'let', 'begin', 'seem', 'help', 'talk', 'turn', 'start', 'might', 'show', 'hear', 'play', 'run', 'move', 'like', 'live', 'believe', 'bring', 'happen', 'write', 'provide', 'sit', 'stand', 'lose', 'pay', 'meet', 'include', 'continue', 'set', 'learn', 'change', 'lead', 'understand', 'watch', 'follow', 'stop', 'create', 'speak', 'read', 'allow', 'add', 'spend', 'grow', 'open', 'walk', 'win', 'offer', 'remember', 'love', 'consider', 'appear', 'buy', 'wait', 'serve', 'die', 'send', 'expect', 'build', 'stay', 'fall', 'cut', 'reach', 'kill', 'remain', 'suggest', 'raise', 'pass', 'sell', 'require', 'report', 'decide', 'pull'}:
            continue

        processed_tokens.append(lemma)

    # Remove duplicates and sort
    unique_tokens = sorted(list(set(processed_tokens)))
    return unique_tokens

def get_job_importance_keywords(text: str) -> list[str]:
    """
    Extracts keywords from a given text (e.g., a job description) that are important for the job.
    Returns lemmatized keywords for better ATS matching.
    """
    if not text or not text.strip():
        return []

    doc = nlp(text)
    processed_tokens = []

    for token in doc:
        if token.pos_ not in ["NOUN", "PROPN", "VERB"]:
            continue
        if not token.is_alpha:
            continue
        word = token.text.lower()
        if len(word) < min_len:
            continue
        if not with_stopwords and word in stop_words:
            continue
        lemma = token.lemma_.lower()

        # Skip very common lemmas
        if lemma in {'be', 'have', 'do', 'make', 'get', 'go', 'know', 'take', 'see', 'come', 'want', 'use', 'find', 'give', 'tell', 'work', 'call', 'try', 'ask', 'need', 'feel', 'become', 'leave', 'put', 'mean', 'keep', 'let', 'begin', 'seem', 'help', 'talk', 'turn', 'start', 'might', 'show', 'hear', 'play', 'run', 'move', 'like', 'live', 'believe', 'bring', 'happen', 'write', 'provide', 'sit', 'stand', 'lose', 'pay', 'meet', 'include', 'continue', 'set', 'learn', 'change', 'lead', 'understand', 'watch', 'follow', 'stop', 'create', 'speak', 'read', 'allow', 'add', 'spend', 'grow', 'open', 'walk', 'win', 'offer', 'remember', 'love', 'consider', 'appear', 'buy', 'wait', 'serve', 'die', 'send', 'expect', 'build', 'stay', 'fall', 'cut', 'reach', 'kill', 'remain', 'suggest', 'raise', 'pass', 'sell', 'require', 'report', 'decide', 'pull'}:
            continue

        processed_tokens.append(lemma)

    # Remove duplicates and sort
    unique_tokens = sorted(list(set(processed_tokens)))
    return unique_tokens

def calculate_keyword_similarity(keyword1: str, keyword2: str) -> float:
    """
    Calculate similarity between two lemmatized keywords using multiple methods.
    Returns a score between 0 and 1.
    """
    if not keyword1 or not keyword2:
        return 0.0

    k1, k2 = keyword1.lower().strip(), keyword2.lower().strip()

    # Exact match gets highest score
    if k1 == k2:
        return 1.0

    # Since keywords are already lemmatized, check if they're the same lemma
    # But also check stemmed versions for additional matching
    stem1, stem2 = ps.stem(k1), ps.stem(k2)
    if stem1 == stem2:
        return 0.9

    # Sequence similarity (for typos and variations)
    seq_similarity = SequenceMatcher(None, k1, k2).ratio()
    if seq_similarity > 0.85:  # Higher threshold since these are already processed
        return seq_similarity * 0.8

    # Check for compound words or partial matches
    words1, words2 = set(k1.split()), set(k2.split())
    if words1 & words2:  # Any common words
        overlap = len(words1 & words2) / max(len(words1), len(words2))
        return overlap * 0.7

    # Check for abbreviations or partial matches
    if len(k1) <= 5 and k2.startswith(k1):
        return 0.6
    if len(k2) <= 5 and k1.startswith(k2):
        return 0.6

    # Check for common variations (e.g., "develop" vs "development")
    if k1 in k2 or k2 in k1:
        longer = max(len(k1), len(k2))
        shorter = min(len(k1), len(k2))
        if longer - shorter <= 4:  # Small difference in length
            return 0.5

    return 0.0

def find_similar_keywords(job_keywords: List[str], resume_keywords: List[str],
                         similarity_threshold: float = 0.7) -> Dict[str, List[str]]:
    """
    Find similar keywords between job description and resume.
    Returns a dictionary mapping job keywords to lists of similar resume keywords.
    """
    matches = {}

    for job_kw in job_keywords:
        similar_resume_kws = []
        for resume_kw in resume_keywords:
            similarity = calculate_keyword_similarity(job_kw, resume_kw)
            if similarity >= similarity_threshold:
                similar_resume_kws.append((resume_kw, similarity))

        # Sort by similarity score and take top matches
        similar_resume_kws.sort(key=lambda x: x[1], reverse=True)
        if similar_resume_kws:
            matches[job_kw] = [kw for kw, _ in similar_resume_kws[:3]]  # Top 3 matches

    return matches

def categorize_keywords(keywords: List[str]) -> Dict[str, List[str]]:
    """
    Categorize keywords into different types for better analysis.
    """
    categories = {
        'technical_skills': [],
        'soft_skills': [],
        'tools_technologies': [],
        'industry_terms': [],
        'education_terms': [],
        'certifications': [],
        'languages': [],
        'other': []
    }

    # Define keyword categories
    technical_skills = [
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
        'algorithm', 'data structure', 'api', 'database', 'sql', 'nosql', 'mongodb', 'postgresql',
        'machine learning', 'deep learning', 'neural network', 'artificial intelligence', 'ai',
        'computer vision', 'nlp', 'natural language processing', 'data science', 'analytics'
    ]

    tools_technologies = [
        'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'git', 'jenkins', 'ci/cd', 'agile',
        'scrum', 'linux', 'windows', 'react', 'angular', 'vue', 'node', 'django', 'flask',
        'spring', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn', 'jupyter'
    ]

    soft_skills = [
        'communication', 'leadership', 'teamwork', 'problem solving', 'critical thinking',
        'time management', 'adaptability', 'creativity', 'collaboration', 'empathy',
        'project management', 'decision making', 'conflict resolution', 'mentoring'
    ]

    education_terms = [
        'bachelor', 'master', 'phd', 'degree', 'university', 'college', 'graduate',
        'undergraduate', 'diploma', 'certificate', 'education', 'qualification'
    ]

    certifications = [
        'cpa', 'cfa', 'pmp', 'aws certified', 'azure', 'gcp', 'cissp', 'ceh', 'comptia',
        'ccna', 'ccnp', 'mcsa', 'mcse', 'oracle', 'red hat', 'itil'
    ]

    languages = [
        'english', 'french', 'spanish', 'german', 'italian', 'portuguese',
        'chinese', 'mandarin', 'japanese', 'korean', 'arabic', 'hindi'
    ]

    for keyword in keywords:
        kw_lower = keyword.lower()

        if any(skill in kw_lower for skill in technical_skills):
            categories['technical_skills'].append(keyword)
        elif any(tool in kw_lower for tool in tools_technologies):
            categories['tools_technologies'].append(keyword)
        elif any(skill in kw_lower for skill in soft_skills):
            categories['soft_skills'].append(keyword)
        elif any(edu in kw_lower for edu in education_terms):
            categories['education_terms'].append(keyword)
        elif any(cert in kw_lower for cert in certifications):
            categories['certifications'].append(keyword)
        elif any(lang in kw_lower for lang in languages):
            categories['languages'].append(keyword)
        else:
            categories['other'].append(keyword)

    return categories

def extract_structured_keywords(text: str) -> Dict[str, List[str]]:
    """
    Extract keywords and categorize them for structured analysis.
    """
    # Get basic keywords
    keywords = get_keywords(text)

    # Categorize them
    categories = categorize_keywords(keywords)

    return categories

def enhanced_keyword_match_score(job_keywords: List[str], resume_text: str,
                               use_similarity: bool = True) -> Dict:
    """
    Enhanced keyword matching with similarity scoring and detailed analysis.
    Returns detailed matching information including exact and similar matches.
    """
    if not job_keywords:
        return {
            'score': 0.0,
            'exact_matches': [],
            'similar_matches': {},
            'total_job_keywords': 0,
            'matched_job_keywords': 0,
            'match_details': {'exact_count': 0, 'similar_count': 0}
        }

    # Get resume keywords (lemmatized)
    resume_keywords = get_keywords(resume_text)
    resume_text_lower = resume_text.lower()

    # Find exact matches - check both lemmatized form and original variations
    exact_matches = []
    for keyword in job_keywords:
        keyword_lower = keyword.lower()

        # Check if the lemmatized keyword appears in the resume text
        if keyword_lower in resume_text_lower:
            exact_matches.append(keyword)
            continue

        # Also check for common variations (plural, gerund forms, etc.)
        variations = [
            keyword_lower,  # base form
            keyword_lower + 's',  # plural
            keyword_lower + 'es',  # plural
            keyword_lower + 'ing',  # gerund
            keyword_lower + 'ed',  # past tense
            keyword_lower.rstrip('e') + 'ing',  # gerund without e
            keyword_lower + 'er',  # comparative
            keyword_lower + 'est',  # superlative
        ]

        if any(var in resume_text_lower for var in variations):
            exact_matches.append(keyword)

    # Remove duplicates
    exact_matches = list(set(exact_matches))

    # Find similar matches if enabled
    similar_matches = {}
    if use_similarity:
        similar_matches = find_similar_keywords(job_keywords, resume_keywords)

    # Calculate comprehensive score
    exact_score = len(exact_matches) / len(job_keywords)

    # Similar matches get partial credit
    similar_score = 0
    total_similar_weight = 0
    for job_kw, resume_matches in similar_matches.items():
        if job_kw not in exact_matches:  # Don't double count exact matches
            # Weight by similarity (assuming average 0.8 similarity for matched keywords)
            similar_score += len(resume_matches) * 0.8
            total_similar_weight += len(resume_matches)

    # Combine scores (exact matches get full credit, similar get partial)
    total_score = (len(exact_matches) + (similar_score if total_similar_weight > 0 else 0)) / len(job_keywords)
    total_score = min(total_score, 1.0)  # Cap at 100%

    # Calculate category-wise matching
    job_categories = categorize_keywords(job_keywords)
    resume_categories = categorize_keywords(resume_keywords)

    categorized_matches = {}
    for category in job_categories:
        job_cat_keywords = job_categories[category]
        if job_cat_keywords:
            exact_cat = [kw for kw in job_cat_keywords if kw in exact_matches]
            similar_cat = {kw: matches for kw, matches in similar_matches.items() if kw in job_cat_keywords}

            if exact_cat or similar_cat:
                cat_score = (len(exact_cat) + sum(len(matches) * 0.8 for matches in similar_cat.values())) / len(job_cat_keywords)
                categorized_matches[category] = {
                    'score': min(cat_score * 100, 100.0),
                    'exact_matches': exact_cat,
                    'similar_matches': similar_cat,
                    'total_keywords': len(job_cat_keywords)
                }

    return {
        'score': total_score * 100,  # Convert to percentage
        'exact_matches': exact_matches,
        'similar_matches': similar_matches,
        'total_job_keywords': len(job_keywords),
        'matched_job_keywords': len(exact_matches) + len(similar_matches),
        'match_details': {
            'exact_count': len(exact_matches),
            'similar_count': len(similar_matches)
        },
        'categorized_matches': categorized_matches,
        'keyword_analysis': {
            'job_categories': job_categories,
            'resume_categories': resume_categories
        }
    }