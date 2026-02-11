#!/usr/bin/env python3
"""
Debug script to inspect a single document entry from ACLU website
Helps understand why scraper isn't working
"""

import requests
from bs4 import BeautifulSoup
import re

def inspect_single_document():
    """Fetch and inspect a single document entry"""
    
    url = "https://www.aclunc.org/racial-justice-act"
    params = {
        'county': 'All',
        'document_type': '475',
        'page': 0
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("Fetching first page...")
    response = requests.get(url, params=params, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find first article
    article = soup.find('article', class_='rja-listing-item')
    
    if not article:
        print("❌ No article found with class 'rja-listing-item'")
        return
    
    print("✓ Found article!")
    print("\n" + "="*70)
    print("ARTICLE ATTRIBUTES")
    print("="*70)
    print(f"about: {article.get('about')}")
    print(f"class: {article.get('class')}")
    
    print("\n" + "="*70)
    print("FULL ARTICLE HTML (first 1500 chars)")
    print("="*70)
    print(article.prettify()[:1500])
    
    print("\n" + "="*70)
    print("ARTICLE TEXT CONTENT")
    print("="*70)
    article_text = article.get_text('\n', strip=True)
    print(article_text[:1000])
    
    print("\n" + "="*70)
    print("EXTRACTING METADATA")
    print("="*70)
    
    # Test extraction patterns
    tests = {
        'County': r'County:?\s*([^\n]+)',
        'Relevant Date': r'Relevant Date:?\s*([^\n]+)',
        'Date of Production': r'Date of Production:?\s*([^\n]+)',
        'Upload Date': r'Upload Date:?\s*([^\n]+)',
        'Source': r'Source:?\s*([^\n]+)',
    }
    
    for field, pattern in tests.items():
        match = re.search(pattern, article_text, re.IGNORECASE)
        if match:
            print(f"✓ {field}: {match.group(1)}")
        else:
            print(f"❌ {field}: Not found")
    
    print("\n" + "="*70)
    print("LOOKING FOR LINKS")
    print("="*70)
    
    links = article.find_all('a', href=True)
    print(f"Found {len(links)} links in article:")
    for i, link in enumerate(links, 1):
        print(f"  {i}. {link.get_text(strip=True)[:50]}")
        print(f"     href: {link['href']}")
    
    print("\n" + "="*70)
    print("RECOMMENDATION")
    print("="*70)
    
    # Check if we need to visit the document page
    has_download = any('download' in link.get_text().lower() for link in links)
    has_file_link = any(re.search(r'\.(pdf|xlsx?)$', link['href'], re.I) for link in links)
    
    if has_download or has_file_link:
        print("✓ Document has direct download link in listing")
    else:
        print("⚠️  Need to visit document page to get download link")
        doc_url = article.get('about')
        if doc_url:
            print(f"   Document URL: https://www.aclunc.org{doc_url}")
            print("   The scraper will need to fetch each document page")


if __name__ == "__main__":
    inspect_single_document()
