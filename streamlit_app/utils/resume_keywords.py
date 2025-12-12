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
    """Validate if a string looks like a real name with improved accuracy."""
    if not name or len(name.strip()) < 2:
        return False

    name = name.strip()
    words = name.split()

    # Filter out titles and honorifics
    words = [w for w in words if w.lower() not in NAME_TITLES]

    if len(words) < 2 or len(words) > 5:  # Typically 2-5 words (first, middle, last, etc.)
        return False

    # Check if all words start with capital letter (common name pattern)
    # Allow for names like "Mary-Jane" or "O'Brien" or "MacDonald"
    for word in words:
        if not word[0].isupper():
            return False
        # Check for valid name characters (letters, hyphens, apostrophes, spaces)
        if not re.match(r"^[A-Za-z'-]+$", word):
            return False

    # Additional validation: check for common name patterns
    # Most names should have vowels and not be all consonants
    for word in words:
        word_lower = word.lower()
        # Skip very short words (initials like "J.")
        if len(word) <= 2:
            continue
        # Check if word has at least one vowel (except for some valid names)
        has_vowel = any(char in 'aeiou' for char in word_lower)
        if not has_vowel and word_lower not in ['by', 'my', 'fy', 'ky']:  # Some valid names without vowels
            return False

    # Filter out common false positives
    false_positives = {
        "email", "phone", "address", "resume", "cv", "linkedin", "github",
        "website", "contact", "information", "details", "profile", "summary",
        "objective", "skills", "experience", "education", "references",
        "professional", "personal", "statement", "curriculum", "vitae"
    }

    # Check individual words and the whole name
    if any(word.lower() in false_positives for word in words):
        return False

    # Check if the whole name contains false positive phrases
    name_lower = name.lower()
    false_phrases = [
        "email address", "phone number", "contact information",
        "personal information", "professional summary"
    ]
    if any(phrase in name_lower for phrase in false_phrases):
        return False

    # Additional check: names should not contain numbers or special symbols beyond hyphens/apostrophes
    if re.search(r'[0-9@#$%^&*+=]', name):
        return False

    return True

