"""
Quick Demo: Web Scraping Feature

This script demonstrates how to use the web scraping functionality
to extract personal details from URLs.
"""

from utils.web_scraper import scrape_all_profiles
import json

print("=" * 70)
print("WEB SCRAPING DEMO - ResumeMatchAI")
print("=" * 70)

# Example URLs (user's actual URLs)
linkedin_url = "https://www.linkedin.com/in/aksheysinghal/"
github_url = "https://github.com/aksheysinghal"
website_url = "https://aksheysinghal.com"

print("\n📋 URLs to scrape:")
print(f"  LinkedIn: {linkedin_url}")
print(f"  GitHub:   {github_url}")
print(f"  Website:  {website_url}")

print("\n🔍 Starting web scraping...")
print("-" * 70)

# Scrape all profiles
results = scrape_all_profiles(
    linkedin_url=linkedin_url,
    github_url=github_url,
    website_url=website_url
)

# Display results
print("\n✅ SCRAPING COMPLETE!\n")

# Show combined information
if results.get('combined_info'):
    print("📊 COMBINED INFORMATION:")
    print("-" * 70)
    for key, value in results['combined_info'].items():
        print(f"  {key.capitalize()}: {value}")
    print()

# Show GitHub results
if results.get('github'):
    print("\n🐙 GITHUB PROFILE:")
    print("-" * 70)
    github = results['github']
    if 'error' in github:
        print(f"  ❌ Error: {github['error']}")
    else:
        print(f"  Name:     {github.get('name', 'N/A')}")
        print(f"  Username: {github.get('username', 'N/A')}")
        print(f"  Bio:      {github.get('bio', 'N/A')}")
        print(f"  Location: {github.get('location', 'N/A')}")
        print(f"  Company:  {github.get('company', 'N/A')}")
        print(f"  Repos:    {github.get('public_repos', 'N/A')}")
        print(f"  Followers: {github.get('followers', 'N/A')}")

# Show LinkedIn results
if results.get('linkedin'):
    print("\n💼 LINKEDIN PROFILE:")
    print("-" * 70)
    linkedin = results['linkedin']
    if 'error' in linkedin:
        print(f"  ⚠️  {linkedin['error']}")
        if linkedin.get('note'):
            print(f"  ℹ️  {linkedin['note']}")
    else:
        print(f"  Name:     {linkedin.get('name', 'N/A')}")
        print(f"  Headline: {linkedin.get('headline', 'N/A')}")

# Show website results
if results.get('personal_website'):
    print("\n🌐 PERSONAL WEBSITE:")
    print("-" * 70)
    website = results['personal_website']
    if 'error' in website:
        print(f"  ❌ Error: {website['error']}")
    else:
        print(f"  Title: {website.get('title', 'N/A')}")
        print(f"  Name:  {website.get('name', 'N/A')}")
        print(f"  Email: {website.get('email', 'N/A')}")
        if website.get('bio'):
            print(f"  Bio:   {website['bio'][:100]}...")

print("\n" + "=" * 70)
print("✨ Demo complete! The feature is ready to use in the Streamlit app.")
print("=" * 70)
