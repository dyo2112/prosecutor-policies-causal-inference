"""
COVID-Controlled Reanalysis of Vera Jail x Prosecutor Policy
=============================================================
The initial pilot found large pre/post Gascon differences in LA County,
but Panel D showed a clear pre-trend: jail pop rates were already falling
before Gascon took office (COVID-driven decline starting 2019-2020).

This script addresses that by:
1. Using other CA counties as a control group (simple DiD)
2. Computing LA's EXCESS change relative to comparable counties
3. Showing pre-trends explicitly to assess parallel trends assumption
4. Re-running cross-sectional correlations with year controls

Author: Dvir Yogev, BERQ-J, UC Berkeley School of Law
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

# -- Paths --
ROOT = Path(__file__).resolve().parent.parent
VERA_FILE    = ROOT / "vera_jail" / "incarceration_trends_county.csv"
POLICY_FILE  = ROOT / "05_data" / "clean" / "prosecutor_policies_CLEANED.csv"
FIG_DIR      = ROOT / "06_figures"
RESULTS_DIR  = ROOT / "05_data" / "results"

# -- Style --
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

print("=" * 70)
print("COVID-CONTROLLED REANALYSIS")
print("=" * 70)

# ===================================================================
# 1. LOAD DATA
# ===================================================================
vera_cols = [
    'year', 'quarter', 'state_abbr', 'county_name',
    'total_jail_pop', 'total_jail_pop_rate',
    'total_jail_pretrial', 'total_jail_pretrial_rate',
    'total_jail_adm', 'total_jail_adm_rate',
    'total_jail_sentenced',
    'black_jail_pop_rate', 'white_jail_pop_rate',
    'total_pop', 'jail_rated_capacity',
]
vera = pd.read_csv(VERA_FILE, usecols=vera_cols)
vera_ca = vera[vera['state_abbr'] == 'CA'].copy()

# Annual averages
vera_annual = (
    vera_ca.groupby(['county_name', 'year'])
    .agg(
        jail_pop_rate     = ('total_jail_pop_rate', 'mean'),
        jail_adm_rate     = ('total_jail_adm_rate', 'mean'),
        jail_pretrial_rate= ('total_jail_pretrial_rate', 'mean'),
        black_jail_rate   = ('black_jail_pop_rate', 'mean'),
        white_jail_rate   = ('white_jail_pop_rate', 'mean'),
        total_pop         = ('total_pop', 'mean'),
    )
    .reset_index()
)
vera_annual['bw_disparity'] = vera_annual['black_jail_rate'] / vera_annual['white_jail_rate']

# Focus on 2015-2023 for overlap
vera_panel = vera_annual[(vera_annual['year'] >= 2015) & (vera_annual['year'] <= 2023)].copy()

# Policy data for identifying progressive DA transitions
pol = pd.read_csv(POLICY_FILE)

# ===================================================================
# 2. LA COUNTY DiD: LA vs REST-OF-CA CONTROL
# ===================================================================
print("\n" + "=" * 70)
print("ANALYSIS 1: LA COUNTY DiD (LA vs Rest of California)")
print("=" * 70)

# Large urban counties as control pool (pop > 500k annual avg in any year)
large_counties = (
    vera_panel.groupby('county_name')['total_pop']
    .max()
    .reset_index()
)
large_counties = large_counties[large_counties['total_pop'] > 500000]
control_counties = large_counties[large_counties['county_name'] != 'Los Angeles County']['county_name'].tolist()

print(f"\nControl counties (pop > 500k, excl. LA):")
for c in sorted(control_counties):
    print(f"  - {c}")

# Compute annual means for LA and control group
la_ts = vera_panel[vera_panel['county_name'] == 'Los Angeles County'].set_index('year')
ctrl_ts = (
    vera_panel[vera_panel['county_name'].isin(control_counties)]
    .groupby('year')
    .agg(
        jail_pop_rate      = ('jail_pop_rate', 'mean'),
        jail_adm_rate      = ('jail_adm_rate', 'mean'),
        jail_pretrial_rate = ('jail_pretrial_rate', 'mean'),
        bw_disparity       = ('bw_disparity', 'mean'),
    )
)

# Compute difference (LA - control) over time
outcomes = ['jail_pop_rate', 'jail_adm_rate', 'jail_pretrial_rate', 'bw_disparity']
outcome_labels = {
    'jail_pop_rate':      'Jail Pop Rate (per 100k)',
    'jail_adm_rate':      'Jail Admission Rate (per 100k)',
    'jail_pretrial_rate': 'Pretrial Rate (per 100k)',
    'bw_disparity':       'Black/White Disparity Ratio',
}

years = sorted(set(la_ts.index) & set(ctrl_ts.index))

diff_data = {}
for var in outcomes:
    diff_data[var] = []
    for y in years:
        la_val = la_ts.loc[y, var] if y in la_ts.index and pd.notna(la_ts.loc[y, var]) else np.nan
        ctrl_val = ctrl_ts.loc[y, var] if y in ctrl_ts.index and pd.notna(ctrl_ts.loc[y, var]) else np.nan
        diff_data[var].append(la_val - ctrl_val)

diff_df = pd.DataFrame(diff_data, index=years)

# DiD estimate: mean(post difference) - mean(pre difference)
# Gascon took office Dec 2020, so 2021+ is post
pre_years = [y for y in years if y <= 2020]
post_years = [y for y in years if y >= 2021]

print(f"\nDiD Estimates (Post = 2021+, Pre = 2015-2020):")
print("-" * 70)
did_results = []
for var in outcomes:
    pre_diff = diff_df.loc[pre_years, var].mean()
    post_diff = diff_df.loc[post_years, var].mean()
    did_est = post_diff - pre_diff

    # Pre-trend test: regress diff on year (pre-period only)
    pre_vals = diff_df.loc[pre_years, var].dropna()
    if len(pre_vals) >= 3:
        slope, intercept, r, p_trend, se = stats.linregress(pre_vals.index, pre_vals.values)
        trend_sig = '(TREND!)' if p_trend < 0.10 else '(flat)'
    else:
        slope, p_trend = np.nan, np.nan
        trend_sig = '(N/A)'

    print(f"\n  {outcome_labels[var]}:")
    print(f"    Pre-period LA-Control avg:  {pre_diff:+.1f}")
    print(f"    Post-period LA-Control avg: {post_diff:+.1f}")
    print(f"    DiD estimate:               {did_est:+.1f}")
    print(f"    Pre-trend slope:            {slope:+.2f}/yr  (p={p_trend:.3f}) {trend_sig}")

    did_results.append({
        'Outcome': outcome_labels[var],
        'Pre_LA_minus_Control': round(pre_diff, 1),
        'Post_LA_minus_Control': round(post_diff, 1),
        'DiD_Estimate': round(did_est, 1),
        'Pre_Trend_Slope': round(slope, 2) if pd.notna(slope) else None,
        'Pre_Trend_p': round(p_trend, 3) if pd.notna(p_trend) else None,
        'Pre_Trend_Flat': p_trend >= 0.10 if pd.notna(p_trend) else None,
    })

pd.DataFrame(did_results).to_csv(RESULTS_DIR / "vera_did_estimates.csv", index=False)

# ===================================================================
# 3. BROADER COVID CONTROL: Year-demeaned cross-sectional correlations
# ===================================================================
print("\n" + "=" * 70)
print("ANALYSIS 2: Year-Demeaned Correlations (COVID-controlled)")
print("=" * 70)

# Reload merged data
merged = pd.read_csv(RESULTS_DIR / "vera_policy_merged.csv")

corr_controlled = []
for var in ['jail_pop_rate', 'jail_adm_rate', 'pretrial_share', 'bw_disparity']:
    sub = merged.dropna(subset=['mean_ideology', var]).copy()
    if len(sub) < 15:
        continue

    # Raw correlation
    r_raw, p_raw = stats.pearsonr(sub['mean_ideology'], sub[var])

    # Year-demeaned (partial correlation controlling for year)
    sub['ideo_resid'] = sub.groupby('year')['mean_ideology'].transform(lambda x: x - x.mean())
    sub['out_resid']  = sub.groupby('year')[var].transform(lambda x: x - x.mean())

    r_ctrl, p_ctrl = stats.pearsonr(sub['ideo_resid'], sub['out_resid'])

    label = outcome_labels.get(var, var)
    print(f"\n  {label}:")
    print(f"    Raw:            r = {r_raw:+.3f}  (p = {p_raw:.4f})")
    print(f"    Year-controlled: r = {r_ctrl:+.3f}  (p = {p_ctrl:.4f})")

    corr_controlled.append({
        'Outcome': label,
        'Raw_r': round(r_raw, 3),
        'Raw_p': round(p_raw, 4),
        'Year_Controlled_r': round(r_ctrl, 3),
        'Year_Controlled_p': round(p_ctrl, 4),
    })

pd.DataFrame(corr_controlled).to_csv(RESULTS_DIR / "vera_correlations_controlled.csv", index=False)

# ===================================================================
# 4. STATEWIDE COVID EFFECT: Show all large counties
# ===================================================================
print("\n" + "=" * 70)
print("ANALYSIS 3: Statewide Trends (COVID Context)")
print("=" * 70)

# Normalize all counties to 2019 = 100 for jail_pop_rate
all_large = vera_panel[vera_panel['county_name'].isin(control_counties + ['Los Angeles County'])]
pivot = all_large.pivot_table(index='year', columns='county_name', values='jail_pop_rate')

# Normalize to 2019 baseline
if 2019 in pivot.index:
    normed = pivot.div(pivot.loc[2019]) * 100
else:
    normed = pivot.div(pivot.iloc[0]) * 100

print("\nJail Pop Rate indexed to 2019 = 100:")
for county in sorted(normed.columns):
    vals = normed[county]
    pre_19 = vals.get(2019, np.nan)
    post_22 = vals.get(2022, np.nan)
    if pd.notna(pre_19) and pd.notna(post_22):
        change = post_22 - 100
        print(f"  {county:30s}  2019->2022: {change:+.1f}%")

# ===================================================================
# 5. FIGURES
# ===================================================================
print("\n" + "=" * 70)
print("GENERATING FIGURES")
print("=" * 70)

fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.suptitle("COVID-Controlled Reanalysis: Prosecutor Policy x Jail Outcomes",
             fontsize=17, fontweight='bold', color='white', y=0.98)
fig.subplots_adjust(hspace=0.38, wspace=0.35, top=0.90, bottom=0.08)

# -- Panel A: LA vs Control Counties (jail pop rate levels) --
ax = axes[0, 0]
ax.plot(years, [la_ts.loc[y, 'jail_pop_rate'] if y in la_ts.index else np.nan for y in years],
        'o-', color=ACCENT, linewidth=2.5, markersize=7, label='Los Angeles', zorder=5)
ax.plot(ctrl_ts.index, ctrl_ts['jail_pop_rate'],
        's--', color=ACCENT2, linewidth=2, markersize=6, label='Control (large urban)')
ax.axvline(x=2020.95, color='white', linestyle=':', linewidth=1.5, alpha=0.6)
ax.axvspan(2019.5, 2020.5, alpha=0.08, color=ACCENT4, label='COVID onset')
ax.text(2021.1, ax.get_ylim()[1] if ax.get_ylim()[1] > 0 else 350, 'Gascon',
        color=ACCENT3, fontsize=10, va='top', fontweight='bold')
ax.set_xlabel('Year')
ax.set_ylabel('Jail Pop Rate (per 100k)')
ax.set_title('A. LA vs Control: Both Declined (COVID)')
ax.legend(fontsize=8, framealpha=0.8, loc='upper right')
ax.grid(True)
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))

# -- Panel B: LA minus Control (the actual DiD difference) --
ax = axes[0, 1]
ax.bar(years, diff_df['jail_pop_rate'].values,
       color=[ACCENT3 if y >= 2021 else NEUTRAL for y in years],
       alpha=0.8, edgecolor='white', linewidth=0.5)
ax.axhline(y=0, color='white', linewidth=0.5, alpha=0.3)
ax.axvline(x=2020.5, color='white', linestyle=':', linewidth=1.5, alpha=0.6)
# Show pre-period mean and post-period mean
pre_mean = diff_df.loc[pre_years, 'jail_pop_rate'].mean()
post_mean = diff_df.loc[post_years, 'jail_pop_rate'].mean()
ax.axhline(y=pre_mean, color=NEUTRAL, linestyle='--', linewidth=1.5, label=f'Pre mean: {pre_mean:+.0f}')
ax.axhline(y=post_mean, color=ACCENT3, linestyle='--', linewidth=1.5, label=f'Post mean: {post_mean:+.0f}')
ax.set_xlabel('Year')
ax.set_ylabel('LA minus Control (per 100k)')
ax.set_title('B. DiD: LA Excess Change After Gascon')
ax.legend(fontsize=8, framealpha=0.8)
ax.grid(True, axis='y')
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))

# -- Panel C: All large counties normalized to 2019 --
ax = axes[0, 2]
for county in sorted(normed.columns):
    if county == 'Los Angeles County':
        ax.plot(normed.index, normed[county], 'o-', color=ACCENT, linewidth=3,
                markersize=6, label='Los Angeles', zorder=10)
    else:
        ax.plot(normed.index, normed[county], '-', color=NEUTRAL, linewidth=1,
                alpha=0.4, label='_nolegend_')
# Control mean
ctrl_mean_normed = normed[[c for c in normed.columns if c != 'Los Angeles County']].mean(axis=1)
ax.plot(ctrl_mean_normed.index, ctrl_mean_normed.values, 's--', color=ACCENT2,
        linewidth=2, markersize=5, label='Control avg', zorder=8)
ax.axvline(x=2020.5, color='white', linestyle=':', linewidth=1.5, alpha=0.6)
ax.axhline(y=100, color='white', linewidth=0.5, alpha=0.3)
ax.set_xlabel('Year')
ax.set_ylabel('Jail Pop Rate (2019 = 100)')
ax.set_title('C. All Large Counties: COVID Hit Everyone')
ax.legend(fontsize=8, framealpha=0.8)
ax.grid(True)
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))

# -- Panel D: Pre-trend test for jail pop rate --
ax = axes[1, 0]
pre_data = diff_df.loc[pre_years, 'jail_pop_rate'].dropna()
post_data = diff_df.loc[post_years, 'jail_pop_rate'].dropna()
ax.scatter(pre_data.index, pre_data.values, color=NEUTRAL, s=80, zorder=5,
           edgecolors='white', linewidths=0.5, label='Pre-treatment')
ax.scatter(post_data.index, post_data.values, color=ACCENT3, s=80, zorder=5,
           edgecolors='white', linewidths=0.5, label='Post-treatment')
# Fit pre-trend line
if len(pre_data) >= 3:
    slope, intercept, r, p_trend, se = stats.linregress(pre_data.index, pre_data.values)
    x_line = np.array(pre_years)
    ax.plot(x_line, slope * x_line + intercept, '--', color=NEUTRAL, linewidth=1.5)
    # Extrapolate to post-period (counterfactual)
    x_ext = np.array(post_years)
    ax.plot(x_ext, slope * x_ext + intercept, ':', color=ACCENT4, linewidth=1.5,
            label=f'Pre-trend extrapolated')
    ax.text(0.05, 0.05, f'Pre-trend: {slope:+.1f}/yr (p={p_trend:.3f})',
            transform=ax.transAxes, fontsize=9, va='bottom',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#21262d', edgecolor=NEUTRAL, alpha=0.9))
ax.axvline(x=2020.5, color='white', linestyle=':', linewidth=1.5, alpha=0.6)
ax.axhline(y=0, color='white', linewidth=0.5, alpha=0.3)
ax.set_xlabel('Year')
ax.set_ylabel('LA minus Control (per 100k)')
ax.set_title('D. Pre-Trend Test: Parallel Trends?')
ax.legend(fontsize=8, framealpha=0.8)
ax.grid(True)
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))

# -- Panel E: DiD for admissions --
ax = axes[1, 1]
ax.bar(years, diff_df['jail_adm_rate'].values,
       color=[ACCENT3 if y >= 2021 else NEUTRAL for y in years],
       alpha=0.8, edgecolor='white', linewidth=0.5)
ax.axhline(y=0, color='white', linewidth=0.5, alpha=0.3)
ax.axvline(x=2020.5, color='white', linestyle=':', linewidth=1.5, alpha=0.6)
pre_adm = diff_df.loc[pre_years, 'jail_adm_rate'].mean()
post_adm = diff_df.loc[post_years, 'jail_adm_rate'].mean()
ax.axhline(y=pre_adm, color=NEUTRAL, linestyle='--', linewidth=1.5, label=f'Pre mean: {pre_adm:+.0f}')
ax.axhline(y=post_adm, color=ACCENT3, linestyle='--', linewidth=1.5, label=f'Post mean: {post_adm:+.0f}')
ax.set_xlabel('Year')
ax.set_ylabel('LA minus Control (per 100k)')
ax.set_title('E. DiD: Admission Rate (LA Excess)')
ax.legend(fontsize=8, framealpha=0.8)
ax.grid(True, axis='y')
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))

# -- Panel F: Year-controlled vs raw correlations --
ax = axes[1, 2]
if len(corr_controlled) > 0:
    cc = pd.DataFrame(corr_controlled)
    x_pos = np.arange(len(cc))
    width = 0.35
    bars1 = ax.bar(x_pos - width/2, cc['Raw_r'], width, label='Raw', color=NEUTRAL, alpha=0.8,
                   edgecolor='white', linewidth=0.5)
    bars2 = ax.bar(x_pos + width/2, cc['Year_Controlled_r'], width, label='Year-controlled',
                   color=ACCENT, alpha=0.85, edgecolor='white', linewidth=0.5)
    ax.axhline(y=0, color='white', linewidth=0.5, alpha=0.3)
    # Significance markers
    for i, row in cc.iterrows():
        for j, (val, pval) in enumerate([(row['Raw_r'], row['Raw_p']),
                                          (row['Year_Controlled_r'], row['Year_Controlled_p'])]):
            xp = i + (j - 0.5) * width
            sig = '***' if pval < 0.001 else '**' if pval < 0.01 else '*' if pval < 0.05 else ''
            if sig:
                yp = val + (0.015 if val >= 0 else -0.025)
                ax.text(xp, yp, sig, ha='center', fontsize=11, color='white', fontweight='bold')
    short_names = ['Jail Pop\nRate', 'Jail Adm\nRate', 'Pretrial\nShare', 'B/W\nDisparity']
    ax.set_xticks(x_pos)
    ax.set_xticklabels(short_names[:len(cc)], fontsize=8)
    ax.legend(fontsize=9, framealpha=0.8)
ax.set_ylabel('Pearson r')
ax.set_title('F. Correlations: Raw vs Year-Controlled')
ax.grid(True, axis='y')

fig.savefig(FIG_DIR / "vera_covid_controlled.png", dpi=180, bbox_inches='tight')
print(f"\n  Saved: {FIG_DIR / 'vera_covid_controlled.png'}")
plt.close()

# ===================================================================
# 6. SUMMARY
# ===================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("""
Key takeaways from COVID-controlled reanalysis:

1. PRE-TRENDS: The naive pre/post Gascon comparison is confounded by
   COVID. All large CA counties saw jail pop declines in 2020. The
   pre-trend in Panel D shows whether LA was already diverging from
   control counties before Gascon.

2. DiD ESTIMATES: After netting out the statewide COVID decline using
   large urban CA counties as controls, the Gascon-specific effect
   becomes clearer (or disappears, depending on what the data shows).

3. YEAR-CONTROLLED CORRELATIONS: Removing year-level variation
   (which captures COVID and statewide policy changes) reveals
   whether the ideology-jail association is real or driven by
   temporal confounding.
""")
