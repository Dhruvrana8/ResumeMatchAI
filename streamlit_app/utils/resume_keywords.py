import re
import spacy
from typing import Optional, Dict, List
from spacy.lang.en import English

# Load spaCy model with NER component
nlp = spacy.load("en_core_web_sm")

# Common titles to filter out from names
NAME_TITLES = {"dr", "mr", "mrs", "ms", "miss", "prof", "professor", "sir", "madam"}

# Normalized mappings of provinces and major cities
province_in_canada = [
    "on", "qc", "bc", "ab", "mb", "ns", "nb", "nl", "pe", "sk", "nu", "yt", "nwt"
]

major_city_in_canada = {
    "on": [
        "toronto","mississauga","hamilton","brampton","thunder bay","windsor","ottawa",
        "kitchener","london","guelph","waterloo","sault ste marie","sudbury","markham",
        "vaughan","richmond","burlington","gatineau","brockville","sarnia","scarborough"
    ],
    "qc": ["montreal","quebec city","sherbrooke","laval","trois-rivieres","lachine"],
    "bc": ["vancouver","burnaby","langley","surrey","richmond","saanich","sooke","duncan","nanaimo","port coquitlam"],
    "ab": ["calgary","edmonton","red deer","lethbridge","medicine hat","airdrie","okotoks","camrose","st. albert","fort mcmurray"],
    "mb": ["winnipeg","brandon","regina","saskatoon","morden","portage la prairie","selkirk","dauphin","steinbach","winkler"],
    "ns": ["halifax","truro","new glasgow","pictou","antigonish","sydney","inverness","wolfville","shelburne","cape breton"],
    "nb": ["fredericton","moncton","saint john","dartmouth","sackville"],
    "nl": ["st john's","happy valley","newfoundland"],
    "pe": ["charlottetown","summerside","cardigan","cumberland","greenwood","new glasgow"],
    "sk": ["saskatoon","regina","moose jaw"],
    "nu": ["iqaluit","rankin inlet","cambridge bay"],
    "yt": ["whitehorse","dawson city","haines"],
    "nwt": ["yellowknife","inuvik","tuktoyaktuk"]
}

# Improved phone regex - handles more formats including international
phone_regex = re.compile(
    r'(?:\+?\d{1,3}[-.\s]?)?'  # Optional country code
    r'(?:\(?\d{1,4}\)?[-.\s]?)'  # Optional area code with parentheses
    r'(?:\d{1,4}[-.\s]?)'  # First part
    r'(?:\d{1,4}[-.\s]?)'  # Second part
    r'(?:\d{1,9})'  # Last part
    r'(?:\s*(?:ext|extension|x|#)\s*\d{1,6})?',  # Optional extension
    re.IGNORECASE
)

# Email regex - more comprehensive
email_regex = re.compile(
    r'\b[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?@[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}\b'
)

def _is_valid_name(name: str) -> bool:
    """Validate if a string looks like a real name."""
    if not name or len(name) < 2:
        return False
    
    words = name.split()
    # Filter out titles
    words = [w for w in words if w.lower() not in NAME_TITLES]
    
    if len(words) < 2 or len(words) > 5:  # Typically 2-5 words (first, middle, last, etc.)
        return False
    
    # Check if all words start with capital letter (common name pattern)
    # Allow for names like "Mary-Jane" or "O'Brien"
    for word in words:
        if not word[0].isupper():
            return False
        # Check for valid name characters (letters, hyphens, apostrophes)
        if not re.match(r"^[A-Za-z'-]+$", word):
            return False
    
    # Filter out common false positives
    false_positives = {"email", "phone", "address", "resume", "cv", "linkedin", "github"}
    if any(word.lower() in false_positives for word in words):
        return False
    
    return True

