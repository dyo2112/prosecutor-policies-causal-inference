#!/usr/bin/env python3
"""
Sample analysis of ACLU prosecutor policies metadata
Demonstrates what you can learn from the metadata before even reading documents
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime

def analyze_metadata(csv_path="aclu_prosecutor_policies/prosecutor_policies_metadata.csv"):
    """Run basic analysis on the metadata"""
    
    print("="*70)
    print("ACLU Prosecutor Policies - Metadata Analysis")
    print("="*70)
    
    # Load data
    df = pd.read_csv(csv_path)
    
    print(f"\nTotal documents: {len(df)}")
    print(f"Columns: {', '.join(df.columns)}")
    
    # Basic stats
    print("\n" + "="*70)
    print("1. COVERAGE BY COUNTY")
    print("="*70)
    
    county_counts = df['county'].value_counts()
    print(f"\nNumber of counties represented: {df['county'].nunique()}")
    print(f"\nTop 10 counties by document count:")
    print(county_counts.head(10))
    
    print(f"\nCounties with only 1-2 documents:")
    sparse_counties = county_counts[county_counts <= 2]
    print(f"Count: {len(sparse_counties)}")
    if len(sparse_counties) > 0:
        print(sparse_counties)
    
    # Source analysis
    print("\n" + "="*70)
    print("2. SOURCES (Which offices provided documents)")
    print("="*70)
    
    if 'source' in df.columns:
        sources = df['source'].value_counts()
        print(f"\nTop 10 sources:")
        print(sources.head(10))
    
    # Time analysis
    print("\n" + "="*70)
    print("3. TEMPORAL ANALYSIS")
    print("="*70)
    
    # Try to parse dates
    for date_col in ['relevant_date', 'date_of_production', 'upload_date']:
        if date_col in df.columns:
            print(f"\n{date_col.replace('_', ' ').title()}:")
            try:
                df[f'{date_col}_parsed'] = pd.to_datetime(df[date_col], errors='coerce')
                valid_dates = df[f'{date_col}_parsed'].notna()
                print(f"  Valid dates: {valid_dates.sum()} ({valid_dates.sum()/len(df)*100:.1f}%)")
                
                if valid_dates.sum() > 0:
                    date_series = df.loc[valid_dates, f'{date_col}_parsed']
                    print(f"  Date range: {date_series.min().date()} to {date_series.max().date()}")
                    
                    # Year distribution
                    year_counts = date_series.dt.year.value_counts().sort_index()
                    print(f"  Documents by year:")
                    for year, count in year_counts.items():
                        print(f"    {year}: {count}")
                        
            except Exception as e:
                print(f"  Could not parse dates: {e}")
    
    # Document type analysis (from filename)
    print("\n" + "="*70)
    print("4. DOCUMENT TYPES (inferred from filenames)")
    print("="*70)
    
    if 'filename' in df.columns:
        # Infer document types from extensions
        df['extension'] = df['filename'].str.extract(r'\.([a-zA-Z0-9]+)$')[0].str.lower()
        ext_counts = df['extension'].value_counts()
        print("\nFile extensions:")
        print(ext_counts)
        
        # Look for keywords in filenames
        print("\nFilename keywords (indicating policy type):")
        keywords = ['policy', 'training', 'manual', 'guideline', 'procedure', 
                   'memo', 'directive', 'protocol', 'standard']
        for keyword in keywords:
            count = df['filename'].str.contains(keyword, case=False, na=False).sum()
            if count > 0:
                print(f"  {keyword}: {count}")
    
    # Download success rate
    print("\n" + "="*70)
    print("5. DOWNLOAD STATUS")
    print("="*70)
    
    if 'download_success' in df.columns:
        success_rate = df['download_success'].value_counts()
        print(success_rate)
        if True in success_rate.index:
            pct = success_rate[True] / len(df) * 100
            print(f"\nSuccess rate: {pct:.1f}%")
    
    # Data quality
    print("\n" + "="*70)
    print("6. DATA COMPLETENESS")
    print("="*70)
    
    for col in df.columns:
        missing = df[col].isna().sum()
        pct_missing = missing / len(df) * 100
        print(f"{col:25s}: {len(df)-missing:4d}/{len(df)} ({100-pct_missing:.1f}% complete)")
    
    return df


def create_visualizations(df, output_dir="aclu_prosecutor_policies"):
    """Create some basic visualizations"""
    
    print("\n" + "="*70)
    print("CREATING VISUALIZATIONS")
    print("="*70)
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # 1. Top counties bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    county_counts = df['county'].value_counts().head(15)
    county_counts.plot(kind='barh', ax=ax)
    ax.set_xlabel('Number of Documents')
    ax.set_title('Top 15 Counties by Document Count')
    plt.tight_layout()
    plt.savefig(output_path / 'counties_barchart.png', dpi=300, bbox_inches='tight')
    print(f"Saved: {output_path / 'counties_barchart.png'}")
    plt.close()
    
    # 2. Timeline of documents
    if 'relevant_date_parsed' in df.columns:
        fig, ax = plt.subplots(figsize=(12, 6))
        date_counts = df['relevant_date_parsed'].dt.to_period('M').value_counts().sort_index()
        date_counts = date_counts[date_counts.index.notna()]
        
        if len(date_counts) > 0:
            date_counts.plot(ax=ax)
            ax.set_xlabel('Date')
            ax.set_ylabel('Number of Documents')
            ax.set_title('Timeline of Policy Documents (by Relevant Date)')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(output_path / 'timeline.png', dpi=300, bbox_inches='tight')
            print(f"Saved: {output_path / 'timeline.png'}")
            plt.close()
    
    # 3. Heatmap of counties over time
    if 'relevant_date_parsed' in df.columns:
        df_with_dates = df[df['relevant_date_parsed'].notna()].copy()
        df_with_dates['year'] = df_with_dates['relevant_date_parsed'].dt.year
        
        # Top 20 counties
        top_counties = df['county'].value_counts().head(20).index
        df_filtered = df_with_dates[df_with_dates['county'].isin(top_counties)]
        
        if len(df_filtered) > 0:
            pivot = pd.crosstab(df_filtered['county'], df_filtered['year'])
            
            fig, ax = plt.subplots(figsize=(14, 10))
            sns.heatmap(pivot, annot=True, fmt='d', cmap='YlOrRd', ax=ax)
            ax.set_title('Document Count by County and Year (Top 20 Counties)')
            ax.set_xlabel('Year')
            ax.set_ylabel('County')
            plt.tight_layout()
            plt.savefig(output_path / 'county_year_heatmap.png', dpi=300, bbox_inches='tight')
            print(f"Saved: {output_path / 'county_year_heatmap.png'}")
            plt.close()
    
    print("\nVisualization complete!")


def main():
    """Main analysis function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze ACLU prosecutor policies metadata')
    parser.add_argument(
        '--csv',
        default='aclu_prosecutor_policies/prosecutor_policies_metadata.csv',
        help='Path to metadata CSV file'
    )
    parser.add_argument(
        '--output-dir',
        default='aclu_prosecutor_policies',
        help='Directory for output visualizations'
    )
    parser.add_argument(
        '--no-viz',
        action='store_true',
        help='Skip creating visualizations'
    )
    
    args = parser.parse_args()
    
    # Run analysis
    df = analyze_metadata(args.csv)
    
    # Create visualizations
    if not args.no_viz:
        try:
            create_visualizations(df, args.output_dir)
        except Exception as e:
            print(f"\nCould not create visualizations: {e}")
            print("Try installing matplotlib and seaborn: pip install matplotlib seaborn")


if __name__ == "__main__":
    main()
