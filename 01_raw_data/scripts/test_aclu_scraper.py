#!/usr/bin/env python3
"""
Test script to inspect ACLU RJA database HTML structure
Useful for debugging the main scraper
"""

import requests
from bs4 import BeautifulSoup
import json

def test_page_structure():
    """Fetch first page and inspect structure"""
    
    url = "https://www.aclunc.org/racial-justice-act"
    params = {
        'county': 'All',
        'document_type': '475',  # Policy or Training Materials
        'relevant_date[min]': '',
        'relevant_date[max]': '',
        'terms': '',
        'page': 0
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("Fetching first page...")
    response = requests.get(url, params=params, headers=headers)
    print(f"Status code: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Save raw HTML for inspection
    with open('page_source.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print("Saved raw HTML to page_source.html")
    
    # Look for common patterns
    print("\n" + "="*60)
    print("Searching for document entries...")
    print("="*60)
    
    # Try different selectors
    selectors = [
        ('div.views-row', 'Views row divs'),
        ('div.document-item', 'Document item divs'),
        ('article', 'Articles'),
        ('div.node', 'Node divs'),
        ('.view-content .views-row', 'View content rows'),
    ]
    
    for selector, description in selectors:
        elements = soup.select(selector)
        print(f"\n{description} ({selector}): {len(elements)} found")
        if elements:
            print(f"First element preview:")
            print(elements[0].prettify()[:500])
    
    # Look for pagination info
    print("\n" + "="*60)
    print("Looking for result count...")
    print("="*60)
    
    result_texts = soup.find_all(string=lambda text: text and 'result' in text.lower())
    for text in result_texts[:5]:
        print(f"  - {text.strip()}")
    
    # Look for download links
    print("\n" + "="*60)
    print("Looking for download links...")
    print("="*60)
    
    download_links = soup.find_all('a', href=lambda href: href and '.pdf' in href.lower())
    print(f"Found {len(download_links)} PDF links")
    if download_links:
        print("\nFirst 3 PDF links:")
        for link in download_links[:3]:
            print(f"  - {link.get('href')}")
            print(f"    Text: {link.get_text(strip=True)}")
    
    # Look for metadata patterns
    print("\n" + "="*60)
    print("Looking for metadata patterns...")
    print("="*60)
    
    text = soup.get_text()
    import re
    
    counties = re.findall(r'County:\s*([^\n]+)', text)
    print(f"Found {len(counties)} 'County:' mentions")
    if counties:
        print(f"Examples: {counties[:3]}")
    
    dates = re.findall(r'Relevant Date:\s*([^\n]+)', text)
    print(f"Found {len(dates)} 'Relevant Date:' mentions")
    if dates:
        print(f"Examples: {dates[:3]}")
    
    print("\n" + "="*60)
    print("Inspection complete!")
    print("Check page_source.html for full HTML structure")
    print("="*60)


if __name__ == "__main__":
    test_page_structure()
