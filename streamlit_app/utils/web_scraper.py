"""
Web Scraper for extracting personal details from LinkedIn, GitHub, and personal websites
"""

import re
import logging
import requests
from typing import Dict, Optional, Any
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time

logger = logging.getLogger(__name__)

# Request headers to avoid being blocked
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# Timeout for requests (seconds)
REQUEST_TIMEOUT = 10

def scrape_github_profile(github_url: str) -> Dict[str, Any]:
    """
    Scrape GitHub profile using GitHub API (no authentication required for public profiles)
    
    Args:
        github_url: GitHub profile URL (e.g., https://github.com/username)
    
    Returns:
        dict: Extracted profile information
    """
    try:
        # Extract username from URL
        username = github_url.rstrip('/').split('/')[-1]
        
        # Use GitHub API
        api_url = f"https://api.github.com/users/{username}"
        
        logger.info(f"Fetching GitHub profile for: {username}")
        response = requests.get(api_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            
            profile = {
                'source': 'github',
                'name': data.get('name'),
                'username': data.get('login'),
                'bio': data.get('bio'),
                'location': data.get('location'),
                'company': data.get('company'),
                'blog': data.get('blog'),
                'email': data.get('email'),
                'twitter': data.get('twitter_username'),
                'public_repos': data.get('public_repos'),
                'followers': data.get('followers'),
                'following': data.get('following'),
                'created_at': data.get('created_at'),
                'avatar_url': data.get('avatar_url'),
                'profile_url': data.get('html_url')
            }
            
            logger.info(f"Successfully scraped GitHub profile: {username}")
            return profile
        elif response.status_code == 404:
            logger.warning(f"GitHub profile not found: {username}")
            return {'error': 'Profile not found', 'source': 'github'}
        else:
            logger.error(f"GitHub API error: {response.status_code}")
            return {'error': f'API error: {response.status_code}', 'source': 'github'}
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout while fetching GitHub profile: {github_url}")
        return {'error': 'Request timeout', 'source': 'github'}
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching GitHub profile: {str(e)}")
        return {'error': f'Request failed: {str(e)}', 'source': 'github'}
    except Exception as e:
        logger.error(f"Unexpected error scraping GitHub: {str(e)}")
        return {'error': f'Unexpected error: {str(e)}', 'source': 'github'}


def scrape_linkedin_profile(linkedin_url: str) -> Dict[str, Any]:
    """
    Attempt to scrape LinkedIn profile (limited due to anti-scraping measures)
    
    Note: LinkedIn has strict anti-scraping policies. This function will attempt
    basic extraction but may not work reliably without authentication.
    
    Args:
        linkedin_url: LinkedIn profile URL
    
    Returns:
        dict: Extracted profile information (may be limited)
    """
    try:
        logger.info(f"Attempting to fetch LinkedIn profile: {linkedin_url}")
        
        # Add delay to be respectful
        time.sleep(1)
        
        response = requests.get(linkedin_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            
            profile = {
                'source': 'linkedin',
                'url': linkedin_url
            }
            
            # Try to extract basic information from meta tags
            # LinkedIn often blocks scraping, so this may return limited data
            
            # Try Open Graph tags
            og_title = soup.find('meta', property='og:title')
            if og_title:
                profile['name'] = og_title.get('content')
            
            og_description = soup.find('meta', property='og:description')
            if og_description:
                profile['headline'] = og_description.get('content')
            
            # Try to extract from title
            title_tag = soup.find('title')
            if title_tag and not profile.get('name'):
                # LinkedIn titles are usually "Name | LinkedIn"
                title_text = title_tag.text.strip()
                if '|' in title_text:
                    profile['name'] = title_text.split('|')[0].strip()
            
            # Check if we got any meaningful data
            if len(profile) <= 2:  # Only source and url
                logger.warning("LinkedIn returned limited data (likely blocked)")
                profile['error'] = 'Limited data - LinkedIn may be blocking scraping'
                profile['note'] = 'Consider using LinkedIn API or manual input'
            else:
                logger.info("Successfully extracted some LinkedIn data")
            
            return profile
            
        elif response.status_code == 999:
            logger.warning("LinkedIn blocked the request (status 999)")
            return {
                'error': 'LinkedIn blocked the request',
                'note': 'LinkedIn has anti-scraping measures. Consider using their official API.',
                'source': 'linkedin',
                'url': linkedin_url
            }
        else:
            logger.error(f"LinkedIn request failed: {response.status_code}")
            return {
                'error': f'Request failed: {response.status_code}',
                'source': 'linkedin',
                'url': linkedin_url
            }
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout while fetching LinkedIn profile: {linkedin_url}")
        return {'error': 'Request timeout', 'source': 'linkedin', 'url': linkedin_url}
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching LinkedIn profile: {str(e)}")
        return {'error': f'Request failed: {str(e)}', 'source': 'linkedin', 'url': linkedin_url}
    except Exception as e:
        logger.error(f"Unexpected error scraping LinkedIn: {str(e)}")
        return {'error': f'Unexpected error: {str(e)}', 'source': 'linkedin', 'url': linkedin_url}


def scrape_personal_website(website_url: str) -> Dict[str, Any]:
    """
    Scrape personal website for basic information
    
    Args:
        website_url: Personal website URL
    
    Returns:
        dict: Extracted information
    """
    try:
        logger.info(f"Fetching personal website: {website_url}")
        
        # Add delay to be respectful
        time.sleep(0.5)
        
        response = requests.get(website_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            
            profile = {
                'source': 'personal_website',
                'url': website_url
            }
            
            # Extract title
            title_tag = soup.find('title')
            if title_tag:
                profile['title'] = title_tag.text.strip()
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                profile['description'] = meta_desc.get('content')
            
            # Try to find name in common patterns
            # Look for h1 tags (often contains name on personal sites)
            h1_tags = soup.find_all('h1')
            if h1_tags:
                # Take the first h1 that looks like a name
                for h1 in h1_tags:
                    text = h1.text.strip()
                    if len(text.split()) >= 2 and len(text) < 50:
                        profile['name'] = text
                        break
            
            # Extract email if present
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, soup.get_text())
            if emails:
                profile['email'] = emails[0]
            
            # Extract social links
            social_links = {}
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                if 'linkedin.com' in href:
                    social_links['linkedin'] = href
                elif 'github.com' in href:
                    social_links['github'] = href
                elif 'twitter.com' in href or 'x.com' in href:
                    social_links['twitter'] = href
            
            if social_links:
                profile['social_links'] = social_links
            
            # Extract paragraphs that might be bio/about
            paragraphs = soup.find_all('p')
            bio_candidates = []
            for p in paragraphs[:5]:  # Check first 5 paragraphs
                text = p.text.strip()
                if len(text) > 50 and len(text) < 500:  # Reasonable bio length
                    bio_candidates.append(text)
            
            if bio_candidates:
                profile['bio'] = bio_candidates[0]
            
            logger.info(f"Successfully scraped personal website: {website_url}")
            return profile
            
        else:
            logger.error(f"Website request failed: {response.status_code}")
            return {
                'error': f'Request failed: {response.status_code}',
                'source': 'personal_website',
                'url': website_url
            }
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout while fetching website: {website_url}")
        return {'error': 'Request timeout', 'source': 'personal_website', 'url': website_url}
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching website: {str(e)}")
        return {'error': f'Request failed: {str(e)}', 'source': 'personal_website', 'url': website_url}
    except Exception as e:
        logger.error(f"Unexpected error scraping website: {str(e)}")
        return {'error': f'Unexpected error: {str(e)}', 'source': 'personal_website', 'url': website_url}


def scrape_all_profiles(linkedin_url: Optional[str] = None, 
                       github_url: Optional[str] = None, 
                       website_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Scrape all provided profile URLs and return combined results
    
    Args:
        linkedin_url: LinkedIn profile URL (optional)
        github_url: GitHub profile URL (optional)
        website_url: Personal website URL (optional)
    
    Returns:
        dict: Combined profile information from all sources
    """
    results = {
        'linkedin': None,
        'github': None,
        'personal_website': None,
        'combined_info': {}
    }
    
    # Scrape GitHub (most reliable)
    if github_url:
        results['github'] = scrape_github_profile(github_url)
        if results['github'] and 'error' not in results['github']:
            # Add to combined info
            if results['github'].get('name'):
                results['combined_info']['name'] = results['github']['name']
            if results['github'].get('bio'):
                results['combined_info']['bio'] = results['github']['bio']
            if results['github'].get('location'):
                results['combined_info']['location'] = results['github']['location']
            if results['github'].get('company'):
                results['combined_info']['company'] = results['github']['company']
            if results['github'].get('blog'):
                results['combined_info']['website'] = results['github']['blog']
    
    # Scrape LinkedIn (may be limited)
    if linkedin_url:
        results['linkedin'] = scrape_linkedin_profile(linkedin_url)
        if results['linkedin'] and 'error' not in results['linkedin']:
            # Add to combined info (prefer LinkedIn for professional info)
            if results['linkedin'].get('name') and not results['combined_info'].get('name'):
                results['combined_info']['name'] = results['linkedin']['name']
            if results['linkedin'].get('headline'):
                results['combined_info']['headline'] = results['linkedin']['headline']
    
    # Scrape personal website
    if website_url:
        results['personal_website'] = scrape_personal_website(website_url)
        if results['personal_website'] and 'error' not in results['personal_website']:
            # Add to combined info
            if results['personal_website'].get('name') and not results['combined_info'].get('name'):
                results['combined_info']['name'] = results['personal_website']['name']
            if results['personal_website'].get('bio') and not results['combined_info'].get('bio'):
                results['combined_info']['bio'] = results['personal_website']['bio']
            if results['personal_website'].get('email'):
                results['combined_info']['email'] = results['personal_website']['email']
    
    return results


def extract_username_from_url(url: str, platform: str) -> Optional[str]:
    """
    Extract username from social media URL
    
    Args:
        url: Social media profile URL
        platform: Platform name ('github', 'linkedin', 'twitter')
    
    Returns:
        str: Extracted username or None
    """
    try:
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        
        if platform == 'github':
            # GitHub: https://github.com/username
            return path.split('/')[0] if path else None
        elif platform == 'linkedin':
            # LinkedIn: https://www.linkedin.com/in/username
            if '/in/' in path:
                return path.split('/in/')[-1].split('/')[0]
            return None
        elif platform == 'twitter':
            # Twitter: https://twitter.com/username or https://x.com/username
            return path.split('/')[0] if path else None
        
        return None
    except Exception as e:
        logger.error(f"Error extracting username from {url}: {str(e)}")
        return None