def _extract_name_from_text(text: str, doc) -> Optional[str]:
    """Extract name using multiple enhanced strategies."""
    if not text or not text.strip():
        return None

    # Strategy 1: Use spaCy PERSON entities with improved filtering
    person_entities = []
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text.strip()
            # Additional filtering for spaCy entities
            if (len(name.split()) >= 2 and
                len(name) < 50 and  # Not too long
                not re.search(r'\d', name) and  # No numbers
                _is_valid_name(name)):
                person_entities.append((name, ent.start_char))  # Keep position for ranking

    # Sort by position (prefer names that appear earlier)
    person_entities.sort(key=lambda x: x[1])
    for name, _ in person_entities:
        return name

    # Strategy 2: Enhanced first few lines check
    lines = text.split('\n')[:12]  # Check first 12 lines for better coverage
    for line in lines:
        line = line.strip()
        if not line or len(line) > 100:  # Skip very long lines
            continue

        # Check if line looks like a name (improved logic)
        words = line.split()
        if 2 <= len(words) <= 5:
            # Check if words are properly capitalized and look like names
            capitalized_words = []
            for word in words:
                if word and word[0].isupper() and re.match(r"^[A-Za-z'-]+$", word):
                    capitalized_words.append(word)

            if len(capitalized_words) >= 2:
                # Filter out titles and check remaining words
                filtered_words = [w for w in capitalized_words if w.lower() not in NAME_TITLES]
                if len(filtered_words) >= 2:
                    candidate = ' '.join(filtered_words)
                    if _is_valid_name(candidate):
                        # Additional check: ensure it's not part of a longer phrase
                        if not re.search(r'(?:email|phone|address|contact|information)', line.lower()):
                            return candidate

    # Strategy 3: Improved first chunk analysis
    first_chunk = text[:300].strip()  # Increased to 300 chars
    resume_headers = {"resume", "curriculum", "vitae", "cv", "application", "profile", "summary"}

    words = first_chunk.split()
    # Skip words that are resume headers
    start_idx = 0
    for i, word in enumerate(words[:4]):  # Check first 4 words
        if word.lower() not in resume_headers:
            start_idx = i
            break

    # Look for consecutive capitalized words
    if len(words) > start_idx:
        name_candidates = []
        consecutive_capitalized = 0

        for i in range(start_idx, min(start_idx + 6, len(words))):
            word = words[i]
            if (word and word[0].isupper() and
                re.match(r"^[A-Za-z'-]+$", word) and
                word.lower() not in NAME_TITLES):

                name_candidates.append(word)
                consecutive_capitalized += 1

                # If we hit a non-capitalized word after finding candidates, stop
                if consecutive_capitalized >= 2:
                    next_word = words[i + 1] if i + 1 < len(words) else ""
                    if next_word and not next_word[0].isupper():
                        break
            else:
                # Allow one non-name word in between (like "Dr." which we already filtered)
                if consecutive_capitalized >= 2:
                    break
                name_candidates = []
                consecutive_capitalized = 0

        if 2 <= len(name_candidates) <= 5:
            candidate = ' '.join(name_candidates)
            if _is_valid_name(candidate):
                return candidate

    # Strategy 4: Enhanced pattern matching
    name_patterns = [
        # Standard patterns
        r'(?:name|full\s+name|applicant|candidate|contact)[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})',
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})(?:\s+(?:email|phone|address|contact|@|\d))',
        # Email-like patterns but for names
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})\s*$',  # Name on its own line
        # Address-like patterns
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})(?:\s+\d+|\s+Street|\s+Avenue|\s+Road|\s+Drive)',
    ]

    for pattern in name_patterns:
        match = re.search(pattern, text[:600], re.IGNORECASE | re.MULTILINE)
        if match:
            candidate = match.group(1).strip()
            if _is_valid_name(candidate):
                return candidate

    # Strategy 5: Check for names near contact information
    contact_indicators = ['email', 'phone', 'contact', 'address', '@']
    for indicator in contact_indicators:
        indicator_pos = text.lower().find(indicator)
        if indicator_pos > 0:
            # Look backwards from contact info for a potential name
            before_indicator = text[max(0, indicator_pos - 100):indicator_pos]
            lines_before = before_indicator.split('\n')[-3:]  # Last 3 lines before contact info

            for line in reversed(lines_before):
                line = line.strip()
                if line and _is_valid_name(line):
                    return line

    return None

def _extract_email(text: str) -> Optional[str]:
    """Extract email address with improved validation and preference for personal emails."""
    emails = email_regex.findall(text)

    if not emails:
        return None

    # Clean and validate emails
    valid_emails = []
    for email in emails:
        email = email.lower().strip()

        # Skip if email is malformed or too long
        if len(email) > 100 or '@' not in email:
            continue

        # Skip obvious false positives (emails in URLs, domains without @ context, etc.)
        email_context = text[max(0, text.lower().find(email) - 20):text.lower().find(email) + len(email) + 20]
        if 'http' in email_context.lower() or 'www.' in email_context.lower():
            continue

        # Basic email format validation
        local_part, domain_part = email.split('@', 1)
        if not local_part or not domain_part or '.' not in domain_part:
            continue

        # Skip emails with invalid characters
        if re.search(r'[<>(),;\[\]]', email):
            continue

        valid_emails.append(email)

    if not valid_emails:
        return None

    # Prioritize personal/professional emails over generic ones
    generic_prefixes = {
        "info", "contact", "support", "admin", "noreply", "no-reply", "help",
        "sales", "marketing", "hello", "hi", "team", "office", "mail",
        "inquiry", "enquiry", "feedback", "service", "customer", "client"
    }

    # Also check for obviously generic domains
    generic_domains = {
        "example.com", "test.com", "domain.com", "sample.com", "yourcompany.com"
    }

    # Score emails by preference
    scored_emails = []
    for email in valid_emails:
        score = 0
        local_part = email.split('@')[0]
        domain = email.split('@')[1]

        # Prefer emails that don't have generic prefixes
        if local_part not in generic_prefixes:
            score += 2

        # Prefer emails not from generic domains
        if domain not in generic_domains:
            score += 1

        # Prefer emails that look like personal names (contain letters, not just numbers)
        if re.search(r'[a-z]{2,}', local_part):
            score += 1

        scored_emails.append((email, score))

    # Sort by score (highest first) and return the best one
    scored_emails.sort(key=lambda x: x[1], reverse=True)
    return scored_emails[0][0]