def _extract_name_from_text(text: str, doc) -> Optional[str]:
    """Extract name using multiple strategies."""
    if not text or not text.strip():
        return None
    
    # Strategy 1: Use spaCy PERSON entities (most reliable)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text.strip()
            if _is_valid_name(name):
                return name
    
    # Strategy 2: Check first few lines (resume headers)
    # Handle both newline-separated and space-separated text
    lines = text.split('\n')[:10]  # Check first 10 lines
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if line looks like a name
        words = line.split()
        if 2 <= len(words) <= 5:
            # Check if all words are capitalized and look like names
            if all(word and word[0].isupper() for word in words):
                # Filter out titles
                filtered_words = [w for w in words if w.lower() not in NAME_TITLES]
                if len(filtered_words) >= 2:
                    candidate = ' '.join(filtered_words)
                    if _is_valid_name(candidate):
                        return candidate
    
    # Strategy 3: Check first 200 characters (for text without newlines)
    # Names are typically at the very beginning of a resume
    first_chunk = text[:200].strip()
    # Skip common resume headers
    resume_headers = {"resume", "curriculum", "vitae", "cv", "application"}
    words = first_chunk.split()
    # Skip words that are resume headers
    start_idx = 0
    for i, word in enumerate(words[:3]):
        if word.lower() not in resume_headers:
            start_idx = i
            break
    
    if len(words) > start_idx:
        # Check first few words that are all capitalized
        name_candidates = []
        for i in range(start_idx, min(start_idx + 5, len(words))):
            if words[i] and words[i][0].isupper():
                name_candidates.append(words[i])
            else:
                break
        
        if 2 <= len(name_candidates) <= 5:
            # Filter out titles
            filtered_words = [w for w in name_candidates if w.lower() not in NAME_TITLES]
            if len(filtered_words) >= 2:
                candidate = ' '.join(filtered_words)
                if _is_valid_name(candidate):
                    return candidate
    
    # Strategy 4: Look for patterns like "Name: John Doe" or similar
    name_patterns = [
        r'(?:name|full\s+name|applicant|candidate)[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})',
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})(?:\s+email|\s+phone|\s+@|\s+\d)',
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text[:500], re.IGNORECASE)
        if match:
            candidate = match.group(1).strip()
            if _is_valid_name(candidate):
                return candidate
    
    return None

def _extract_email(text: str) -> Optional[str]:
    """Extract email address, preferring personal emails."""
    emails = email_regex.findall(text)
    
    if not emails:
        return None
    
    # Filter out emails in common false positive contexts
    valid_emails = []
    for email in emails:
        # Skip if email is part of a URL or domain reference
        if not re.search(r'\b' + re.escape(email) + r'\b', text):
            continue
        valid_emails.append(email.lower())
    
    if not valid_emails:
        return None
    
    # Prefer personal emails (not generic ones like info@, contact@, etc.)
    generic_prefixes = {"info", "contact", "support", "admin", "noreply", "no-reply"}
    personal_emails = [e for e in valid_emails if not e.split('@')[0] in generic_prefixes]
    
    return personal_emails[0] if personal_emails else valid_emails[0]

def _extract_phone(text: str) -> Optional[str]:
    """Extract phone number with better validation."""
    matches = phone_regex.finditer(text)
    phone_numbers = []
    
    for match in matches:
        phone_str = match.group(0)
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone_str)
        
        # Validate phone number length (7-15 digits is typical)
        digit_count = len(re.sub(r'[^\d]', '', cleaned))
        if 7 <= digit_count <= 15:
            phone_numbers.append(cleaned)
    
    # Remove duplicates
    seen = set()
    unique_phones = []
    for phone in phone_numbers:
        if phone not in seen:
            seen.add(phone)
            unique_phones.append(phone)
    
    return unique_phones[0] if unique_phones else None

def _extract_location(text: str, doc) -> tuple[Optional[str], Optional[str]]:
    """Extract province and city with improved logic."""
    province = None
    major_city = None
    
    # Normalize text to lowercase words without punctuation
    words = [re.sub(r"[^\w]", "", w).lower() for w in text.split()]
    
    # Step 1: Detect province abbreviation directly
    for w in words:
        if w in province_in_canada:
            province = w
            break
    
    # Step 2: Detect city using spaCy GPE entities
    for ent in doc.ents:
        if ent.label_ == "GPE":
            city = ent.text.lower().strip()
            # Normalize city name (remove punctuation, handle variations)
            city_normalized = re.sub(r"[^\w\s]", "", city).lower()
            
            # Compare with known cities
            for prov_code, cities in major_city_in_canada.items():
                for known_city in cities:
                    known_city_normalized = re.sub(r"[^\w\s]", "", known_city).lower()
                    # Check for exact match or if known city is contained in detected city
                    if (city_normalized == known_city_normalized or 
                        known_city_normalized in city_normalized or
                        city_normalized in known_city_normalized):
                        major_city = known_city  # Use the standardized name
                        if not province:
                            province = prov_code
                        break
                if major_city:
                    break
            if major_city:
                break
    
    return province, major_city

