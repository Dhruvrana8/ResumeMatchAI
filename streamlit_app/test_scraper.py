"""
Test script for web scraper functionality
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.web_scraper import scrape_all_profiles
import json

# Test with user's URLs
linkedin_url = "https://www.linkedin.com/in/aksheysinghal/"
github_url = "https://github.com/aksheysinghal"
website_url = "https://aksheysinghal.com"

print("Testing Web Scraper...")
print("=" * 60)

results = scrape_all_profiles(
    linkedin_url=linkedin_url,
    github_url=github_url,
    website_url=website_url
)

print("\n📊 SCRAPING RESULTS:\n")
print(json.dumps(results, indent=2))

print("\n" + "=" * 60)
print("\n✅ Combined Information:")
for key, value in results['combined_info'].items():
    print(f"  {key}: {value}")
