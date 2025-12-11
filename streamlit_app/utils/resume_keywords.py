import re
import spacy
from spacy.lang.en import English

# Load spaCy model with NER component
nlp = spacy.load("en_core_web_sm")

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

# Precompile phone regex
phone_regex = re.compile(r'(\+?\d{1,2}\s?)?(\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})')

def get_personal_info(text: str) -> dict[str, any]:
    """
    Extracts personal information from resume text including:
    - Name (first person name found using NER)
    - Email
    - Phone number
    """
    doc = nlp(text)

    # ----------------- Extract Name -----------------
    # Look for PERSON entities, typically the first one is the resume owner's name
    name = None
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            # Take the first PERSON entity found (usually at the top of resume)
            name = ent.text.strip()
            break
    
    # If no PERSON entity found, try to extract from first line (common resume format)
    if not name:
        first_line = text.split('\n')[0].strip()
        # Check if first line looks like a name (2-4 words, capitalized)
        words = first_line.split()
        if 2 <= len(words) <= 4 and all(word[0].isupper() for word in words if word):
            name = first_line

    # ----------------- Extract Email -----------------
    email_match = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", doc.text)
    email = email_match[0] if email_match else None

    # ----------------- Extract Phone Numbers -----------------
    matches = phone_regex.findall(text)
    phone_number = list({re.sub(r'[^\d+]', '', m[1]) for m in matches})
    # Return first phone number as string, or None
    phone_number = phone_number[0] if phone_number else None

    # ----------------- Extract Province & City -----------------
    province = None
    major_city = None

    # Normalize text to lowercase words without punctuation
    words = [re.sub(r"[^\w]", "", w).lower() for w in text.split()]

    # ---- Step 1: Detect province abbreviation directly ----
    for w in words:
        if w in province_in_canada:
            province = w
            break

    # ---- Step 2: Detect city using spaCy GPE ----
    for ent in doc.ents:
        if ent.label_ == "GPE":
            city = ent.text.lower().strip()
            # Compare normalized city
            for prov_code, cities in major_city_in_canada.items():
                if city in [c.lower() for c in cities]:
                    major_city = city
                    # if province not found yet, infer it
                    if not province:
                        province = prov_code
                    break

    return {
        "name": name,
        "email": email,
        "phone_number": phone_number,
        "province": province,
        "major_city": major_city
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