def _extract_phone(text: str) -> Optional[str]:
    """Extract phone number with enhanced validation and formatting."""
    matches = phone_regex.finditer(text)
    phone_numbers = []

    for match in matches:
        phone_str = match.group(0).strip()

        # Skip if phone number is part of a larger URL or email
        if '@' in phone_str or 'http' in phone_str.lower():
            continue

        # Clean the phone number
        cleaned = re.sub(r'[^\d+]', '', phone_str)

        # Validate phone number
        digit_count = len(re.sub(r'[^\d]', '', cleaned))

        # More sophisticated validation
        if not (7 <= digit_count <= 15):
            continue

        # Skip obviously invalid patterns
        if cleaned.startswith('+') and len(cleaned) < 8:  # Too short for international
            continue
        if not cleaned.startswith('+') and len(cleaned) < 7:  # Too short for local
            continue

        # Skip numbers that are just extensions or too repetitive
        if re.search(r'^(\d)\1{6,}$', cleaned.replace('+', '')):  # All same digit
            continue

        phone_numbers.append(cleaned)

    # Remove duplicates and sort by length (prefer longer, more complete numbers)
    seen = set()
    unique_phones = []
    for phone in phone_numbers:
        if phone not in seen:
            seen.add(phone)
            unique_phones.append(phone)

    # Sort by preference: longer numbers first (more complete), then international format
    unique_phones.sort(key=lambda x: (len(re.sub(r'[^\d]', '', x)), x.startswith('+')), reverse=True)

    if unique_phones:
        # Format the best phone number nicely
        best_phone = unique_phones[0]
        return _format_phone_number(best_phone)

    return None

def _format_phone_number(phone: str) -> str:
    """Format phone number for better readability."""
    digits_only = re.sub(r'[^\d]', '', phone)

    if phone.startswith('+'):
        # International format - keep as is but add spaces for readability
        if len(digits_only) == 11:  # +1 XXX XXX XXXX (US)
            return f"+{digits_only[0]} {digits_only[1:4]} {digits_only[4:7]} {digits_only[7:]}"
        elif len(digits_only) == 12:  # +XX XXX XXX XXXX
            return f"+{digits_only[:2]} {digits_only[2:5]} {digits_only[5:8]} {digits_only[8:]}"
        else:
            return phone  # Keep original format for other international numbers
    else:
        # Local format
        if len(digits_only) == 10:  # XXX XXX XXXX (North American)
            return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
        elif len(digits_only) == 7:  # XXX XXXX (local)
            return f"{digits_only[:3]}-{digits_only[3:]}"
        else:
            return phone  # Keep original format

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

def _extract_professional_summary(text: str) -> Optional[str]:
    """Extract professional summary or objective from resume."""
    summary_patterns = [
        r'(?:professional summary|summary|objective|career objective|profile)[:\s]*\n?(.*?)(?:\n\n|\n[A-Z]|$)',
        r'(?:about me|personal statement)[:\s]*\n?(.*?)(?:\n\n|\n[A-Z]|$)'
    ]

    text_lower = text.lower()
    for pattern in summary_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            summary = match.group(1).strip()
            if len(summary) > 20 and len(summary) < 500:  # Reasonable length
                return summary

    return None

