import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from nltk.stem import PorterStemmer

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


def get_keywords(text: str, min_len: int = 3) -> list[str]:
    """
    Extracts keywords from a given text (e.g., a job description).
    Filters nouns, proper nouns, verbs, removes stopwords, lemmatizes, stems,
    and returns a sorted list of unique keywords.
    """
    doc = nlp(text)
    processed_tokens = []

    for token in doc:
        # Only nouns, proper nouns, and verbs of sufficient length
        if token.pos_ not in ["NOUN", "PROPN", "VERB"]:
            continue

        word = token.text.lower()
        if not word.isalnum() or len(word) < min_len:
            continue

        if word in stop_words:
            continue

        # Lemmatize
        lemma = token.lemma_.lower()

        # Stem
        stem = ps.stem(lemma)
        processed_tokens.append(stem)

    # Remove duplicates and sort
    unique_tokens = sorted(list(set(processed_tokens)))
    return unique_tokens
