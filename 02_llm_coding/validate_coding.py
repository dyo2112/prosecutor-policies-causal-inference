"""
Validation and Quality Control for Prosecutor Policy Coding
Checks consistency, completeness, and quality of LLM-coded documents
"""

import pandas as pd
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json


class CodingValidator:
    """Validate and analyze coded prosecutor policy documents"""
    
    def __init__(self, coded_data_file: str):
        self.df = pd.read_csv(coded_data_file)
        print(f"Loaded {len(self.df)} coded documents")
    
    def check_completeness(self):
        """Check for missing values and incomplete coding"""
        print("\n" + "="*80)
        print("COMPLETENESS CHECK")
        print("="*80)
        
        key_fields = [
            'document_type', 'primary_topic', 'extensive_margin_impact',
            'intensive_margin_impact', 'ideological_orientation', 'confidence_level'
        ]
        
        for field in key_fields:
            if field in self.df.columns:
                missing = self.df[field].isna().sum()
                pct = missing / len(self.df) * 100
                print(f"{field:30s}: {missing:4d} missing ({pct:5.1f}%)")
            else:
                print(f"{field:30s}: FIELD NOT FOUND")
        
        # Check for unclear/not_addressed values
        print("\n'Unclear' or 'Not Addressed' Responses:")
        for field in key_fields:
            if field in self.df.columns:
                unclear = self.df[field].astype(str).str.contains(
                    'unclear|not_addressed', case=False, na=False
                ).sum()
                pct = unclear / len(self.df) * 100
                print(f"{field:30s}: {unclear:4d} unclear ({pct:5.1f}%)")
    
    def analyze_distributions(self):
        """Analyze distributions of key variables"""
        print("\n" + "="*80)
        print("DISTRIBUTION ANALYSIS")
        print("="*80)
        
        categorical_vars = {
            'document_type': 'Document Type',
            'primary_topic': 'Primary Topic',
            'ideological_orientation': 'Ideological Orientation',
            'extensive_margin_direction': 'Extensive Margin Direction',
            'intensive_margin_direction': 'Intensive Margin Direction',
            'confidence_level': 'Confidence Level'
        }
        
        for var, label in categorical_vars.items():
            if var in self.df.columns:
                print(f"\n{label}:")
                counts = self.df[var].value_counts()
                for val, count in counts.items():
                    pct = count / len(self.df) * 100
                    print(f"  {str(val):30s}: {count:4d} ({pct:5.1f}%)")
    
    def check_consistency(self):
        """Check for logical inconsistencies in coding"""
        print("\n" + "="*80)
        print("CONSISTENCY CHECKS")
        print("="*80)
        
        issues = []
        
        # Check 1: Progressive orientation but traditional indicators
        if 'ideological_orientation' in self.df.columns and 'traditional_indicators' in self.df.columns:
            progressive = self.df['ideological_orientation'].str.contains('progressive', case=False, na=False)
            has_traditional = self.df['traditional_indicators'].notna() & (self.df['traditional_indicators'].astype(str) != '[]')
            
            inconsistent = progressive & has_traditional
            print(f"Progressive orientation with traditional indicators: {inconsistent.sum()}")
            issues.extend(self.df[inconsistent]['filename'].tolist())
        
        # Check 2: High confidence but many unclear fields
        if 'confidence_level' in self.df.columns:
            high_conf = self.df['confidence_level'] == 'high'
            unclear_count = self.df.apply(
                lambda row: sum([str(v).lower() in ['unclear', 'not_addressed'] 
                               for v in row.values]), axis=1
            )
            inconsistent = high_conf & (unclear_count >= 3)
            print(f"High confidence but 3+ unclear fields: {inconsistent.sum()}")
            issues.extend(self.df[inconsistent]['filename'].tolist())
        
        # Check 3: Impact coded but direction is not_applicable
        for margin in ['extensive', 'intensive']:
            impact = f'{margin}_margin_impact'
            direction = f'{margin}_margin_direction'
            
            if impact in self.df.columns and direction in self.df.columns:
                has_impact = self.df[impact].isin(['high_impact', 'moderate_impact'])
                no_direction = self.df[direction].isin(['not_applicable', 'unclear'])
                
                inconsistent = has_impact & no_direction
                print(f"{margin.title()} impact but no direction: {inconsistent.sum()}")
                issues.extend(self.df[inconsistent]['filename'].tolist())
        
        if issues:
            print(f"\nTotal documents with potential issues: {len(set(issues))}")
            print("Sample flagged documents:")
            for doc in list(set(issues))[:5]:
                print(f"  - {doc}")
    
    def temporal_analysis(self):
        """Analyze trends over time"""
        print("\n" + "="*80)
        print("TEMPORAL ANALYSIS")
        print("="*80)
        
        if 'relevant_date' not in self.df.columns:
            print("No date information available")
            return
        
        self.df['year'] = pd.to_datetime(self.df['relevant_date'], errors='coerce').dt.year
        
        # Documents by year
        print("\nDocuments by year:")
        year_counts = self.df['year'].value_counts().sort_index()
        for year, count in year_counts.items():
            if pd.notna(year):
                print(f"  {int(year)}: {count}")
        
        # Progressive orientation over time
        if 'ideological_orientation' in self.df.columns:
            print("\nProgressive orientation by year:")
            progressive = self.df['ideological_orientation'].str.contains('progressive', case=False, na=False)
            prog_by_year = self.df[progressive].groupby('year').size()
            total_by_year = self.df.groupby('year').size()
            pct_prog = (prog_by_year / total_by_year * 100).fillna(0)
            
            for year in sorted(pct_prog.index):
                if pd.notna(year) and year >= 2015:
                    print(f"  {int(year)}: {pct_prog[year]:.1f}% progressive")
    
    def county_comparison(self):
        """Compare coding across counties"""
        print("\n" + "="*80)
        print("COUNTY COMPARISONS")
        print("="*80)
        
        if 'county' not in self.df.columns:
            print("No county information available")
            return
        
        # Top counties by document count
        print("\nTop 10 counties by document count:")
        county_counts = self.df['county'].value_counts().head(10)
        for county, count in county_counts.items():
            print(f"  {county:30s}: {count}")
        
        # Progressive orientation by county (top 10)
        if 'ideological_orientation' in self.df.columns:
            print("\nProgressive orientation by county (top 10):")
            progressive = self.df['ideological_orientation'].str.contains('progressive', case=False, na=False)
            
            top_counties = county_counts.index[:10]
            for county in top_counties:
                county_docs = self.df[self.df['county'] == county]
                n_prog = (county_docs['ideological_orientation'].str.contains(
                    'progressive', case=False, na=False)).sum()
                pct = n_prog / len(county_docs) * 100
                print(f"  {county:30s}: {n_prog:3d}/{len(county_docs):3d} ({pct:5.1f}%)")
    
    def export_summary(self, output_file: str):
        """Export summary statistics to CSV"""
        summary_stats = {}
        
        # Overall statistics
        summary_stats['total_documents'] = len(self.df)
        
        # Completeness rates
        key_fields = ['document_type', 'primary_topic', 'ideological_orientation']
        for field in key_fields:
            if field in self.df.columns:
                summary_stats[f'{field}_complete_pct'] = (1 - self.df[field].isna().sum() / len(self.df)) * 100
        
        # Ideological distribution
        if 'ideological_orientation' in self.df.columns:
            progressive = self.df['ideological_orientation'].str.contains('progressive', case=False, na=False).sum()
            traditional = self.df['ideological_orientation'].str.contains('traditional', case=False, na=False).sum()
            summary_stats['progressive_count'] = progressive
            summary_stats['traditional_count'] = traditional
            summary_stats['progressive_pct'] = progressive / len(self.df) * 100
        
        # Export
        pd.DataFrame([summary_stats]).to_csv(output_file, index=False)
        print(f"\nSummary statistics exported to {output_file}")
    
    def generate_report(self, output_dir: str = "/mnt/user-data/outputs"):
        """Generate comprehensive validation report"""
        self.check_completeness()
        self.analyze_distributions()
        self.check_consistency()
        self.temporal_analysis()
        self.county_comparison()
        
        # Export summary
        output_path = Path(output_dir) / "coding_validation_summary.csv"
        self.export_summary(str(output_path))


def main():
    """Run validation analysis"""
    
    # Load coded data
    coded_file = "/mnt/user-data/outputs/coded_prosecutor_policies.csv"
    
    validator = CodingValidator(coded_file)
    validator.generate_report()


if __name__ == "__main__":
    main()
