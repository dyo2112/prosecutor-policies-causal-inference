"""
QUICK START GUIDE: Using the Cleaned Prosecutor Policy Data

This script demonstrates how to load and analyze the cleaned data.
"""

import pandas as pd
import numpy as np

# Load the cleaned data
df = pd.read_csv('prosecutor_policies_CLEANED.csv')

print("="*80)
print("CLEANED PROSECUTOR POLICY DATABASE - QUICK START")
print("="*80)

# Basic info
print(f"\nTotal documents: {len(df)}")
print(f"Date range: {df['year'].min():.0f} - {df['year'].max():.0f}")
print(f"Counties: {df['county'].nunique()}")

# ============================================================================
# EXAMPLE 1: Progressive vs Traditional by County
# ============================================================================
print("\n" + "="*80)
print("EXAMPLE 1: Progressive vs Traditional by County")
print("="*80)

county_ideology = df.groupby('county').agg({
    'filename': 'count',
    'is_progressive': 'sum',
    'is_traditional': 'sum',
    'ideology_score': 'mean'
}).rename(columns={'filename': 'total_docs'})

county_ideology['progressive_pct'] = (county_ideology['is_progressive'] / county_ideology['total_docs'] * 100).round(1)
county_ideology['traditional_pct'] = (county_ideology['is_traditional'] / county_ideology['total_docs'] * 100).round(1)
county_ideology['net_progressive'] = county_ideology['progressive_pct'] - county_ideology['traditional_pct']

# Filter to counties with at least 20 documents
significant_counties = county_ideology[county_ideology['total_docs'] >= 20]
significant_counties = significant_counties.sort_values('net_progressive', ascending=False)

print("\nTop 10 Most Progressive Counties (net progressive %):")
print(significant_counties[['total_docs', 'progressive_pct', 'traditional_pct', 'net_progressive']].head(10))

# ============================================================================
# EXAMPLE 2: Temporal Trends in Progressive Policies
# ============================================================================
print("\n" + "="*80)
print("EXAMPLE 2: Temporal Trends")
print("="*80)

# Group by year
yearly_trends = df.groupby('year').agg({
    'filename': 'count',
    'is_progressive': 'sum',
    'is_traditional': 'sum',
    'ideology_score': 'mean'
}).rename(columns={'filename': 'total_docs'})

yearly_trends['progressive_pct'] = (yearly_trends['is_progressive'] / yearly_trends['total_docs'] * 100).round(1)
yearly_trends['traditional_pct'] = (yearly_trends['is_traditional'] / yearly_trends['total_docs'] * 100).round(1)

print("\nProgressive Documents by Year:")
print(yearly_trends[['total_docs', 'progressive_pct', 'traditional_pct', 'ideology_score']].tail(10))

# ============================================================================
# EXAMPLE 3: Policy Positions Analysis
# ============================================================================
print("\n" + "="*80)
print("EXAMPLE 3: Policy Positions")
print("="*80)

print("\nPosition on Enhancements:")
print(df['position_on_enhancements_clean'].value_counts().head(10))

print("\nSupport for Alternatives to Incarceration:")
print(df['supports_alternatives_clean'].value_counts())

print("\nRacial Justice Emphasis:")
print(df['racial_justice_emphasis_clean'].value_counts())

# ============================================================================
# EXAMPLE 4: Extensive vs Intensive Margin Analysis
# ============================================================================
print("\n" + "="*80)
print("EXAMPLE 4: Extensive vs Intensive Margin")
print("="*80)

# Create cross-tab of extensive vs intensive margin directions
margin_crosstab = pd.crosstab(
    df['extensive_margin_direction_clean'],
    df['intensive_margin_direction_clean'],
    margins=True
)

print("\nExtensive (rows) vs Intensive (columns) Margin Directions:")
print(margin_crosstab)

# Identify documents that are lenient on both margins
both_lenient = df[
    (df['extensive_margin_direction_clean'].str.contains('lenient', case=False, na=False)) &
    (df['intensive_margin_direction_clean'].str.contains('lenient', case=False, na=False))
]

