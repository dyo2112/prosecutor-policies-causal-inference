#!/usr/bin/env python3
"""
Selective downloader for ACLU prosecutor policies
Download only specific counties, date ranges, or keywords
"""

import pandas as pd
import requests
from pathlib import Path
import time
import re
from urllib.parse import urlparse

class SelectiveDownloader:
    def __init__(self, metadata_csv, output_dir="selected_policies"):
        self.df = pd.read_csv(metadata_csv)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.documents_dir = self.output_dir / "documents"
        self.documents_dir.mkdir(exist_ok=True)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def filter_by_counties(self, counties):
        """Filter to specific counties"""
        if isinstance(counties, str):
            counties = [counties]
        
        mask = self.df['county'].str.contains('|'.join(counties), case=False, na=False)
        filtered = self.df[mask].copy()
        print(f"Found {len(filtered)} documents from: {', '.join(counties)}")
        return filtered
    
    def filter_by_date_range(self, start_date=None, end_date=None, date_column='relevant_date'):
        """Filter by date range"""
        df_copy = self.df.copy()
        df_copy[f'{date_column}_parsed'] = pd.to_datetime(df_copy[date_column], errors='coerce')
        
        mask = df_copy[f'{date_column}_parsed'].notna()
        
        if start_date:
            start = pd.to_datetime(start_date)
            mask &= (df_copy[f'{date_column}_parsed'] >= start)
            
        if end_date:
            end = pd.to_datetime(end_date)
            mask &= (df_copy[f'{date_column}_parsed'] <= end)
        
        filtered = df_copy[mask].copy()
        print(f"Found {len(filtered)} documents in date range")
        return filtered
    
    def filter_by_keywords(self, keywords):
        """Filter by keywords in filename"""
        if isinstance(keywords, str):
            keywords = [keywords]
        
        mask = self.df['filename'].str.contains('|'.join(keywords), case=False, na=False)
        filtered = self.df[mask].copy()
        print(f"Found {len(filtered)} documents matching keywords: {', '.join(keywords)}")
        return filtered
    
    def download_document(self, url, filename):
        """Download a single document"""
        if not url or pd.isna(url):
            return False
        
        try:
            # Clean filename
            safe_filename = re.sub(r'[<>:"/\\|?*]', '_', str(filename))
            if not any(safe_filename.lower().endswith(ext) for ext in ['.pdf', '.xlsx', '.docx', '.doc']):
                ext = Path(urlparse(url).path).suffix
                if ext:
                    safe_filename += ext
                else:
                    safe_filename += '.pdf'
            
            filepath = self.documents_dir / safe_filename
            
            if filepath.exists():
                print(f"  ✓ Already downloaded: {safe_filename}")
                return True
            
            print(f"  ↓ Downloading: {safe_filename}")
            response = requests.get(url, headers=self.headers, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            time.sleep(0.5)
            return True
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return False
    
    def download_filtered(self, filtered_df):
        """Download documents from filtered dataframe"""
        print(f"\nDownloading {len(filtered_df)} documents...")
        print("="*60)
        
        success_count = 0
        for i, row in enumerate(filtered_df.itertuples(), 1):
            print(f"[{i}/{len(filtered_df)}] {row.county}")
            if self.download_document(row.download_url, row.filename):
                success_count += 1
        
        print("="*60)
        print(f"Successfully downloaded: {success_count}/{len(filtered_df)}")
        
        # Save filtered metadata
        metadata_path = self.output_dir / "selected_metadata.csv"
        filtered_df.to_csv(metadata_path, index=False)
        print(f"Metadata saved to: {metadata_path}")
        
        return success_count


def interactive_mode(downloader):
    """Interactive mode for selecting what to download"""
    
    print("\n" + "="*70)
    print("ACLU PROSECUTOR POLICIES - SELECTIVE DOWNLOADER")
    print("="*70)
    
    print(f"\nTotal documents available: {len(downloader.df)}")
    print(f"Counties represented: {downloader.df['county'].nunique()}")
    
    # Show available counties
    print("\nTop 20 counties by document count:")
    print(downloader.df['county'].value_counts().head(20))
    
    print("\n" + "="*70)
    print("FILTER OPTIONS")
    print("="*70)
    
    filtered_df = downloader.df.copy()
    
    # County filter
    county_input = input("\nEnter counties to include (comma-separated, or 'all'): ").strip()
    if county_input.lower() not in ['', 'all']:
        counties = [c.strip() for c in county_input.split(',')]
        filtered_df = downloader.filter_by_counties(counties)
    
    # Date range filter
    date_input = input("\nFilter by date range? (y/n): ").strip().lower()
    if date_input == 'y':
        start_date = input("Start date (YYYY-MM-DD or press Enter to skip): ").strip()
        end_date = input("End date (YYYY-MM-DD or press Enter to skip): ").strip()
        
        if start_date or end_date:
            filtered_df = downloader.filter_by_date_range(
                start_date if start_date else None,
                end_date if end_date else None
            )
    
    # Keyword filter
    keyword_input = input("\nFilter by keywords in filename (comma-separated, or press Enter to skip): ").strip()
    if keyword_input:
        keywords = [k.strip() for k in keyword_input.split(',')]
        filtered_df = downloader.filter_by_keywords(keywords)
    
    # Confirm and download
    print(f"\n{len(filtered_df)} documents match your filters.")
    
    if len(filtered_df) == 0:
        print("No documents found with those filters.")
        return
    
    confirm = input("Download these documents? (y/n): ").strip().lower()
    if confirm == 'y':
        downloader.download_filtered(filtered_df)
    else:
        print("Download cancelled.")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Selectively download ACLU prosecutor policies',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python selective_download.py --interactive
  
  # Download specific counties
  python selective_download.py --counties "Los Angeles,San Francisco,Alameda"
  
  # Download date range
  python selective_download.py --start-date 2020-01-01 --end-date 2023-12-31
  
  # Download with keyword filter
  python selective_download.py --keywords "policy,training"
  
  # Combine filters
  python selective_download.py --counties "Los Angeles" --start-date 2020-01-01
        """
    )
    
    parser.add_argument(
        '--csv',
        default='aclu_prosecutor_policies/prosecutor_policies_metadata.csv',
        help='Path to metadata CSV'
    )
    parser.add_argument(
        '--output-dir',
        default='selected_policies',
        help='Output directory'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    parser.add_argument(
        '--counties',
        help='Comma-separated list of counties'
    )
    parser.add_argument(
        '--start-date',
        help='Start date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--end-date',
        help='End date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--keywords',
        help='Comma-separated keywords to search in filename'
    )
    
    args = parser.parse_args()
    
    # Check if CSV exists
    if not Path(args.csv).exists():
        print(f"Error: Metadata CSV not found at {args.csv}")
        print("Run aclu_prosecutor_policies_scraper.py first to get metadata.")
        return
    
    downloader = SelectiveDownloader(args.csv, args.output_dir)
    
    if args.interactive:
        interactive_mode(downloader)
    else:
        # Command line mode
        filtered_df = downloader.df.copy()
        
        if args.counties:
            counties = [c.strip() for c in args.counties.split(',')]
            filtered_df = downloader.filter_by_counties(counties)
        
        if args.start_date or args.end_date:
            filtered_df = downloader.filter_by_date_range(
                args.start_date,
                args.end_date
            )
        
        if args.keywords:
            keywords = [k.strip() for k in args.keywords.split(',')]
            filtered_df = downloader.filter_by_keywords(keywords)
        
        if len(filtered_df) == 0:
            print("No documents match your filters.")
            return
        
        print(f"\n{len(filtered_df)} documents match your filters.")
        downloader.download_filtered(filtered_df)


if __name__ == "__main__":
    main()