def get_personal_info(text: str) -> Dict[str, Optional[str]]:
    """
    Extracts personal information from resume text including:
    - Name (first person name found using NER with validation)
    - Email (prefers personal emails)
    - Phone number (validates format and length)
    - Province & City (Canadian locations)
    
    Args:
        text: Resume text content
        
    Returns:
        Dictionary with keys: name, email, phone_number, province, major_city
    """
    if not text or not text.strip():
        return {
            "name": None,
            "email": None,
            "phone_number": None,
            "province": None,
            "major_city": None
        }
    
    try:
        # Process text once with spaCy
        doc = nlp(text)
        
        # Extract all information
        name = _extract_name_from_text(text, doc)
        email = _extract_email(text)
        phone_number = _extract_phone(text)
        province, major_city = _extract_location(text, doc)
        
        return {
            "name": name,
            "email": email,
            "phone_number": phone_number,
            "province": province,
            "major_city": major_city
        }
    except Exception as e:
        # Log error in production, but return empty dict for now
        print(f"Error extracting personal info: {e}")
        return {
            "name": None,
            "email": None,
            "phone_number": None,
            "province": None,
            "major_city": None
        }


def get_websites(text: str) -> list[str]:
    """
    Extracts all website URLs from resume text.
    Returns a list of unique website URLs found.
    """
    # Pattern to match URLs (http, https, www, or domain patterns)
    url_pattern = re.compile(
        r'(?:https?://|www\.)?'  # Optional protocol or www
        r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+'  # Domain name
        r'[a-zA-Z]{2,}'  # TLD
        r'(?:/[^\s]*)?',  # Optional path
        re.IGNORECASE
    )
    
    # Find all URLs
    urls = url_pattern.findall(text)
    
    # Clean and normalize URLs
    cleaned_urls = []
    for url in urls:
        url = url.strip().rstrip('.,;:!?)')  # Remove trailing punctuation
        # Add https:// if no protocol specified
        if not url.startswith(('http://', 'https://')):
            if url.startswith('www.'):
                url = 'https://' + url
            else:
                url = 'https://' + url
        cleaned_urls.append(url)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_urls = []
    for url in cleaned_urls:
        if url.lower() not in seen:
            seen.add(url.lower())
            unique_urls.append(url)
    
    return unique_urls


def _extract_company_name(text: str, doc) -> Optional[str]:
    """Extract company name from job description."""
    if not text or not text.strip():
        return None
    
    # Strategy 1: Look for ORG entities from spaCy
    for ent in doc.ents:
        if ent.label_ == "ORG":
            company = ent.text.strip()
            # Filter out common false positives
            false_positives = {"inc", "llc", "ltd", "corp", "company", "corporation"}
            if company.lower() not in false_positives and len(company) > 2:
                return company
    
    # Strategy 2: Look for patterns like "at [Company]", "with [Company]", "[Company] is hiring"
    company_patterns = [
        r'(?:at|with|from|join|work\s+at|work\s+for)\s+([A-Z][A-Za-z0-9\s&.,-]+(?:Inc|LLC|Ltd|Corp|Corporation|Company)?)',
        r'([A-Z][A-Za-z0-9\s&.,-]+(?:Inc|LLC|Ltd|Corp|Corporation|Company)?)\s+(?:is\s+hiring|is\s+looking|seeks)',
        r'company[:\s]+([A-Z][A-Za-z0-9\s&.,-]+)',
        r'employer[:\s]+([A-Z][A-Za-z0-9\s&.,-]+)',
    ]
    
    for pattern in company_patterns:
        match = re.search(pattern, text[:1000], re.IGNORECASE)
        if match:
            company = match.group(1).strip()
            # Clean up common suffixes
            company = re.sub(r'\s+(Inc|LLC|Ltd|Corp|Corporation|Company)\.?$', '', company, flags=re.IGNORECASE)
            if len(company) > 2 and len(company) < 100:
                return company
    
    # Strategy 3: Look in first few lines for capitalized company-like names
    lines = text.split('\n')[:5]
    for line in lines:
        line = line.strip()
        # Look for lines that might contain company name
        if re.search(r'company|employer|organization', line, re.IGNORECASE):
            words = line.split()
            for i, word in enumerate(words):
                if word.lower() in ['company', 'employer', 'organization', 'org']:
                    if i > 0:
                        # Take the word before
                        candidate = words[i-1]
                        if candidate[0].isupper() and len(candidate) > 2:
                            return candidate
                    break
    
    return None