def _extract_work_experience(text: str) -> list[Dict]:
    """Extract work experience information."""
    experiences = []

    # Look for experience sections
    experience_patterns = [
        r'(?:experience|employment|work experience|professional experience|career history)[:\s]*\n?(.*?)(?:\n\n[A-Z]|\n[A-Z]{3,}|\Z)',
        r'(?:work history|employment history)[:\s]*\n?(.*?)(?:\n\n[A-Z]|\n[A-Z]{3,}|\Z)'
    ]

    for pattern in experience_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            exp_section = match.group(1)

            # Split into individual experiences (basic approach)
            # This could be enhanced with more sophisticated parsing
            lines = exp_section.split('\n')
            current_exp = {}

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Basic position detection
                if any(title in line.lower() for title in ['developer', 'engineer', 'manager', 'analyst', 'specialist', 'coordinator']):
                    if current_exp and current_exp.get('position'):
                        experiences.append(current_exp)
                    current_exp = {'position': line}
                elif current_exp and 'company' not in current_exp and len(line.split()) <= 5:
                    current_exp['company'] = line
                elif current_exp and 'duration' not in current_exp and any(term in line.lower() for term in ['present', 'current', '-', 'to', 'years', 'months']):
                    current_exp['duration'] = line

            if current_exp:
                experiences.append(current_exp)

            break  # Use first match

    return experiences

def _extract_education(text: str) -> list[Dict]:
    """Extract education information."""
    education_records = []

    # Look for education sections
    education_patterns = [
        r'(?:education|academic background|qualifications|degrees)[:\s]*\n?(.*?)(?:\n\n[A-Z]|\n[A-Z]{3,}|\Z)'
    ]

    for pattern in education_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            edu_section = match.group(1)

            # Split into lines and extract education info
            lines = edu_section.split('\n')
            current_edu = {}

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Basic degree detection
                if any(degree in line.lower() for degree in ['bachelor', 'master', 'phd', 'doctorate', 'associate', 'diploma', 'certificate']):
                    if current_edu and current_edu.get('degree'):
                        education_records.append(current_edu)
                    current_edu = {'degree': line}
                elif current_edu and 'institution' not in current_edu and len(line.split()) <= 6:
                    current_edu['institution'] = line
                elif current_edu and 'year' not in current_edu and re.search(r'\b(19|20)\d{2}\b', line):
                    year_match = re.search(r'\b(19|20)\d{2}\b', line)
                    if year_match:
                        current_edu['year'] = year_match.group(0)

            if current_edu:
                education_records.append(current_edu)

            break

    return education_records

def _extract_certifications(text: str) -> list[str]:
    """Extract certifications."""
    certifications = []

    cert_keywords = [
        'certified', 'certificate', 'certification', 'license', 'licensed',
        'cpa', 'cfa', 'pmp', 'aws', 'azure', 'gcp', 'cissp', 'ceh', 'comptia'
    ]

    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if any(cert in line.lower() for cert in cert_keywords):
            certifications.append(line)

    return list(set(certifications))

def _extract_projects(text: str) -> list[Dict]:
    """Extract project information."""
    projects = []

    # Look for projects section
    project_patterns = [
        r'(?:projects|personal projects|key projects)[:\s]*\n?(.*?)(?:\n\n[A-Z]|\n[A-Z]{3,}|\Z)'
    ]

    for pattern in project_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            proj_section = match.group(1)

            # Split into individual projects
            lines = proj_section.split('\n')
            current_proj = {}

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Basic project detection
                if line and not line.startswith(('•', '-', '*')) and len(line) > 10:
                    if current_proj and current_proj.get('name'):
                        projects.append(current_proj)
                    current_proj = {'name': line}
                elif current_proj and 'description' not in current_proj:
                    current_proj['description'] = line

            if current_proj:
                projects.append(current_proj)

            break

    return projects

