"""
Analysis of Prosecutor Policy Ideology
Explore patterns in prosecutorial orientation across time and place
Focus on extensive vs intensive margins and progressive vs traditional ideology
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

sns.set_style("whitegrid")
sns.set_palette("Set2")


class ProsecutorPolicyAnalyzer:
    """Analyze coded prosecutor policy documents"""
    
    def __init__(self, coded_data_file: str, metadata_file: str = None):
        self.df = pd.read_csv(coded_data_file)
        
        # Merge with metadata if provided
        if metadata_file:
            metadata = pd.read_csv(metadata_file)
            self.df = self.df.merge(
                metadata[['filename', 'county', 'relevant_date']], 
                on='filename', 
                how='left',
                suffixes=('', '_meta')
            )
        
        # Parse dates
        self.df['year'] = pd.to_datetime(
            self.df['relevant_date'], errors='coerce'
        ).dt.year
        
        # Create binary ideology indicators
        self.df['is_progressive'] = self.df['ideological_orientation'].str.contains(
            'progressive', case=False, na=False
        ).astype(int)
        
        self.df['is_traditional'] = self.df['ideological_orientation'].str.contains(
            'traditional', case=False, na=False
        ).astype(int)
        
        # Create margin indicators
        self.df['extensive_lenient'] = self.df['extensive_margin_direction'].str.contains(
            'lenient', case=False, na=False
        ).astype(int)
        
        self.df['intensive_lenient'] = self.df['intensive_margin_direction'].str.contains(
            'lenient', case=False, na=False
        ).astype(int)
        
        print(f"Loaded {len(self.df)} coded documents")
        print(f"Date range: {self.df['year'].min():.0f} - {self.df['year'].max():.0f}")
        print(f"Counties: {self.df['county'].nunique()}")
    
    def temporal_trends(self):
        """Analyze temporal trends in prosecutorial ideology"""
        print("\n" + "="*80)
        print("TEMPORAL TRENDS IN PROSECUTORIAL IDEOLOGY")
        print("="*80)
        
        # Focus on 2015-2021 (main period)
        df_main = self.df[(self.df['year'] >= 2015) & (self.df['year'] <= 2021)]
        
        # Progressive orientation over time
        prog_by_year = df_main.groupby('year').agg({
            'is_progressive': ['sum', 'mean', 'count']
        }).round(3)
        prog_by_year.columns = ['n_progressive', 'pct_progressive', 'total_docs']
        
        print("\nProgressive Orientation by Year (2015-2021):")
        print(prog_by_year)
        
        # Test for trend
        if len(prog_by_year) > 2:
            years = prog_by_year.index.values
            pcts = prog_by_year['pct_progressive'].values
            slope, intercept, r_value, p_value, std_err = stats.linregress(years, pcts)
            
            print(f"\nLinear trend test:")
            print(f"  Slope: {slope:.4f} (change per year)")
            print(f"  R-squared: {r_value**2:.4f}")
            print(f"  P-value: {p_value:.4f}")
        
        # Extensive vs intensive margins over time
        print("\n\nLenient Direction by Margin and Year:")
        margin_trends = df_main.groupby('year').agg({
            'extensive_lenient': 'mean',
            'intensive_lenient': 'mean'
        }).round(3)
        margin_trends.columns = ['Extensive (Lenient %)', 'Intensive (Lenient %)']
        print(margin_trends)
    
    def county_comparison(self, top_n: int = 15):
        """Compare ideology across counties"""
        print("\n" + "="*80)
        print(f"COUNTY COMPARISONS (Top {top_n} by document count)")
        print("="*80)
        
        # Get top counties
        top_counties = self.df['county'].value_counts().head(top_n).index
        df_top = self.df[self.df['county'].isin(top_counties)]
        
        # Calculate statistics by county
        county_stats = df_top.groupby('county').agg({
            'is_progressive': ['mean', 'sum', 'count'],
            'extensive_lenient': 'mean',
            'intensive_lenient': 'mean'
        }).round(3)
        
        county_stats.columns = [
            'Progressive %', 'Progressive N', 'Total Docs',
            'Extensive Lenient %', 'Intensive Lenient %'
        ]
        
        # Sort by progressive percentage
        county_stats = county_stats.sort_values('Progressive %', ascending=False)
        
        print("\nCounty Rankings (by Progressive Orientation):")
        print(county_stats)
        
        # Statistical test: difference between most and least progressive
        if len(county_stats) >= 2:
            most_prog = county_stats.index[0]
            least_prog = county_stats.index[-1]
            
            most_prog_docs = df_top[df_top['county'] == most_prog]['is_progressive']
            least_prog_docs = df_top[df_top['county'] == least_prog]['is_progressive']
            
            chi2, p_value = stats.chi2_contingency([
                [most_prog_docs.sum(), len(most_prog_docs) - most_prog_docs.sum()],
                [least_prog_docs.sum(), len(least_prog_docs) - least_prog_docs.sum()]
            ])[:2]
            
            print(f"\nDifference test ({most_prog} vs {least_prog}):")
            print(f"  Chi-square: {chi2:.2f}")
            print(f"  P-value: {p_value:.4f}")
    
    def policy_domain_analysis(self):
        """Analyze ideology by policy domain"""
        print("\n" + "="*80)
        print("IDEOLOGY BY POLICY DOMAIN")
        print("="*80)
        
        if 'primary_topic' not in self.df.columns:
            print("No primary_topic field available")
            return
        
        # Top policy domains
        top_topics = self.df['primary_topic'].value_counts().head(10).index
        
        topic_ideology = self.df[self.df['primary_topic'].isin(top_topics)].groupby('primary_topic').agg({
            'is_progressive': ['mean', 'count'],
            'extensive_lenient': 'mean',
            'intensive_lenient': 'mean'
        }).round(3)
        
        topic_ideology.columns = [
            'Progressive %', 'N Docs',
            'Extensive Lenient %', 'Intensive Lenient %'
        ]
        
        topic_ideology = topic_ideology.sort_values('Progressive %', ascending=False)
        
        print("\nTop Policy Domains by Progressive Orientation:")
        print(topic_ideology)
    
    def extensive_vs_intensive_comparison(self):
        """Compare extensive and intensive margin policies"""
        print("\n" + "="*80)
        print("EXTENSIVE VS INTENSIVE MARGIN ANALYSIS")
        print("="*80)
        
        # Overall comparison
        print("\nOverall Margin Impact:")
        print(f"  Extensive margin - High/Moderate impact: "
              f"{(self.df['extensive_margin_impact'].isin(['high_impact', 'moderate_impact']).sum() / len(self.df) * 100):.1f}%")
        print(f"  Intensive margin - High/Moderate impact: "
              f"{(self.df['intensive_margin_impact'].isin(['high_impact', 'moderate_impact']).sum() / len(self.df) * 100):.1f}%")
        
        # Direction comparison
        print("\nDirection of Policy Impact:")
        
        for margin in ['extensive', 'intensive']:
            direction_col = f'{margin}_margin_direction'
            if direction_col in self.df.columns:
                print(f"\n{margin.title()} Margin:")
                direction_counts = self.df[direction_col].value_counts()
                for val, count in direction_counts.items():
                    pct = count / len(self.df) * 100
                    print(f"  {val:20s}: {count:4d} ({pct:5.1f}%)")
        
        # Progressive ideology by margin emphasis
        print("\n\nProgressive Orientation by Margin Emphasis:")
        
        extensive_focus = self.df['extensive_margin_impact'].isin(['high_impact', 'moderate_impact'])
        intensive_focus = self.df['intensive_margin_impact'].isin(['high_impact', 'moderate_impact'])
        
        print(f"  Extensive focus: {self.df[extensive_focus]['is_progressive'].mean()*100:.1f}% progressive")
        print(f"  Intensive focus: {self.df[intensive_focus]['is_progressive'].mean()*100:.1f}% progressive")
        print(f"  Both margins: {self.df[extensive_focus & intensive_focus]['is_progressive'].mean()*100:.1f}% progressive")
    
    def regression_analysis(self):
        """Simple regression analysis of ideology predictors"""
        print("\n" + "="*80)
        print("REGRESSION ANALYSIS: PREDICTORS OF PROGRESSIVE ORIENTATION")
        print("="*80)
        
        # Prepare data
        df_reg = self.df[
            (self.df['year'] >= 2015) & 
            (self.df['year'] <= 2021)
        ].copy()
        
        # Create dummy variables for top counties
        top_counties = df_reg['county'].value_counts().head(10).index
        for county in top_counties:
            df_reg[f'county_{county.replace(" ", "_").lower()}'] = (
                df_reg['county'] == county
            ).astype(int)
        
        # Create time trend
        df_reg['year_centered'] = df_reg['year'] - 2015
        
        # Select predictors
        predictors = ['year_centered'] + [f'county_{c.replace(" ", "_").lower()}' 
                                          for c in top_counties]
        predictors = [p for p in predictors if p in df_reg.columns]
        
        # Run regression (simplified - using correlation for quick analysis)
        print("\nCorrelations with Progressive Orientation:")
        
        if 'year_centered' in df_reg.columns:
            corr_year = df_reg[['is_progressive', 'year_centered']].corr().iloc[0, 1]
            print(f"  Year (2015=0): {corr_year:.3f}")
        
        # County effects
        print("\nCounty Effects (vs. average):")
        for county in top_counties[:5]:
            county_var = f'county_{county.replace(" ", "_").lower()}'
            if county_var in df_reg.columns:
                county_mean = df_reg[df_reg[county_var] == 1]['is_progressive'].mean()
                overall_mean = df_reg['is_progressive'].mean()
                diff = county_mean - overall_mean
                print(f"  {county:30s}: {diff:+.3f}")
    
    def create_visualizations(self, output_dir: str = "/mnt/user-data/outputs"):
        """Create visualization plots"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)
        
        # Focus on main period
        df_plot = self.df[(self.df['year'] >= 2015) & (self.df['year'] <= 2021)]
        
        # 1. Progressive orientation over time
        fig, ax = plt.subplots(figsize=(10, 6))
        
        prog_by_year = df_plot.groupby('year')['is_progressive'].mean() * 100
        ax.plot(prog_by_year.index, prog_by_year.values, marker='o', linewidth=2, markersize=8)
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('% Progressive Orientation', fontsize=12)
        ax.set_title('Progressive Prosecutorial Orientation Over Time (2015-2021)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path / 'progressive_trend.png', dpi=300)
        print(f"\nSaved: {output_path / 'progressive_trend.png'}")
        plt.close()
        
        # 2. County comparison (top 10)
        top_counties = df_plot['county'].value_counts().head(10).index
        df_counties = df_plot[df_plot['county'].isin(top_counties)]
        
        county_prog = df_counties.groupby('county')['is_progressive'].mean().sort_values() * 100
        
        fig, ax = plt.subplots(figsize=(10, 8))
        county_prog.plot(kind='barh', ax=ax, color='steelblue')
        ax.set_xlabel('% Progressive Orientation', fontsize=12)
        ax.set_ylabel('')
        ax.set_title('Progressive Orientation by County (Top 10)', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path / 'county_comparison.png', dpi=300)
        print(f"Saved: {output_path / 'county_comparison.png'}")
        plt.close()
        
        # 3. Extensive vs Intensive margins
        margin_data = df_plot.groupby('year').agg({
            'extensive_lenient': 'mean',
            'intensive_lenient': 'mean'
        }) * 100
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(margin_data.index, margin_data['extensive_lenient'], 
                marker='o', label='Extensive Margin (Lenient)', linewidth=2)
        ax.plot(margin_data.index, margin_data['intensive_lenient'], 
                marker='s', label='Intensive Margin (Lenient)', linewidth=2)
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('% Lenient Direction', fontsize=12)
        ax.set_title('Policy Direction by Margin Type (2015-2021)', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path / 'margin_comparison.png', dpi=300)
        print(f"Saved: {output_path / 'margin_comparison.png'}")
        plt.close()
    
    def export_analysis_results(self, output_dir: str = "/mnt/user-data/outputs"):
        """Export analysis results to CSV files"""
        output_path = Path(output_dir)
        
        # 1. Temporal trends
        df_main = self.df[(self.df['year'] >= 2015) & (self.df['year'] <= 2021)]
        temporal = df_main.groupby('year').agg({
            'is_progressive': ['mean', 'sum', 'count'],
            'extensive_lenient': 'mean',
            'intensive_lenient': 'mean'
        })
        temporal.to_csv(output_path / 'temporal_trends.csv')
        
        # 2. County comparisons
        top_counties = self.df['county'].value_counts().head(20).index
        county_stats = self.df[self.df['county'].isin(top_counties)].groupby('county').agg({
            'is_progressive': ['mean', 'sum', 'count'],
            'extensive_lenient': 'mean',
            'intensive_lenient': 'mean'
        })
        county_stats.to_csv(output_path / 'county_comparisons.csv')
        
        print(f"\nExported analysis results to {output_path}")
    
    def run_full_analysis(self):
        """Run all analyses"""
        self.temporal_trends()
        self.county_comparison()
        self.policy_domain_analysis()
        self.extensive_vs_intensive_comparison()
        self.regression_analysis()
        self.create_visualizations()
        self.export_analysis_results()


def main():
    """Run full analysis pipeline"""
    
    coded_file = "/mnt/user-data/outputs/coded_prosecutor_policies.csv"
    metadata_file = "/mnt/user-data/uploads/prosecutor_policies_metadata.csv"
    
    analyzer = ProsecutorPolicyAnalyzer(coded_file, metadata_file)
    analyzer.run_full_analysis()


if __name__ == "__main__":
    main()