def _extract_job_position(text: str, doc) -> Optional[str]:
    """Extract job position/title from job description."""
    if not text or not text.strip():
        return None
    
    # Strategy 1: Look for common job title patterns
    job_title_patterns = [
        r'(?:position|role|title|job)[:\s]+([A-Z][A-Za-z\s-]+(?:Engineer|Developer|Manager|Analyst|Specialist|Coordinator|Director|Lead|Senior|Junior)?)',
        r'(?:we\s+are\s+hiring|looking\s+for|seeking)\s+(?:a|an)?\s*([A-Z][A-Za-z\s-]+(?:Engineer|Developer|Manager|Analyst|Specialist|Coordinator|Director|Lead|Senior|Junior)?)',
        r'^([A-Z][A-Za-z\s-]+(?:Engineer|Developer|Manager|Analyst|Specialist|Coordinator|Director|Lead|Senior|Junior)?)\s+(?:position|role|job)',
    ]
    
    for pattern in job_title_patterns:
        match = re.search(pattern, text[:500], re.IGNORECASE)
        if match:
            position = match.group(1).strip()
            # Clean up and validate
            position = re.sub(r'\s+', ' ', position)
            if 3 <= len(position) <= 80:
                return position
    
    # Strategy 2: Look in first line or first few words
    first_line = text.split('\n')[0].strip()
    first_words = first_line.split()[:5]
    if len(first_words) >= 2:
        # Check if first few words look like a job title
        candidate = ' '.join(first_words)
        if candidate[0].isupper() and any(keyword in candidate.lower() for keyword in 
            ['engineer', 'developer', 'manager', 'analyst', 'specialist', 'coordinator', 
             'director', 'lead', 'senior', 'junior', 'assistant', 'executive', 'officer']):
            return candidate
    
    return None


def _extract_job_location(text: str, doc) -> Optional[str]:
    """Extract job location from job description."""
    if not text or not text.strip():
        return None
    
    # Strategy 1: Use spaCy GPE (Geopolitical Entity) entities
    locations = []
    for ent in doc.ents:
        if ent.label_ == "GPE":
            location = ent.text.strip()
            if location and len(location) > 1:
                locations.append(location)
    
    if locations:
        # Return the first location found (usually the most relevant)
        return locations[0]
    
    # Strategy 2: Look for location patterns
    location_patterns = [
        r'(?:location|based\s+in|located\s+in|work\s+location)[:\s]+([A-Z][A-Za-z\s,]+(?:ON|QC|BC|AB|MB|NS|NB|NL|PE|SK|NU|YT|NWT|Canada|USA|United\s+States)?)',
        r'([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?),\s*(?:ON|QC|BC|AB|MB|NS|NB|NL|PE|SK|NU|YT|NWT|Canada)',
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, text[:1000], re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            if 2 <= len(location) <= 100:
                return location
    
    return None


def get_job_info(text: str) -> Dict[str, Optional[str]]:
    """
    Extracts job information from job description text including:
    - Company name
    - Position/Job title
    - Location
    - Website
    
    Args:
        text: Job description text content
        
    Returns:
        Dictionary with keys: company_name, position, location, website
    """
    if not text or not text.strip():
        return {
            "company_name": None,
            "position": None,
            "location": None,
            "website": None
        }
    
    try:
        # Process text once with spaCy
        doc = nlp(text)
        
        # Extract all information
        company_name = _extract_company_name(text, doc)
        position = _extract_job_position(text, doc)
        location = _extract_job_location(text, doc)
        
        # Extract website (reuse get_websites function)
        websites = get_websites(text)
        website = websites[0] if websites else None
        
        return {
            "company_name": company_name,
            "position": position,
            "location": location,
            "website": website
        }
    except Exception as e:
        # Log error in production, but return empty dict for now
        print(f"Error extracting job info: {e}")
        return {
            "company_name": None,
            "position": None,
            "location": None,
            "website": None
        }