def _extract_languages(text: str) -> list[str]:
    """Extract languages known."""
    common_languages = [
        'english', 'french', 'spanish', 'german', 'italian', 'portuguese',
        'chinese', 'mandarin', 'cantonese', 'japanese', 'korean', 'arabic',
        'hindi', 'bengali', 'russian', 'turkish', 'dutch', 'swedish', 'norwegian',
        'danish', 'finnish', 'polish', 'czech', 'hungarian', 'greek'
    ]

    text_lower = text.lower()
    found_languages = []

    for lang in common_languages:
        if lang in text_lower:
            found_languages.append(lang.title())

    return list(set(found_languages))

def _extract_achievements(text: str) -> list[str]:
    """Extract achievements and awards."""
    achievements = []

    achievement_indicators = [
        'award', 'achievement', 'accomplishment', 'recognition', 'honor',
        'prize', 'scholarship', 'dean\'s list', 'honor roll', 'magna cum laude',
        'summa cum laude', 'valedictorian', 'salutatorian'
    ]

    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if any(indicator in line.lower() for indicator in achievement_indicators):
            achievements.append(line)

    return list(set(achievements))

def get_comprehensive_resume_info(text: str) -> Dict:
    """
    Extracts comprehensive information from resume text.
    Much more detailed than the basic get_personal_info function.

    Returns:
        Dictionary with extensive resume information
    """
    if not text or not text.strip():
        return {
            "personal_info": {
                "name": None,
                "email": None,
                "phone_number": None,
                "province": None,
                "major_city": None
            },
            "professional_summary": None,
            "work_experience": [],
            "education": [],
            "certifications": [],
            "projects": [],
            "skills": [],
            "languages": [],
            "achievements": [],
            "websites": [],
            "volunteer_work": [],
            "publications": [],
            "professional_memberships": []
        }

    try:
        # Process text once with spaCy
        doc = nlp(text)

        # Extract basic personal information
        name = _extract_name_from_text(text, doc)
        email = _extract_email(text)
        phone_number = _extract_phone(text)
        province, major_city = _extract_location(text, doc)

        # Extract additional information
        professional_summary = _extract_professional_summary(text)
        work_experience = _extract_work_experience(text)
        education = _extract_education(text)
        certifications = _extract_certifications(text)
        projects = _extract_projects(text)
        languages = _extract_languages(text)
        achievements = _extract_achievements(text)
        websites = get_websites(text)

        # Extract skills (from keywords)
        from utils.keywords_extraction import get_keywords
        all_keywords = get_keywords(text)
        skills = all_keywords[:30]  # Top 30 keywords as skills

        return {
            "personal_info": {
                "name": name,
                "email": email,
                "phone_number": phone_number,
                "province": province,
                "major_city": major_city
            },
            "professional_summary": professional_summary,
            "work_experience": work_experience,
            "education": education,
            "certifications": certifications,
            "projects": projects,
            "skills": skills,
            "languages": languages,
            "achievements": achievements,
            "websites": websites,
            "volunteer_work": [],  # Could be enhanced
            "publications": [],    # Could be enhanced
            "professional_memberships": []  # Could be enhanced
        }
    except Exception as e:
        print(f"Error extracting comprehensive resume info: {e}")
        return {
            "personal_info": {
                "name": None,
                "email": None,
                "phone_number": None,
                "province": None,
                "major_city": None
            },
            "professional_summary": None,
            "work_experience": [],
            "education": [],
            "certifications": [],
            "projects": [],
            "skills": [],
            "languages": [],
            "achievements": [],
            "websites": [],
            "volunteer_work": [],
            "publications": [],
            "professional_memberships": []
        }