print(f"\n\nDocuments lenient on BOTH margins: {len(both_lenient)} ({len(both_lenient)/len(df)*100:.1f}%)")

# ============================================================================
# EXAMPLE 5: Filter for Specific Analysis
# ============================================================================
print("\n" + "="*80)
print("EXAMPLE 5: Filtering for Specific Research Questions")
print("="*80)

# Filter 1: Progressive policies on bail
progressive_bail = df[
    (df['is_progressive'] == 1) &
    (df['primary_topic_clean'] == 'bail')
]

print(f"\nProgressive documents on bail: {len(progressive_bail)}")
if len(progressive_bail) > 0:
    print(f"  Counties: {progressive_bail['county'].unique()[:5]}")

# Filter 2: High-impact intensive margin policies
high_impact_intensive = df[
    (df['intensive_margin_impact_clean'] == 'high_impact') &
    (df['intensive_margin_direction_clean'].str.contains('lenient', case=False, na=False))
]

print(f"\nHigh-impact lenient intensive margin policies: {len(high_impact_intensive)}")

# Filter 3: Los Angeles County progressive policies 2020+
la_recent_progressive = df[
    (df['county'] == 'Los Angeles County') &
    (df['year'] >= 2020) &
    (df['is_progressive'] == 1)
]

print(f"\nLA County progressive policies 2020+: {len(la_recent_progressive)}")

# ============================================================================
# EXAMPLE 6: Document Type Analysis
# ============================================================================
print("\n" + "="*80)
print("EXAMPLE 6: Document Types and Ideology")
print("="*80)

doc_type_ideology = df.groupby('document_type_clean').agg({
    'filename': 'count',
    'is_progressive': 'sum',
    'ideology_score': 'mean'
}).rename(columns={'filename': 'total'})

doc_type_ideology['progressive_pct'] = (doc_type_ideology['is_progressive'] / doc_type_ideology['total'] * 100).round(1)
doc_type_ideology = doc_type_ideology.sort_values('total', ascending=False)

print("\nIdeology by Document Type:")
print(doc_type_ideology[['total', 'progressive_pct', 'ideology_score']].head(10))

# ============================================================================
# TIPS FOR ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("TIPS FOR YOUR ANALYSIS")
print("="*80)

print("""
KEY VARIABLES TO USE:

Ideology Measures:
  - ideology: Categorical (clearly_progressive, leans_progressive, etc.)
  - ideology_score: Numeric (-2 to +2)
  - is_progressive: Binary (1/0)
  - is_traditional: Binary (1/0)

Policy Impact:
  - extensive_margin_direction_clean: Who enters the system
  - intensive_margin_direction_clean: Severity of treatment
  - extensive_lenient, extensive_punitive: Binary indicators
  - intensive_lenient, intensive_punitive: Binary indicators

Specific Policies:
  - position_on_enhancements_clean
  - supports_diversion_clean
  - supports_alternatives_clean
  - racial_justice_emphasis_clean

Context:
  - county: Geographic variation
  - year: Temporal trends
  - da_administration_clean: By administration
  - document_type_clean: Policy vs training vs memo
  - primary_topic_clean: Policy area

RECOMMENDED ANALYSES:

1. Time Series: Track ideology_score over time by county
2. County Comparison: Compare progressive_pct across counties
3. Policy Clustering: Group policies by topic and ideology
4. Impact Assessment: Analyze extensive vs intensive margin patterns
5. DA Administration: Compare policies by DA administration

SAMPLE REGRESSION MODELS:

Model 1: Progressive probability
  DV: is_progressive
  IV: year, county fixed effects, document_type
  
Model 2: Ideology score
  DV: ideology_score
  IV: year, county, da_administration, topic
  
Model 3: Leniency
  DV: extensive_lenient OR intensive_lenient
  IV: is_progressive, county, year, document_type
""")

print("\n" + "="*80)
print("Ready for analysis!")
print("="*80)
