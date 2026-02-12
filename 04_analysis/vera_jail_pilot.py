"""
Vera Jail Data x Prosecutor Policy Pilot Analysis
===================================================
Links AI-coded prosecutor policy ideology scores to Vera Institute
county-level jail population outcomes in California.

Research Question: Do counties with more progressive prosecutor policies
show lower jail populations, admissions, and racial disparities?

Author: Dvir Yogev, CLJC, UC Berkeley School of Law
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy import stats
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
POLICY_FILE  = ROOT / "05_data" / "clean" / "prosecutor_policies_CLEANED.csv"
VERA_FILE    = ROOT / "vera_jail" / "incarceration_trends_county.csv"
FIG_DIR      = ROOT / "06_figures"
RESULTS_DIR  = ROOT / "05_data" / "results"
FIG_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# ── Style ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': '#0d1117',
    'axes.facecolor':   '#161b22',
    'axes.edgecolor':   '#30363d',
    'axes.labelcolor':  '#c9d1d9',
    'text.color':       '#c9d1d9',
    'xtick.color':      '#8b949e',
    'ytick.color':      '#8b949e',
    'grid.color':       '#21262d',
    'grid.alpha':       0.6,
    'font.family':      'sans-serif',
    'font.size':        11,
    'axes.titlesize':   13,
    'axes.titleweight': 'bold',
})
ACCENT   = '#58a6ff'
ACCENT2  = '#f0883e'
ACCENT3  = '#3fb950'
ACCENT4  = '#f778ba'
NEUTRAL  = '#8b949e'

# ═══════════════════════════════════════════════════════════════════════════════
# 1.  LOAD & PREPARE DATA
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("VERA JAIL × PROSECUTOR POLICY PILOT ANALYSIS")
print("=" * 70)

# ── Policy data ──────────────────────────────────────────────────────────────
pol = pd.read_csv(POLICY_FILE)
print(f"\nPolicy data: {len(pol)} documents, {pol['county'].nunique()} counties")

# Standardise county names to match Vera (add " County")
pol['county_vera'] = pol['county'].str.strip() + " County"
# A few may already end in County – deduplicate
pol['county_vera'] = pol['county_vera'].str.replace(" County County", " County", regex=False)

# Ensure numeric year
pol['year'] = pd.to_numeric(pol['year'], errors='coerce')

# Aggregate policy scores to county-year
policy_cy = (
    pol.groupby(['county_vera', 'year'])
    .agg(
        n_docs          = ('ideology_score', 'size'),
        mean_ideology   = ('ideology_score', 'mean'),
        pct_progressive = ('is_progressive', 'mean'),
        pct_traditional = ('is_traditional', 'mean'),
        pct_ext_lenient = ('extensive_lenient', lambda x: x.mean() if 'extensive_lenient' in pol.columns else np.nan),
        pct_int_lenient = ('intensive_lenient', lambda x: x.mean() if 'intensive_lenient' in pol.columns else np.nan),
    )
    .reset_index()
)
policy_cy['pct_progressive'] *= 100
policy_cy['pct_traditional'] *= 100
policy_cy['pct_ext_lenient'] *= 100
policy_cy['pct_int_lenient'] *= 100

# ── Vera data (annual averages for CA) ───────────────────────────────────────
vera_cols = [
    'year', 'quarter', 'state_abbr', 'county_name',
    'total_jail_pop', 'total_jail_pop_rate',
    'total_jail_pretrial', 'total_jail_pretrial_rate',
    'total_jail_adm', 'total_jail_adm_rate',
    'total_jail_sentenced',
    'black_jail_pop_rate', 'white_jail_pop_rate',
    'total_pop', 'total_pop_15to64',
    'jail_rated_capacity',
]
vera = pd.read_csv(VERA_FILE, usecols=vera_cols)
vera_ca = vera[vera['state_abbr'] == 'CA'].copy()
print(f"Vera CA rows: {len(vera_ca)}, counties: {vera_ca['county_name'].nunique()}")

# Annual averages
vera_annual = (
    vera_ca.groupby(['county_name', 'year'])
    .agg(
        jail_pop          = ('total_jail_pop', 'mean'),
        jail_pop_rate     = ('total_jail_pop_rate', 'mean'),
        jail_pretrial     = ('total_jail_pretrial', 'mean'),
        jail_pretrial_rate= ('total_jail_pretrial_rate', 'mean'),
        jail_adm          = ('total_jail_adm', 'mean'),
        jail_adm_rate     = ('total_jail_adm_rate', 'mean'),
        jail_sentenced    = ('total_jail_sentenced', 'mean'),
        black_jail_rate   = ('black_jail_pop_rate', 'mean'),
        white_jail_rate   = ('white_jail_pop_rate', 'mean'),
        total_pop         = ('total_pop', 'mean'),
        jail_capacity     = ('jail_rated_capacity', 'mean'),
    )
    .reset_index()
)

# Racial disparity ratio
vera_annual['bw_disparity'] = vera_annual['black_jail_rate'] / vera_annual['white_jail_rate']

# Jail utilisation (% of capacity)
vera_annual['jail_utilisation'] = (
    vera_annual['jail_pop'] / vera_annual['jail_capacity'] * 100
)

# Pretrial share
vera_annual['pretrial_share'] = (
    vera_annual['jail_pretrial'] / vera_annual['jail_pop'] * 100
)

# ═══════════════════════════════════════════════════════════════════════════════
# 2.  MERGE
# ═══════════════════════════════════════════════════════════════════════════════
merged = policy_cy.merge(vera_annual, left_on=['county_vera', 'year'],
                          right_on=['county_name', 'year'], how='inner')
print(f"\nMerged county-years: {len(merged)}")
print(f"Counties in merge: {merged['county_vera'].nunique()}")
print(f"Year range: {int(merged['year'].min())}–{int(merged['year'].max())}")

# Filter to years with decent overlap (2015+) and minimum docs
merged = merged[(merged['year'] >= 2015) & (merged['n_docs'] >= 2)].copy()
print(f"After filter (≥2015, ≥2 docs): {len(merged)} county-years, "
      f"{merged['county_vera'].nunique()} counties")

# Save merged dataset
merged.to_csv(RESULTS_DIR / "vera_policy_merged.csv", index=False)

# ═══════════════════════════════════════════════════════════════════════════════
# 3.  ANALYSIS A — CROSS-SECTIONAL CORRELATIONS
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("ANALYSIS A: CROSS-SECTIONAL CORRELATIONS")
print("=" * 70)

outcome_vars = {
    'jail_pop_rate':     'Jail Population Rate (per 100k)',
    'jail_adm_rate':     'Jail Admission Rate (per 100k)',
    'pretrial_share':    'Pretrial Share (%)',
    'bw_disparity':      'Black/White Jail Rate Ratio',
    'jail_utilisation':  'Jail Utilisation (% capacity)',
}

corr_results = []
for var, label in outcome_vars.items():
    subset = merged.dropna(subset=['mean_ideology', var])
    if len(subset) < 10:
        continue
    r, p = stats.pearsonr(subset['mean_ideology'], subset[var])
    rho, p_rho = stats.spearmanr(subset['mean_ideology'], subset[var])
    corr_results.append({
        'Outcome': label,
        'Variable': var,
        'N': len(subset),
        'Pearson_r': round(r, 3),
        'Pearson_p': round(p, 4),
        'Spearman_rho': round(rho, 3),
        'Spearman_p': round(p_rho, 4),
        'Significant': '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else '†' if p < 0.10 else '',
    })

corr_df = pd.DataFrame(corr_results)
print("\nCorrelation: Mean Ideology Score ↔ Jail Outcomes")
print("-" * 70)
for _, row in corr_df.iterrows():
    sig = row['Significant']
    print(f"  {row['Outcome']:40s}  r={row['Pearson_r']:+.3f}  (p={row['Pearson_p']:.4f}) {sig}  N={row['N']}")

corr_df.to_csv(RESULTS_DIR / "vera_correlations.csv", index=False)

# ═══════════════════════════════════════════════════════════════════════════════
# 4.  ANALYSIS B — PROGRESSIVE vs TRADITIONAL COUNTIES
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("ANALYSIS B: PROGRESSIVE vs TRADITIONAL COUNTIES")
print("=" * 70)

# County-level mean ideology across all years
county_ideology = (
    merged.groupby('county_vera')
    .agg(
        mean_ideology   = ('mean_ideology', 'mean'),
        n_years         = ('year', 'nunique'),
    )
    .reset_index()
)

# Classify: top tercile = progressive, bottom tercile = traditional
q33, q66 = county_ideology['mean_ideology'].quantile([0.33, 0.66])
county_ideology['group'] = pd.cut(
    county_ideology['mean_ideology'],
    bins=[-np.inf, q33, q66, np.inf],
    labels=['Traditional', 'Moderate', 'Progressive']
)

merged = merged.merge(county_ideology[['county_vera', 'group']], on='county_vera', how='left')

group_compare = []
for var, label in outcome_vars.items():
    prog = merged.loc[merged['group'] == 'Progressive', var].dropna()
    trad = merged.loc[merged['group'] == 'Traditional', var].dropna()
    if len(prog) < 3 or len(trad) < 3:
        continue
    t_stat, p_val = stats.ttest_ind(prog, trad, equal_var=False)
    d = (prog.mean() - trad.mean()) / np.sqrt((prog.std()**2 + trad.std()**2) / 2)
    group_compare.append({
        'Outcome': label,
        'Progressive_mean': round(prog.mean(), 1),
        'Traditional_mean': round(trad.mean(), 1),
        'Difference': round(prog.mean() - trad.mean(), 1),
        'Pct_diff': round((prog.mean() - trad.mean()) / trad.mean() * 100, 1) if trad.mean() != 0 else np.nan,
        'Cohens_d': round(d, 2),
        't_stat': round(t_stat, 2),
        'p_value': round(p_val, 4),
        'Significant': '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else '†' if p_val < 0.10 else '',
    })

group_df = pd.DataFrame(group_compare)
print(f"\nProgressive (ideology > {q66:.2f}) vs Traditional (ideology < {q33:.2f})")
print("-" * 70)
for _, row in group_df.iterrows():
    print(f"  {row['Outcome']:40s}  Prog={row['Progressive_mean']:7.1f}  Trad={row['Traditional_mean']:7.1f}  "
          f"Δ={row['Difference']:+7.1f} ({row['Pct_diff']:+.1f}%)  d={row['Cohens_d']:+.2f} {row['Significant']}")

group_df.to_csv(RESULTS_DIR / "vera_group_comparison.csv", index=False)

# ═══════════════════════════════════════════════════════════════════════════════
# 5.  ANALYSIS C — LA COUNTY NATURAL EXPERIMENT (Gascón DiD Preview)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("ANALYSIS C: LA COUNTY NATURAL EXPERIMENT (Gascón Effect)")
print("=" * 70)

la = vera_annual[vera_annual['county_name'] == 'Los Angeles County'].copy()
la = la[(la['year'] >= 2015) & (la['year'] <= 2024)]

# Gascón took office Dec 2020
la['era'] = np.where(la['year'] <= 2020, 'Pre-Gascón', 'Gascón Era')
pre  = la[la['era'] == 'Pre-Gascón']
post = la[la['era'] == 'Gascón Era']

if len(pre) > 0 and len(post) > 0:
    for var, label in [('jail_pop_rate', 'Jail Pop Rate'),
                       ('jail_adm_rate', 'Jail Adm Rate'),
                       ('pretrial_share', 'Pretrial Share'),
                       ('bw_disparity', 'B/W Disparity')]:
        pre_val = pre[var].mean()
        post_val = post[var].mean()
        if pd.notna(pre_val) and pd.notna(post_val) and pre_val != 0:
            change = (post_val - pre_val) / pre_val * 100
            print(f"  {label:25s}  Pre: {pre_val:7.1f}  Post: {post_val:7.1f}  Δ={change:+.1f}%")

# ═══════════════════════════════════════════════════════════════════════════════
# 6.  ANALYSIS D — PANEL REGRESSION PREVIEW (OLS with county/year FE)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("ANALYSIS D: PANEL REGRESSION (OLS with Fixed Effects)")
print("=" * 70)

from numpy.linalg import lstsq

for dep_var, dep_label in [('jail_pop_rate', 'Jail Population Rate'),
                           ('jail_adm_rate', 'Jail Admission Rate'),
                           ('pretrial_share', 'Pretrial Share (%)')]:
    subset = merged.dropna(subset=['mean_ideology', dep_var]).copy()
    if len(subset) < 15:
        print(f"\n  {dep_label}: Insufficient data (n={len(subset)})")
        continue

    # De-mean by county (county fixed effects) and by year (year fixed effects)
    subset['ideology_dm'] = subset.groupby('county_vera')['mean_ideology'].transform(
        lambda x: x - x.mean())
    subset['outcome_dm'] = subset.groupby('county_vera')[dep_var].transform(
        lambda x: x - x.mean())
    # Also remove year means
    subset['ideology_dm'] -= subset.groupby('year')['ideology_dm'].transform('mean')
    subset['outcome_dm']  -= subset.groupby('year')['outcome_dm'].transform('mean')

    x = subset['ideology_dm'].values
    y = subset['outcome_dm'].values
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]

    if len(x) < 10:
        continue

    # OLS
    X = np.column_stack([np.ones_like(x), x])
    beta, residuals, _, _ = lstsq(X, y, rcond=None)
    y_hat = X @ beta
    resid = y - y_hat
    se = np.sqrt(np.sum(resid**2) / (len(y) - 2) / np.sum((x - x.mean())**2))
    t = beta[1] / se
    p = 2 * (1 - stats.t.cdf(abs(t), len(y) - 2))

    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else '†' if p < 0.10 else ''
    print(f"\n  {dep_label} ~ Ideology (TWFE)")
    print(f"    β = {beta[1]:.2f}   SE = {se:.2f}   t = {t:.2f}   p = {p:.4f} {sig}")
    print(f"    N = {len(y)}   Counties = {subset['county_vera'].nunique()}   "
          f"Years = {subset['year'].nunique()}")
    print(f"    Interpretation: 1-point ideology ↑ ≈ {beta[1]:+.1f} change in {dep_label}")


# ═══════════════════════════════════════════════════════════════════════════════
# 7.  FIGURES
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("GENERATING FIGURES")
print("=" * 70)

fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.suptitle("Prosecutor Policy × Jail Outcomes: Pilot Analysis",
             fontsize=18, fontweight='bold', color='white', y=0.98)
fig.subplots_adjust(hspace=0.35, wspace=0.35, top=0.90, bottom=0.08)

# ── Panel A: Scatter – Ideology vs Jail Pop Rate ─────────────────────────────
ax = axes[0, 0]
sub = merged.dropna(subset=['mean_ideology', 'jail_pop_rate'])
scatter = ax.scatter(sub['mean_ideology'], sub['jail_pop_rate'],
                     c=sub['year'], cmap='cool', s=50, alpha=0.75, edgecolors='white', linewidths=0.3)
# Fit line
if len(sub) >= 5:
    z = np.polyfit(sub['mean_ideology'], sub['jail_pop_rate'], 1)
    xline = np.linspace(sub['mean_ideology'].min(), sub['mean_ideology'].max(), 100)
    ax.plot(xline, np.polyval(z, xline), color=ACCENT, linewidth=2, linestyle='--')
    r, p = stats.pearsonr(sub['mean_ideology'], sub['jail_pop_rate'])
    ax.text(0.05, 0.95, f'r = {r:.2f} (p = {p:.3f})',
            transform=ax.transAxes, va='top', fontsize=10,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#21262d', edgecolor=ACCENT, alpha=0.9))
cb = plt.colorbar(scatter, ax=ax, shrink=0.8)
cb.set_label('Year', fontsize=9)
ax.set_xlabel('Mean Ideology Score')
ax.set_ylabel('Jail Pop Rate (per 100k)')
ax.set_title('A. Progressive Ideology → Lower Jail Pop Rate?')
ax.grid(True)

# ── Panel B: Scatter – Ideology vs B/W Disparity ─────────────────────────────
ax = axes[0, 1]
sub = merged.dropna(subset=['mean_ideology', 'bw_disparity'])
sub_clip = sub[sub['bw_disparity'] < sub['bw_disparity'].quantile(0.95)]  # remove extreme outliers
ax.scatter(sub_clip['mean_ideology'], sub_clip['bw_disparity'],
           c=ACCENT4, s=50, alpha=0.7, edgecolors='white', linewidths=0.3)
if len(sub_clip) >= 5:
    z = np.polyfit(sub_clip['mean_ideology'], sub_clip['bw_disparity'], 1)
    xline = np.linspace(sub_clip['mean_ideology'].min(), sub_clip['mean_ideology'].max(), 100)
    ax.plot(xline, np.polyval(z, xline), color=ACCENT4, linewidth=2, linestyle='--')
    r, p = stats.pearsonr(sub_clip['mean_ideology'], sub_clip['bw_disparity'])
    ax.text(0.05, 0.95, f'r = {r:.2f} (p = {p:.3f})',
            transform=ax.transAxes, va='top', fontsize=10,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#21262d', edgecolor=ACCENT4, alpha=0.9))
ax.set_xlabel('Mean Ideology Score')
ax.set_ylabel('Black/White Jail Rate Ratio')
ax.set_title('B. Progressive Ideology → Reduced Disparity?')
ax.grid(True)

# ── Panel C: Group comparison bar chart ───────────────────────────────────────
ax = axes[0, 2]
if len(group_df) > 0:
    x_pos = np.arange(len(group_df))
    width = 0.35
    bars_prog = ax.bar(x_pos - width/2, group_df['Progressive_mean'], width,
                       label='Progressive', color=ACCENT3, alpha=0.85, edgecolor='white', linewidth=0.5)
    bars_trad = ax.bar(x_pos + width/2, group_df['Traditional_mean'], width,
                       label='Traditional', color=ACCENT2, alpha=0.85, edgecolor='white', linewidth=0.5)
    ax.set_xticks(x_pos)
    short_labels = [l.replace(' (per 100k)', '').replace(' (% capacity)', ' %').replace(' (%)', ' %')
                    for l in group_df['Outcome']]
    ax.set_xticklabels(short_labels, rotation=35, ha='right', fontsize=8)
    ax.legend(fontsize=9, loc='upper right', framealpha=0.8)
    # Add significance markers
    for i, row in group_df.iterrows():
        if row['Significant']:
            max_val = max(row['Progressive_mean'], row['Traditional_mean'])
            ax.text(i, max_val * 1.05, row['Significant'], ha='center', fontsize=12,
                    color='white', fontweight='bold')
ax.set_title('C. Progressive vs Traditional Counties')
ax.grid(True, axis='y')

# ── Panel D: LA County time series with Gascón line ──────────────────────────
ax = axes[1, 0]
la_plot = vera_annual[vera_annual['county_name'] == 'Los Angeles County']
la_plot = la_plot[(la_plot['year'] >= 2015) & (la_plot['year'] <= 2024)]
ax.plot(la_plot['year'], la_plot['jail_pop_rate'], 'o-', color=ACCENT, linewidth=2, markersize=6)
ax.axvline(x=2020.95, color=ACCENT2, linestyle='--', linewidth=2, label='Gascón takes office')
ax.fill_betweenx(ax.get_ylim() if ax.get_ylim()[1] > 0 else [0, 1000],
                 2021, 2024, alpha=0.08, color=ACCENT2)
ax.set_xlabel('Year')
ax.set_ylabel('Jail Pop Rate (per 100k)')
ax.set_title('D. LA County: Jail Pop Rate & Gascón Effect')
ax.legend(fontsize=9, framealpha=0.8)
ax.grid(True)
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))

# ── Panel E: LA County B/W disparity over time ──────────────────────────────
ax = axes[1, 1]
la_disp = la_plot.dropna(subset=['bw_disparity'])
if len(la_disp) > 0:
    ax.plot(la_disp['year'], la_disp['bw_disparity'], 's-', color=ACCENT4, linewidth=2, markersize=6)
    ax.axvline(x=2020.95, color=ACCENT2, linestyle='--', linewidth=2, label='Gascón takes office')
    ax.set_xlabel('Year')
    ax.set_ylabel('Black/White Jail Rate Ratio')
    ax.set_title('E. LA County: Racial Disparity & Gascón')
    ax.legend(fontsize=9, framealpha=0.8)
ax.grid(True)
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))

# ── Panel F: Pretrial share in progressive vs traditional ────────────────────
ax = axes[1, 2]
for grp, color, ls in [('Progressive', ACCENT3, '-'), ('Traditional', ACCENT2, '--'), ('Moderate', NEUTRAL, ':')]:
    gdata = merged[merged['group'] == grp].groupby('year')['pretrial_share'].mean()
    if len(gdata) > 2:
        ax.plot(gdata.index, gdata.values, f'o{ls}', color=color, linewidth=2, markersize=5, label=grp)
ax.set_xlabel('Year')
ax.set_ylabel('Pretrial Share (%)')
ax.set_title('F. Pretrial Detention by Ideology Group')
ax.legend(fontsize=9, framealpha=0.8)
ax.grid(True)
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))

fig.savefig(FIG_DIR / "vera_pilot_analysis.png", dpi=180, bbox_inches='tight')
print(f"  Saved: {FIG_DIR / 'vera_pilot_analysis.png'}")
plt.close()

# ═══════════════════════════════════════════════════════════════════════════════
# 8.  SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("PILOT SUMMARY")
print("=" * 70)
print(f"""
Data successfully linked:
  • Policy data: {merged['county_vera'].nunique()} counties, {int(merged['year'].min())}–{int(merged['year'].max())}
  • Vera jail data: quarterly → annual averages
  • Merged dataset: {len(merged)} county-year observations

Key correlations (ideology ↔ jail outcomes):""")
for _, row in corr_df.iterrows():
    print(f"  • {row['Outcome']:40s}  r = {row['Pearson_r']:+.3f}  {row['Significant']}")

print(f"""
Group comparison (Progressive vs Traditional counties):""")
for _, row in group_df.iterrows():
    print(f"  • {row['Outcome']:40s}  Δ = {row['Difference']:+.1f}  (d = {row['Cohens_d']:+.2f})  {row['Significant']}")

print(f"""
Output files:
  • {RESULTS_DIR / 'vera_policy_merged.csv'}
  • {RESULTS_DIR / 'vera_correlations.csv'}
  • {RESULTS_DIR / 'vera_group_comparison.csv'}
  • {FIG_DIR / 'vera_pilot_analysis.png'}
""")