def get_personal_info(text: str) -> Dict[str, Optional[str]]:
    """
    Legacy function - kept for backward compatibility.
    Use get_comprehensive_resume_info() for more detailed extraction.
    """
    comprehensive = get_comprehensive_resume_info(text)
    personal = comprehensive["personal_info"]
    return {
        "name": personal["name"],
        "email": personal["email"],
        "phone_number": personal["phone_number"],
        "province": personal["province"],
        "major_city": personal["major_city"]
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


def _extract_salary_info(text: str) -> Optional[str]:
    """Extract salary information from job description."""
    salary_patterns = [
        r'\$[\d,]+(?:\.\d+)?(?:\s*[-–]\s*\$[\d,]+(?:\.\d+)?)?(?:\s*per\s+(?:year|month|hour|week|day))?',
        r'(?:salary|compensation|pay|wage)[:\s]+(?:range[:\s]+)?\$[\d,]+(?:\.\d+)?(?:\s*[-–]\s*\$[\d,]+(?:\.\d+)?)?(?:\s*per\s+(?:year|month|hour|week|day))?',
        r'(?:\$[\d,]+(?:\.\d+)?(?:\s*[-–]\s*\$[\d,]+(?:\.\d+)?)?)\s+(?:annually|monthly|hourly|weekly|daily)',
        r'(?:CAD|USD|EUR|GBP)[\s]*\$?[\d,]+(?:\.\d+)?(?:\s*[-–]\s*(?:CAD|USD|EUR|GBP)?[\s]*\$?[\d,]+(?:\.\d+)?)?',
    ]

    for pattern in salary_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()

    return None

def _extract_experience_level(text: str) -> Optional[str]:
    """Extract required experience level."""
    text_lower = text.lower()

    # Senior level indicators
    if any(term in text_lower for term in ['senior', 'sr.', 'lead', 'principal', 'architect', 'manager', 'director', '8+', '10+', 'expert']):
        return 'Senior'

    # Mid level indicators
    if any(term in text_lower for term in ['mid', 'intermediate', '3-5', '4-6', 'experienced']):
        return 'Mid-Level'

    # Junior/Entry level indicators
    if any(term in text_lower for term in ['junior', 'jr.', 'entry', 'graduate', '0-2', '1-3', 'fresher', 'intern']):
        return 'Entry/Junior'

    # Look for year ranges
    year_patterns = [
        r'(\d+)[-+]\d+\s*(?:years?|yrs?)',
        r'(\d+)\s*to\s*\d+\s*(?:years?|yrs?)',
        r'at least (\d+)\s*(?:years?|yrs?)',
        r'minimum (\d+)\s*(?:years?|yrs?)'
    ]

    for pattern in year_patterns:
        match = re.search(pattern, text_lower)
        if match:
            years = int(match.group(1))
            if years >= 7:
                return 'Senior'
            elif years >= 3:
                return 'Mid-Level'
            else:
                return 'Entry/Junior'

    return None

def _extract_work_type(text: str) -> Optional[str]:
    """Extract work type (remote, hybrid, onsite)."""
    text_lower = text.lower()

    if 'remote' in text_lower or 'work from home' in text_lower or 'wfh' in text_lower:
        return 'Remote'
    elif 'hybrid' in text_lower:
        return 'Hybrid'
    elif 'onsite' in text_lower or 'on-site' in text_lower or 'office' in text_lower:
        return 'On-site'

    return None

def _extract_employment_type(text: str) -> Optional[str]:
    """Extract employment type."""
    text_lower = text.lower()

    if 'full-time' in text_lower or 'full time' in text_lower or 'fte' in text_lower:
        return 'Full-time'
    elif 'part-time' in text_lower or 'part time' in text_lower:
        return 'Part-time'
    elif 'contract' in text_lower or 'freelance' in text_lower or 'consultant' in text_lower:
        return 'Contract'
    elif 'temporary' in text_lower or 'temp' in text_lower:
        return 'Temporary'
    elif 'internship' in text_lower or 'intern' in text_lower:
        return 'Internship'

    return None

def _extract_education_requirements(text: str) -> list[str]:
    """Extract education requirements."""
    education_keywords = [
        'bachelor', 'master', 'phd', 'doctorate', 'associate', 'diploma',
        'degree', 'certificate', 'certification', 'qualification',
        'university', 'college', 'graduate', 'undergraduate'
    ]

    text_lower = text.lower()
    found_education = []

    for keyword in education_keywords:
        if keyword in text_lower:
            found_education.append(keyword.title())

    return list(set(found_education))

def _extract_benefits(text: str) -> list[str]:
    """Extract benefits and perks."""
    benefits_keywords = [
        'health insurance', 'dental', 'vision', '401k', 'retirement',
        'vacation', 'pto', 'paid time off', 'sick leave', 'maternity',
        'paternity', 'bonus', 'stock options', 'equity', 'remote work',
        'flexible hours', 'gym membership', 'professional development',
        'training', 'conference', 'learning budget', 'home office',
        'commuter benefits', 'parking', 'catered meals', 'snacks'
    ]

    text_lower = text.lower()
    found_benefits = []

    for benefit in benefits_keywords:
        if benefit in text_lower:
            found_benefits.append(benefit.title())

    return list(set(found_benefits))

def get_comprehensive_job_info(text: str) -> Dict:
    """
    Extracts comprehensive job information from job description text.
    Much more detailed than the basic get_job_info function.

    Returns:
        Dictionary with extensive job information
    """
    if not text or not text.strip():
        return {
            "company_name": None,
            "position": None,
            "location": None,
            "website": None,
            "salary_info": None,
            "experience_level": None,
            "work_type": None,
            "employment_type": None,
            "education_requirements": [],
            "benefits": [],
            "industry": None,
            "team_size": None,
            "key_skills": [],
            "responsibilities": [],
            "application_deadline": None
        }

    try:
        # Process text once with spaCy
        doc = nlp(text)

        # Extract basic information
        company_name = _extract_company_name(text, doc)
        position = _extract_job_position(text, doc)
        location = _extract_job_location(text, doc)

        # Extract website
        websites = get_websites(text)
        website = websites[0] if websites else None

        # Extract additional information
        salary_info = _extract_salary_info(text)
        experience_level = _extract_experience_level(text)
        work_type = _extract_work_type(text)
        employment_type = _extract_employment_type(text)
        education_requirements = _extract_education_requirements(text)
        benefits = _extract_benefits(text)

        # Extract key skills (from keywords)
        from utils.keywords_extraction import get_keywords
        all_keywords = get_keywords(text)
        key_skills = all_keywords[:20]  # Top 20 keywords as skills

        # Extract responsibilities (basic for now)
        responsibilities = []
        if 'responsibilities' in text.lower():
            # Could be enhanced to extract specific responsibilities
            pass

        return {
            "company_name": company_name,
            "position": position,
            "location": location,
            "website": website,
            "salary_info": salary_info,
            "experience_level": experience_level,
            "work_type": work_type,
            "employment_type": employment_type,
            "education_requirements": education_requirements,
            "benefits": benefits,
            "industry": None,  # Could be enhanced
            "team_size": None,  # Could be enhanced
            "key_skills": key_skills,
            "responsibilities": responsibilities,
            "application_deadline": None  # Could be enhanced
        }
    except Exception as e:
        print(f"Error extracting comprehensive job info: {e}")
        return {
            "company_name": None,
            "position": None,
            "location": None,
            "website": None,
            "salary_info": None,
            "experience_level": None,
            "work_type": None,
            "employment_type": None,
            "education_requirements": [],
            "benefits": [],
            "industry": None,
            "team_size": None,
            "key_skills": [],
            "responsibilities": [],
            "application_deadline": None
        }

def get_job_info(text: str) -> Dict[str, Optional[str]]:
    """
    Legacy function - kept for backward compatibility.
    Use get_comprehensive_job_info() for more detailed extraction.
    """
    comprehensive = get_comprehensive_job_info(text)
    return {
        "company_name": comprehensive["company_name"],
        "position": comprehensive["position"],
        "location": comprehensive["location"],
        "website": comprehensive["website"]
    }
