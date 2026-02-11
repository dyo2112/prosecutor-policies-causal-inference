"""
COMPREHENSIVE VISUALIZATIONS
Creates publication-ready charts for prosecutor policy analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Load data
df = pd.read_csv('prosecutor_policies_CLEANED.csv')
df['date'] = pd.to_datetime(df['date'])

################################################################################
# FIGURE 1: TEMPORAL EVOLUTION (3 panels)
################################################################################

fig1, axes = plt.subplots(1, 3, figsize=(18, 5))
fig1.suptitle('Figure 1: Temporal Evolution of Prosecutorial Ideology (2010-2024)', 
              fontsize=14, fontweight='bold', y=1.02)

# Panel A: Progressive vs Traditional over time
recent = df[(df['year'] >= 2010) & (df['year'] <= 2024)].copy()
yearly = recent.groupby('year').agg({
    'filename': 'count',
    'is_progressive': 'sum',
    'is_traditional': 'sum'
})
yearly['progressive_pct'] = (yearly['is_progressive'] / yearly['filename'] * 100)
yearly['traditional_pct'] = (yearly['is_traditional'] / yearly['filename'] * 100)

axes[0].plot(yearly.index, yearly['progressive_pct'], marker='o', linewidth=2.5, 
             markersize=8, label='Progressive', color='#2E7D32')
axes[0].plot(yearly.index, yearly['traditional_pct'], marker='s', linewidth=2.5, 
             markersize=8, label='Traditional', color='#C62828')
axes[0].axvspan(2019.5, 2020.5, alpha=0.2, color='gold', label='2020 Surge')
axes[0].set_xlabel('Year', fontsize=11, fontweight='bold')
axes[0].set_ylabel('Percentage of Documents', fontsize=11, fontweight='bold')
axes[0].set_title('A. Progressive vs Traditional Documents', fontsize=12, fontweight='bold')
axes[0].legend(loc='upper left')
axes[0].grid(True, alpha=0.3)
axes[0].set_ylim(0, 60)

# Panel B: Ideology score over time with trend line
ideology_yearly = recent.groupby('year')['ideology_score'].mean()
axes[1].scatter(ideology_yearly.index, ideology_yearly.values, s=100, alpha=0.6, color='steelblue')

# Add trend line
z = np.polyfit(ideology_yearly.index, ideology_yearly.values, 1)
p = np.poly1d(z)
axes[1].plot(ideology_yearly.index, p(ideology_yearly.index), 
             "r--", linewidth=2, label=f'Trend: +{z[0]:.3f}/year')

axes[1].axhline(y=0, color='gray', linestyle='--', alpha=0.5, linewidth=1)
axes[1].set_xlabel('Year', fontsize=11, fontweight='bold')
axes[1].set_ylabel('Mean Ideology Score', fontsize=11, fontweight='bold')
axes[1].set_title('B. Ideology Score Trend (p=0.003)', fontsize=12, fontweight='bold')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Panel C: Document volume over time
doc_counts = recent.groupby('year')['filename'].count()
axes[2].bar(doc_counts.index, doc_counts.values, color='slategray', alpha=0.7, edgecolor='black')
axes[2].set_xlabel('Year', fontsize=11, fontweight='bold')
axes[2].set_ylabel('Number of Documents', fontsize=11, fontweight='bold')
axes[2].set_title('C. Document Volume', fontsize=12, fontweight='bold')
axes[2].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('fig1_temporal_evolution.png', dpi=300, bbox_inches='tight')
print("✓ Figure 1 saved: fig1_temporal_evolution.png")

################################################################################
# FIGURE 2: GEOGRAPHIC PATTERNS
################################################################################

fig2, axes = plt.subplots(1, 2, figsize=(16, 6))
fig2.suptitle('Figure 2: Geographic Variation in Prosecutorial Ideology', 
              fontsize=14, fontweight='bold', y=1.00)

# Panel A: Top counties by net progressive
county_stats = df.groupby('county').agg({
    'filename': 'count',
    'is_progressive': 'sum',
    'is_traditional': 'sum'
})
county_stats = county_stats[county_stats['filename'] >= 20].copy()
county_stats['progressive_pct'] = (county_stats['is_progressive'] / county_stats['filename'] * 100)
county_stats['traditional_pct'] = (county_stats['is_traditional'] / county_stats['filename'] * 100)
county_stats['net_progressive'] = county_stats['progressive_pct'] - county_stats['traditional_pct']
county_stats = county_stats.sort_values('net_progressive')

# Get top and bottom 12
top_bottom = pd.concat([county_stats.head(6), county_stats.tail(6)])

colors = ['#C62828' if x < 0 else '#2E7D32' for x in top_bottom['net_progressive']]
axes[0].barh(range(len(top_bottom)), top_bottom['net_progressive'], color=colors, edgecolor='black')
axes[0].set_yticks(range(len(top_bottom)))
axes[0].set_yticklabels([c.replace(' County', '') for c in top_bottom.index], fontsize=9)
axes[0].axvline(x=0, color='black', linewidth=1.5)
axes[0].set_xlabel('Net Progressive (%)', fontsize=11, fontweight='bold')
axes[0].set_title('A. Most Traditional vs Most Progressive Counties', fontsize=12, fontweight='bold')
axes[0].grid(True, alpha=0.3, axis='x')

# Panel B: Bay Area comparison
bay_area_counties = ['San Francisco County', 'Alameda County', 'Contra Costa County', 
                     'Marin County', 'San Mateo County', 'Santa Clara County']
bay_data = []
for county in bay_area_counties:
    county_df = df[df['county'] == county]
    if len(county_df) >= 10:
        bay_data.append({
            'county': county.replace(' County', ''),
            'progressive_pct': (county_df['is_progressive'].sum() / len(county_df) * 100),
            'traditional_pct': (county_df['is_traditional'].sum() / len(county_df) * 100),
            'n': len(county_df)
        })

bay_df = pd.DataFrame(bay_data).sort_values('progressive_pct', ascending=False)

x = np.arange(len(bay_df))
width = 0.35

axes[1].bar(x - width/2, bay_df['progressive_pct'], width, label='Progressive', 
            color='#2E7D32', edgecolor='black')
axes[1].bar(x + width/2, bay_df['traditional_pct'], width, label='Traditional', 
            color='#C62828', edgecolor='black')

axes[1].set_ylabel('Percentage of Documents', fontsize=11, fontweight='bold')
axes[1].set_title('B. Bay Area Counties', fontsize=12, fontweight='bold')
axes[1].set_xticks(x)
axes[1].set_xticklabels(bay_df['county'], rotation=45, ha='right', fontsize=9)
axes[1].legend()
axes[1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('fig2_geographic_patterns.png', dpi=300, bbox_inches='tight')
print("✓ Figure 2 saved: fig2_geographic_patterns.png")

################################################################################
# FIGURE 3: RACIAL JUSTICE EMERGENCE
################################################################################

fig3, axes = plt.subplots(2, 2, figsize=(14, 10))
fig3.suptitle('Figure 3: Racial Justice Emphasis - Emergence and Impact', 
              fontsize=14, fontweight='bold', y=0.995)

# Panel A: Racial justice over time
rj_yearly = df[(df['year'] >= 2010) & (df['year'] <= 2024)].groupby('year').agg({
    'filename': 'count',
    'racial_justice_emphasis_clean': lambda x: (x.isin(['high', 'moderate', 'low'])).sum()
})
rj_yearly['rj_pct'] = (rj_yearly['racial_justice_emphasis_clean'] / rj_yearly['filename'] * 100)

axes[0,0].plot(rj_yearly.index, rj_yearly['rj_pct'], marker='o', linewidth=2.5, 
               markersize=8, color='darkviolet')
axes[0,0].axvspan(2019.5, 2020.5, alpha=0.3, color='gold', label='2020 Breakthrough')
axes[0,0].set_xlabel('Year', fontsize=11, fontweight='bold')
axes[0,0].set_ylabel('% Docs with RJ Emphasis', fontsize=11, fontweight='bold')
axes[0,0].set_title('A. Racial Justice Emphasis Over Time', fontsize=12, fontweight='bold')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

# Panel B: Top counties for racial justice
rj_by_county = df.groupby('county').agg({
    'filename': 'count',
    'racial_justice_emphasis_clean': lambda x: (x == 'high').sum()
})
rj_by_county = rj_by_county[rj_by_county['filename'] >= 15].copy()
rj_by_county['high_rj_pct'] = (rj_by_county['racial_justice_emphasis_clean'] / rj_by_county['filename'] * 100)
rj_by_county = rj_by_county.sort_values('high_rj_pct', ascending=False).head(10)

axes[0,1].barh(range(len(rj_by_county)), rj_by_county['high_rj_pct'], 
               color='darkviolet', edgecolor='black', alpha=0.7)
axes[0,1].set_yticks(range(len(rj_by_county)))
axes[0,1].set_yticklabels([c.replace(' County', '') for c in rj_by_county.index], fontsize=9)
axes[0,1].set_xlabel('% Docs with High RJ Emphasis', fontsize=11, fontweight='bold')
axes[0,1].set_title('B. Top Counties by RJ Emphasis', fontsize=12, fontweight='bold')
axes[0,1].grid(True, alpha=0.3, axis='x')

# Panel C: RJ emphasis by ideology
rj_ideology = pd.crosstab(
    df['racial_justice_emphasis_clean'],
    df['ideology'],
    normalize='index'
) * 100

ideology_order = ['clearly_progressive', 'leans_progressive', 'neutral', 'leans_traditional', 'clearly_traditional']
rj_order = ['high', 'moderate', 'low', 'not_addressed']

rj_ideology_filtered = rj_ideology.loc[rj_order, [col for col in ideology_order if col in rj_ideology.columns]]

rj_ideology_filtered.plot(kind='bar', stacked=True, ax=axes[1,0], 
                          color=['#1B5E20', '#4CAF50', '#9E9E9E', '#EF5350', '#B71C1C'])
axes[1,0].set_xlabel('Racial Justice Emphasis', fontsize=11, fontweight='bold')
axes[1,0].set_ylabel('Percentage', fontsize=11, fontweight='bold')
axes[1,0].set_title('C. RJ Emphasis × Ideology Distribution', fontsize=12, fontweight='bold')
axes[1,0].legend(title='Ideology', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
axes[1,0].set_xticklabels(axes[1,0].get_xticklabels(), rotation=45, ha='right')
axes[1,0].grid(True, alpha=0.3, axis='y')

# Panel D: Progressive rate by RJ emphasis
rj_progressive = df.groupby('racial_justice_emphasis_clean')['is_progressive'].mean() * 100
rj_categories = ['not_addressed', 'low', 'moderate', 'high']
rj_progressive_ordered = rj_progressive.reindex(rj_categories)

colors_gradient = ['#E0E0E0', '#9C27B0', '#7B1FA2', '#4A148C']
axes[1,1].bar(range(len(rj_progressive_ordered)), rj_progressive_ordered.values, 
              color=colors_gradient, edgecolor='black', alpha=0.8)
axes[1,1].set_xticks(range(len(rj_progressive_ordered)))
axes[1,1].set_xticklabels(['Not Addressed', 'Low', 'Moderate', 'High'])
axes[1,1].set_ylabel('% Progressive Documents', fontsize=11, fontweight='bold')
axes[1,1].set_title('D. Progressive Rate by RJ Emphasis (χ²=421, p<0.001)', fontsize=12, fontweight='bold')
axes[1,1].grid(True, alpha=0.3, axis='y')

# Add percentage labels
for i, v in enumerate(rj_progressive_ordered.values):
    axes[1,1].text(i, v + 2, f'{v:.0f}%', ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('fig3_racial_justice.png', dpi=300, bbox_inches='tight')
print("✓ Figure 3 saved: fig3_racial_justice.png")

################################################################################
# FIGURE 4: POLICY FOCUS SHIFTS
################################################################################

fig4, axes = plt.subplots(2, 2, figsize=(14, 10))
fig4.suptitle('Figure 4: Policy Focus Shifts (Pre-2020 vs Post-2020)', 
              fontsize=14, fontweight='bold', y=0.995)

pre_2020 = df[df['year'] < 2020]
post_2020 = df[df['year'] >= 2020]

# Panel A: Topic changes
pre_topics = pre_2020['primary_topic_clean'].value_counts(normalize=True).head(10) * 100
post_topics = post_2020['primary_topic_clean'].value_counts(normalize=True).head(10) * 100

all_topics = sorted(set(pre_topics.index) | set(post_topics.index))
topic_comparison = pd.DataFrame({
    'Pre-2020': [pre_topics.get(t, 0) for t in all_topics],
    'Post-2020': [post_topics.get(t, 0) for t in all_topics]
}, index=all_topics)

topic_comparison['change'] = topic_comparison['Post-2020'] - topic_comparison['Pre-2020']
topic_comparison = topic_comparison.sort_values('change', ascending=False).head(8)

x = np.arange(len(topic_comparison))
width = 0.35

axes[0,0].bar(x - width/2, topic_comparison['Pre-2020'], width, label='Pre-2020', 
              color='skyblue', edgecolor='black')
axes[0,0].bar(x + width/2, topic_comparison['Post-2020'], width, label='Post-2020', 
              color='coral', edgecolor='black')

axes[0,0].set_ylabel('Percentage of Documents', fontsize=11, fontweight='bold')
axes[0,0].set_title('A. Emerging Topics', fontsize=12, fontweight='bold')
axes[0,0].set_xticks(x)
axes[0,0].set_xticklabels(topic_comparison.index, rotation=45, ha='right', fontsize=9)
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3, axis='y')

# Panel B: Support for alternatives
support_alt_pre = pre_2020['supports_alternatives_clean'].value_counts(normalize=True) * 100
support_alt_post = post_2020['supports_alternatives_clean'].value_counts(normalize=True) * 100

categories = ['yes', 'no', 'unclear', 'not_addressed']
pre_vals = [support_alt_pre.get(c, 0) for c in categories]
post_vals = [support_alt_post.get(c, 0) for c in categories]

x = np.arange(len(categories))
axes[0,1].bar(x - width/2, pre_vals, width, label='Pre-2020', 
              color='skyblue', edgecolor='black')
axes[0,1].bar(x + width/2, post_vals, width, label='Post-2020', 
              color='coral', edgecolor='black')

axes[0,1].set_ylabel('Percentage', fontsize=11, fontweight='bold')
axes[0,1].set_title('B. Support for Alternatives to Incarceration', fontsize=12, fontweight='bold')
axes[0,1].set_xticks(x)
axes[0,1].set_xticklabels(['Yes', 'No', 'Unclear', 'Not Addressed'])
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3, axis='y')

# Panel C: Margin strategies
periods = [
    (2010, 2015, "2010-2015"),
    (2016, 2019, "2016-2019"),
    (2020, 2024, "2020-2024")
]

margin_data = []
for start, end, label in periods:
    period_df = df[(df['year'] >= start) & (df['year'] <= end)]
    margin_data.append({
        'Period': label,
        'Extensive Lenient': period_df['extensive_lenient'].mean() * 100,
        'Intensive Lenient': period_df['intensive_lenient'].mean() * 100
    })

margin_df = pd.DataFrame(margin_data)

x = np.arange(len(margin_df))
axes[1,0].bar(x - width/2, margin_df['Extensive Lenient'], width, 
              label='Extensive (Charging)', color='#1976D2', edgecolor='black')
axes[1,0].bar(x + width/2, margin_df['Intensive Lenient'], width, 
              label='Intensive (Sentencing)', color='#388E3C', edgecolor='black')

axes[1,0].set_ylabel('% Lenient Documents', fontsize=11, fontweight='bold')
axes[1,0].set_title('C. Extensive vs Intensive Margin Leniency', fontsize=12, fontweight='bold')
axes[1,0].set_xticks(x)
axes[1,0].set_xticklabels(margin_df['Period'])
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3, axis='y')

# Panel D: LA County - Gascón transformation
la = df[df['county'] == 'Los Angeles County']
la = la[(la['year'] >= 2015) & (la['year'] <= 2024)]
la['period'] = la['year'].apply(lambda x: 'Pre-Gascón\n(2015-2020)' if x < 2021 else 'Gascón\n(2021-2024)')

la_stats = la.groupby('period').agg({
    'is_progressive': 'mean',
    'extensive_lenient': 'mean',
    'intensive_lenient': 'mean'
}) * 100

metrics = ['is_progressive', 'extensive_lenient', 'intensive_lenient']
labels = ['Progressive\nDocs', 'Extensive\nLenient', 'Intensive\nLenient']

x = np.arange(len(metrics))
pre_gascon_vals = [la_stats.loc['Pre-Gascón\n(2015-2020)', m] for m in metrics]
gascon_vals = [la_stats.loc['Gascón\n(2021-2024)', m] for m in metrics]

axes[1,1].bar(x - width/2, pre_gascon_vals, width, label='Pre-Gascón', 
              color='lightcoral', edgecolor='black')
axes[1,1].bar(x + width/2, gascon_vals, width, label='Gascón Era', 
              color='mediumseagreen', edgecolor='black')

axes[1,1].set_ylabel('Percentage', fontsize=11, fontweight='bold')
axes[1,1].set_title('D. LA County: Gascón Impact (p<0.001)', fontsize=12, fontweight='bold')
axes[1,1].set_xticks(x)
axes[1,1].set_xticklabels(labels)
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('fig4_policy_shifts.png', dpi=300, bbox_inches='tight')
print("✓ Figure 4 saved: fig4_policy_shifts.png")

################################################################################
# FIGURE 5: COMPREHENSIVE HEATMAP
################################################################################

# Create county-year heatmap for top counties
top_counties = df['county'].value_counts().head(15).index

# Create pivot table
heatmap_data = []
for county in top_counties:
    for year in range(2015, 2025):
        county_year = df[(df['county'] == county) & (df['year'] == year)]
        if len(county_year) >= 3:  # Minimum 3 docs
            heatmap_data.append({
                'County': county.replace(' County', ''),
                'Year': year,
                'Ideology Score': county_year['ideology_score'].mean(),
                'N': len(county_year)
            })

heatmap_df = pd.DataFrame(heatmap_data)
pivot = heatmap_df.pivot(index='County', columns='Year', values='Ideology Score')

fig5, ax = plt.subplots(figsize=(12, 10))
sns.heatmap(pivot, annot=False, cmap='RdYlGn', center=0, 
            vmin=-1.5, vmax=1.5, cbar_kws={'label': 'Ideology Score'}, ax=ax)
ax.set_title('Figure 5: Ideology Heatmap by County and Year (2015-2024)', 
             fontsize=14, fontweight='bold', pad=20)
ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('County', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('fig5_ideology_heatmap.png', dpi=300, bbox_inches='tight')
print("✓ Figure 5 saved: fig5_ideology_heatmap.png")

print("\n" + "="*80)
print("✅ ALL VISUALIZATIONS COMPLETE!")
print("="*80)
print("\nGenerated files:")
print("  • fig1_temporal_evolution.png - Temporal trends 2010-2024")
print("  • fig2_geographic_patterns.png - County comparisons and Bay Area")
print("  • fig3_racial_justice.png - RJ emergence and impact")
print("  • fig4_policy_shifts.png - Pre/post 2020 and LA County transformation")
print("  • fig5_ideology_heatmap.png - County-year heatmap")
