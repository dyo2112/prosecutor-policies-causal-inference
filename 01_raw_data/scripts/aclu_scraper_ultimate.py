#!/usr/bin/env python3
"""
ACLU NorCal Prosecutor Policies Scraper - ULTIMATE VERSION
Properly parses the HTML structure based on actual inspection
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urljoin
import re
from pathlib import Path

class ACLUPoliciesScraper:
    def __init__(self, output_dir="aclu_prosecutor_policies"):
        self.base_url = "https://www.aclunc.org"
        self.search_url = "https://www.aclunc.org/racial-justice-act"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.documents_dir = self.output_dir / "documents"
        self.documents_dir.mkdir(exist_ok=True)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def get_page_content(self, page=0):
        """Fetch a page of results"""
        params = {
            'county': 'All',
            'document_type': '475',  # Policy or Training Materials
            'relevant_date[min]': '',
            'relevant_date[max]': '',
            'terms': '',
            'page': page
        }
        
        print(f"Fetching page {page}...")
        response = self.session.get(self.search_url, params=params)
        response.raise_for_status()
        return response.text
    
    def parse_document_entry(self, article):
        """Parse a single document entry using HTML structure"""
        metadata = {}
        
        # Get document URL from 'about' attribute
        about_url = article.get('about', '')
        metadata['document_url'] = urljoin(self.base_url, about_url) if about_url else None
        
        # Get filename from title
        title_elem = article.find('h2', class_='rja-listing-item__title')
        if title_elem:
            title_span = title_elem.find('span', class_='field--name-title')
            if title_span:
                metadata['filename'] = title_span.get_text(strip=True)
            else:
                metadata['filename'] = title_elem.get_text(strip=True)
        else:
            metadata['filename'] = 'Unknown'
        
        # Parse structured fields by field name
        fields = {
            'county': 'field--name-field-county',
            'relevant_date': 'field--name-field-relevant-date',
            'date_of_production': 'field--name-field-date-of-producti',  # Truncated in HTML
            'upload_date': 'field--name-field-upload-date',
            'source': 'field--name-field-source'
        }
        
        for key, field_class in fields.items():
            field_div = article.find('div', class_=re.compile(field_class))
            if field_div:
                # Get the field__item div which contains the actual value
                item_div = field_div.find('div', class_='field__item')
                if item_div:
                    # For date fields, look for time element
                    if 'date' in key:
                        time_elem = item_div.find('time')
                        if time_elem:
                            metadata[key] = time_elem.get_text(strip=True)
                        else:
                            metadata[key] = item_div.get_text(strip=True)
                    else:
                        metadata[key] = item_div.get_text(strip=True)
                else:
                    metadata[key] = None
            else:
                metadata[key] = None
        
        # Get download link
        download_link = article.find('a', string=re.compile(r'Download', re.I))
        if download_link and download_link.get('href'):
            metadata['download_url'] = download_link['href']
        else:
            metadata['download_url'] = None
        
        return metadata
    
    def get_total_results(self, soup):
        """Extract total number of results from the page"""
        results_text = soup.find(string=re.compile(r'Displaying.*of.*results', re.I))
        if results_text:
            match = re.search(r'of\s+([\d,]+)\s+results', results_text, re.I)
            if match:
                return int(match.group(1).replace(',', ''))
        return None
    
    def scrape_all_metadata(self):
        """Scrape metadata from all pages"""
        all_metadata = []
        
        # Get first page
        first_page = self.get_page_content(page=0)
        soup = BeautifulSoup(first_page, 'html.parser')
        
        total_results = self.get_total_results(soup)
        if total_results:
            print(f"Found {total_results} total documents")
            estimated_pages = (total_results // 6) + 1
            print(f"Estimated pages: ~{estimated_pages}")
        
        page = 0
        consecutive_empty = 0
        max_empty = 3
        
        while consecutive_empty < max_empty and page < 500:
            if page > 0:
                html = self.get_page_content(page=page)
                soup = BeautifulSoup(html, 'html.parser')
            
            # Find all articles
            entries = soup.find_all('article', class_='rja-listing-item')
            
            if not entries:
                print(f"No entries found on page {page}")
                consecutive_empty += 1
                if consecutive_empty >= max_empty:
                    print(f"Stopping after {max_empty} consecutive empty pages")
                    break
                page += 1
                time.sleep(1)
                continue
            
            consecutive_empty = 0
            print(f"Found {len(entries)} entries on page {page}")
            
            for entry in entries:
                metadata = self.parse_document_entry(entry)
                if metadata.get('filename'):
                    all_metadata.append(metadata)
            
            page += 1
            time.sleep(1)  # Rate limiting
        
        print(f"\nTotal metadata entries collected: {len(all_metadata)}")
        return all_metadata
    
    def download_document(self, url, filename):
        """Download a single document"""
        if not url:
            return False
        
        try:
            # Clean filename
            safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            if not any(safe_filename.lower().endswith(ext) for ext in ['.pdf', '.xlsx', '.xls', '.docx', '.doc', '.csv']):
                # Add extension if missing
                if 'drive.google.com' in url:
                    safe_filename += '.pdf'  # Google Drive files are usually PDFs
                else:
                    safe_filename += '.pdf'
            
            filepath = self.documents_dir / safe_filename
            
            if filepath.exists():
                print(f"  ✓ Already exists: {safe_filename}")
                return True
            
            print(f"  ↓ Downloading: {safe_filename}")
            
            # Handle Google Drive links specially
            if 'drive.google.com' in url:
                # Convert to direct download link
                if 'open?id=' in url:
                    file_id = url.split('open?id=')[1].split('&')[0]
                    url = f'https://drive.google.com/uc?export=download&id={file_id}'
                elif '/d/' in url:
                    file_id = url.split('/d/')[1].split('/')[0]
                    url = f'https://drive.google.com/uc?export=download&id={file_id}'
            
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            time.sleep(0.5)
            return True
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return False
    
    def download_all_documents(self, metadata_list):
        """Download all documents"""
        downloadable = [m for m in metadata_list if m.get('download_url')]
        print(f"\nDownloading {len(downloadable)} documents...")
        print("(This will take a while...)")
        
        for i, metadata in enumerate(downloadable, 1):
            print(f"\n[{i}/{len(downloadable)}]")
            success = self.download_document(
                metadata.get('download_url'),
                metadata.get('filename', f'document_{i}')
            )
            metadata['download_success'] = success
        
        return metadata_list
    
    def save_metadata_csv(self, metadata_list, filename="prosecutor_policies_metadata.csv"):
        """Save metadata to CSV"""
        if not metadata_list:
            print("⚠️  No metadata to save!")
            return None
        
        df = pd.DataFrame(metadata_list)
        
        # Reorder columns
        column_order = [
            'filename', 'county', 'source', 'relevant_date', 
            'date_of_production', 'upload_date', 'document_url',
            'download_url', 'download_success'
        ]
        
        column_order = [col for col in column_order if col in df.columns]
        df = df[column_order]
        
        csv_path = self.output_dir / filename
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')  # UTF-8 with BOM for Excel
        print(f"\n✓ Metadata saved to: {csv_path}")
        
        # Print summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Total documents: {len(df)}")
        print(f"\nCounties represented: {df['county'].nunique()}")
        print(f"\nTop 10 counties:")
        print(df['county'].value_counts().head(10))
        
        if 'relevant_date' in df.columns:
            df['year'] = pd.to_datetime(df['relevant_date'], errors='coerce').dt.year
            print(f"\nDocuments by year:")
            print(df['year'].value_counts().sort_index())
        
        return df
    
    def run(self, download_files=True):
        """Main execution"""
        print("ACLU Prosecutor Policies Scraper - ULTIMATE VERSION")
        print("="*60)
        
        # Scrape metadata
        print("\n📋 Scraping metadata from all pages...")
        metadata_list = self.scrape_all_metadata()
        
        if len(metadata_list) == 0:
            print("\n❌ No documents found!")
            return None, []
        
        print(f"\n✓ Found {len(metadata_list)} documents!")
        
        # Save metadata
        print("\n💾 Saving metadata...")
        df = self.save_metadata_csv(metadata_list)
        
        # Download files
        if download_files:
            print("\n📥 Downloading files...")
            metadata_list = self.download_all_documents(metadata_list)
            self.save_metadata_csv(metadata_list)
        
        print("\n" + "="*60)
        print("✓ COMPLETE!")
        print("="*60)
        print(f"Output directory: {self.output_dir}")
        
        return df, metadata_list


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Scrape prosecutor policy documents from ACLU NorCal'
    )
    parser.add_argument(
        '--output-dir',
        default='aclu_prosecutor_policies',
        help='Output directory'
    )
    parser.add_argument(
        '--no-download',
        action='store_true',
        help='Only get metadata, skip downloading files'
    )
    
    args = parser.parse_args()
    
    scraper = ACLUPoliciesScraper(output_dir=args.output_dir)
    scraper.run(download_files=not args.no_download)


if __name__ == "__main__":
    main()
