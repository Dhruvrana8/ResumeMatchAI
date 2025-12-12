#!/usr/bin/env python3
"""
Test script to debug keyword extraction issues.
"""

def test_keyword_extraction():
    """Test the keyword extraction function."""

    # Sample job description
    sample_jd = """
    Senior Python Developer

    We are looking for an experienced Python Developer to join our team.

    Requirements:
    - 3+ years of Python development experience
    - Strong knowledge of Django, Flask, and FastAPI
    - Experience with databases (PostgreSQL, MongoDB)
    - Familiarity with AWS or Azure cloud services
    - Git version control experience
    - Knowledge of RESTful APIs and microservices
    - Experience with Docker and containerization

    Responsibilities:
    - Develop and maintain web applications using Python
    - Collaborate with cross-functional teams
    - Write clean, efficient, and maintainable code
    - Participate in code reviews and mentoring

    Skills:
    - Python
    - Django
    - Flask
    - PostgreSQL
    - MongoDB
    - AWS
    - Docker
    - Git
    - REST APIs
    """

    print("Testing keyword extraction...")
    print("=" * 50)

    print("Input text (first 200 characters):")
    print(repr(sample_jd[:200]))
    print()

    # Test without spaCy first - just check the text processing logic
    print("Sample keywords we expect to find:")
    expected_keywords = ['python', 'developer', 'experience', 'django', 'flask', 'database', 'postgresql', 'mongodb', 'aws', 'git', 'api', 'docker', 'team', 'code', 'application']

    print(f"Expected keywords: {expected_keywords}")
    print()

    # Manual check of what should be extracted
    sample_lower = sample_jd.lower()

    found_in_text = []
    for kw in expected_keywords:
        if kw in sample_lower:
            found_in_text.append(kw)

    print(f"Keywords found in raw text: {found_in_text}")
    print(f"Coverage: {len(found_in_text)}/{len(expected_keywords)} keywords")

    # Test the enhanced matching logic manually
    print("\n" + "="*50)
    print("Testing enhanced keyword matching logic...")

    # Simulate what the enhanced matching should find
    from utils.keywords_extraction import enhanced_keyword_match_score

    # Mock job keywords (what we expect from a real job description)
    mock_job_keywords = ['python', 'developer', 'experience', 'django', 'flask', 'database', 'postgresql', 'mongodb', 'aws', 'git', 'api', 'docker', 'team', 'code', 'application']

    print(f"Mock job keywords: {mock_job_keywords}")
    print(f"Resume text contains: {len(sample_jd.split())} words")

    try:
        # Test the enhanced matching
        match_result = enhanced_keyword_match_score(mock_job_keywords, sample_jd, use_similarity=False)
        print(f"\nEnhanced matching result: {match_result}")

        print("
Keyword extraction logic validation:")
        print(f"- Total job keywords: {match_result['total_job_keywords']}")
        print(f"- Exact matches found: {match_result['exact_matches']}")
        print(f"- Match score: {match_result['score']:.1f}%")

    except Exception as e:
        print(f"Error in enhanced matching: {e}")
        import traceback
        traceback.print_exc()

    # Now try to load the actual function
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

        from utils.keywords_extraction import get_keywords

        keywords = get_keywords(sample_jd)
        print(f"\nExtracted keywords ({len(keywords)} total):")
        print(keywords[:25])  # Show first 25 keywords

        # Check if we got expected keywords (now with proper lemmatization)
        expected_lemmas = ['python', 'developer', 'experience', 'django', 'flask', 'database', 'postgresql', 'mongodb', 'aws', 'git', 'api', 'docker', 'team', 'code', 'application']
        found_expected = [kw for kw in expected_lemmas if kw in keywords]

        print(f"\nExpected keywords found: {len(found_expected)}/{len(expected_lemmas)}")
        print(f"Found: {found_expected}")
        print(f"Missing: {[kw for kw in expected_lemmas if kw not in keywords]}")

        # Show some examples of what we got
        print(f"\nFirst 15 extracted keywords: {keywords[:15]}")

    except ImportError as e:
        print(f"\nCannot import keyword extraction (missing dependencies): {e}")
        print("But based on our text analysis, the keywords should be extractable.")
    except Exception as e:
        print(f"Error during keyword extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_keyword_extraction()