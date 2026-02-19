"""
Arnold Ventures Funder Summary Figure
4-panel narrative arc:
  A. Measurement works (progressive surge)
  B. Causal design feasible (IV first stage: margin → ideology)
  C. Progressive counties jail fewer people (year-demeaned scatter)
  D. Not a COVID artifact (raw vs. year-controlled correlations)

Run from the aclu_policies root directory with system Python:
  python 04_analysis/funder_summary_figure.py
"""

import matplotlib
matplotlib.use('Agg')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

ROOT = r"c:\Users\dviry\My Drive\Papers and ClassReading\Berkeley\postdoc\aclu_policies"
DATA = ROOT + r"\05_data\results"
OUT  = ROOT + r"\06_figures\funder_summary_figure.png"

# ── Palette ────────────────────────────────────────────────────────────────────
C_PROG = "#1565C0"   # deep blue  → progressive
C_TRAD = "#C62828"   # deep red   → traditional
C_NEUT = "#9E9E9E"   # grey
C_GOLD = "#F57C00"   # amber
C_DARK = "#212121"
C_BG   = "#FAFAFA"

# ── Load Data ──────────────────────────────────────────────────────────────────
clean  = pd.read_csv(ROOT + r"\05_data\clean\prosecutor_policies_CLEANED.csv")
merged = pd.read_csv(DATA + r"\vera_policy_merged.csv")
elec   = pd.read_csv(DATA + r"\election_margins_1st_2nd.csv")
raw_c  = pd.read_csv(DATA + r"\vera_correlations.csv")
ctrl_c = pd.read_csv(DATA + r"\vera_correlations_controlled.csv")

# ═══════════════════════════════════════════════════════════════════════════════
# Layout
# ═══════════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(14, 10), facecolor='white')
gs = gridspec.GridSpec(
    2, 2, figure=fig,
    left=0.09, right=0.97,
    top=0.87, bottom=0.09,
    hspace=0.48, wspace=0.36
)
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[1, 0])
ax4 = fig.add_subplot(gs[1, 1])

for ax in [ax1, ax2, ax3, ax4]:
    ax.set_facecolor(C_BG)
    for sp in ax.spines.values():
        sp.set_edgecolor('#DDDDDD')

TITLE_KW = dict(fontsize=11, fontweight='bold', color=C_DARK, pad=8)
AXIS_KW  = dict(fontsize=9, color='#444')

# ─────────────────────────────────────────────────────────────────────────────
# Panel A: % Progressive documents per year (2012–2024)
# ─────────────────────────────────────────────────────────────────────────────
yr_col   = 'year'
ideo_col = 'ideology'   # actual col in cleaned CSV

prog_tags = ['clearly_progressive', 'leans_progressive', 'progressive']

yearly = clean.dropna(subset=[yr_col, ideo_col]).copy()
yearly[yr_col] = pd.to_numeric(yearly[yr_col], errors='coerce')
yearly = yearly[(yearly[yr_col] >= 2012) & (yearly[yr_col] <= 2024)]
yearly['is_prog'] = yearly[ideo_col].str.lower().isin(prog_tags)

yr_sum = yearly.groupby(yr_col).agg(
    n=('is_prog', 'count'),
    pct=('is_prog', 'mean')
).reset_index()
yr_sum = yr_sum[yr_sum['n'] >= 5]

ax1.fill_between(yr_sum[yr_col], yr_sum['pct'] * 100,
                 alpha=0.15, color=C_PROG)
ax1.plot(yr_sum[yr_col], yr_sum['pct'] * 100,
         color=C_PROG, linewidth=2.5, marker='o', markersize=6, zorder=3)

# 2020 shading
ax1.axvspan(2019.5, 2021.5, alpha=0.12, color='#FFC107', zorder=1)
ymax = yr_sum['pct'].max() * 100 + 3
ax1.text(2020.5, ymax * 0.96, 'BLM\n2020', ha='center', va='top',
         fontsize=7.5, color='#795548', alpha=0.9)

# Trend annotation
try:
    sl, ic, r, p, _ = stats.linregress(yr_sum[yr_col], yr_sum['pct'] * 100)
    ax1.annotate(f"+{sl:.1f} pp/yr  (p = {p:.3f})",
                 xy=(0.05, 0.93), xycoords='axes fraction',
                 fontsize=8.5, color=C_PROG,
                 bbox=dict(boxstyle='round,pad=0.3', fc='white', ec=C_PROG, alpha=0.9))
except Exception:
    pass

ax1.set_title("A  ·  Measurement works: progressive surge is real", **TITLE_KW)
ax1.set_xlabel("Year", **AXIS_KW)
ax1.set_ylabel("% Documents Progressive", **AXIS_KW)
ax1.set_xlim(2011.5, 2024.5)
ax1.tick_params(labelsize=8)

# ─────────────────────────────────────────────────────────────────────────────
# Panel B: Event study — jail rates around progressive-DA elections
# ─────────────────────────────────────────────────────────────────────────────
# Treatment defined by our NLP ideology classifier applied to internal DA
# policy documents — the core contribution of this project.
post_elec = pd.read_csv(DATA + r"\final_post_election_analysis.csv")
post_elec['mean_ideology_score'] = pd.to_numeric(
    post_elec['mean_ideology_score'], errors='coerce')
post_elec['tenure_start'] = pd.to_numeric(post_elec['tenure_start'], errors='coerce')
post_elec['county_clean'] = post_elec['county'].str.strip()

# A DA term is "progressive" if the avg ideology score of their policy
# documents exceeds 0.3 (well above neutral zero).
da_terms = post_elec.groupby(['county_clean','da_name','tenure_start']).agg(
    avg_ideo=('mean_ideology_score','mean')).reset_index()
prog_das = da_terms[da_terms['avg_ideo'] > 0.3]
# For each county, the event year = first progressive DA taking office
first_prog = prog_das.groupby('county_clean')['tenure_start'].min().reset_index()
first_prog.columns = ['county_clean', 'event_year']
event_map = dict(zip(first_prog['county_clean'], first_prog['event_year']))

# Prepare vera data with standardised county names
ev_df = merged[['county_vera','year','jail_pop_rate']].copy()
ev_df['jail_pop_rate'] = pd.to_numeric(ev_df['jail_pop_rate'], errors='coerce')
ev_df['year'] = pd.to_numeric(ev_df['year'], errors='coerce')
ev_df = ev_df.dropna()
ev_df['county_clean'] = ev_df['county_vera'].str.replace(
    ' County', '', regex=False).str.strip()

# Tag treated counties
ev_df['event_year'] = ev_df['county_clean'].map(event_map)

# Treated counties: must have ≥1 pre AND ≥1 post observations
treated = ev_df.dropna(subset=['event_year']).copy()
treated['t'] = treated['year'] - treated['event_year']
good_counties = []
for c in treated['county_clean'].unique():
    cdf = treated[treated['county_clean'] == c]
    if (cdf['t'] < 0).any() and (cdf['t'] >= 0).any():
        good_counties.append(c)
treated = treated[treated['county_clean'].isin(good_counties)]

# Control (never-treated) counties
ctrl = ev_df[ev_df['event_year'].isna()].copy()

# --- Normalize treated counties to pre-treatment baseline (index = 100) ---
for c in good_counties:
    mask = treated['county_clean'] == c
    cdf = treated.loc[mask].sort_values('t')
    pre = cdf[cdf['t'] < 0]
    base = pre.iloc[-1]['jail_pop_rate'] if len(pre) else cdf.iloc[0]['jail_pop_rate']
    treated.loc[mask, 'jail_idx'] = treated.loc[mask, 'jail_pop_rate'] / base * 100

# --- Build control-group line in event time ---
# For each treated county, map control calendar years into that county's
# event time, then average across all treated-county perspectives.
ctrl_event_rows = []
for c in good_counties:
    e_yr = event_map[c]
    ctrl_yr = ctrl.groupby('year')['jail_pop_rate'].mean().reset_index()
    ctrl_yr['t'] = ctrl_yr['year'] - e_yr
    pre_ctrl = ctrl_yr[ctrl_yr['t'] < 0].sort_values('t')
    ctrl_base = pre_ctrl.iloc[-1]['jail_pop_rate'] if len(pre_ctrl) else ctrl_yr.iloc[0]['jail_pop_rate']
    ctrl_yr['jail_idx'] = ctrl_yr['jail_pop_rate'] / ctrl_base * 100
    ctrl_yr['ref_county'] = c
    ctrl_event_rows.append(ctrl_yr[['t', 'jail_idx', 'ref_county']])

ctrl_event = pd.concat(ctrl_event_rows)
ctrl_avg = ctrl_event.groupby('t')['jail_idx'].mean().reset_index()
ctrl_avg.columns = ['t', 'mean']

# --- Plotting ---
# Individual treated county lines
county_colors = {c: plt.cm.Set1(i) for i, c in enumerate(good_counties)}
for c in good_counties:
    cdf = treated[treated['county_clean'] == c].sort_values('t')
    ax2.plot(cdf['t'], cdf['jail_idx'],
             color=county_colors[c], linewidth=2.2, marker='o', markersize=5,
             alpha=0.85, label=c, zorder=3)

# Treated average (bold)
tr_avg = treated.groupby('t')['jail_idx'].agg(['mean','sem']).reset_index()
tr_avg.columns = ['t', 'mean', 'sem']
tr_avg['sem'] = tr_avg['sem'].fillna(0)
ax2.plot(tr_avg['t'], tr_avg['mean'],
         color=C_PROG, linewidth=3, marker='s', markersize=7,
         label='Treated avg', zorder=5, alpha=0.9)
ax2.fill_between(tr_avg['t'], tr_avg['mean'] - tr_avg['sem'],
                 tr_avg['mean'] + tr_avg['sem'],
                 color=C_PROG, alpha=0.12, zorder=2)

# Control average (dashed grey)
t_range = [treated['t'].min() - 0.5, treated['t'].max() + 0.5]
ctrl_plot = ctrl_avg[(ctrl_avg['t'] >= t_range[0]) & (ctrl_avg['t'] <= t_range[1])]
ax2.plot(ctrl_plot['t'], ctrl_plot['mean'],
         color='#757575', linewidth=2.5, linestyle='--', marker='D', markersize=4,
         alpha=0.7, label=f'Control avg (n={ctrl["county_clean"].nunique()})', zorder=4)

# Treatment line at t=0
ax2.axvline(0, color=C_TRAD, linewidth=2, linestyle='--', alpha=0.7, zorder=4)
ax2.annotate('DA takes\noffice', xy=(0, 1), xycoords=('data', 'axes fraction'),
             xytext=(5, -5), textcoords='offset points',
             fontsize=7, color=C_TRAD, va='top', ha='left')

# Baseline reference line at 100
ax2.axhline(100, color='grey', linewidth=0.8, linestyle=':', alpha=0.5, zorder=1)

ax2.set_xlabel("Years relative to progressive DA taking office", fontsize=8.5)
ax2.set_ylabel("Jail Pop Rate Index\n(pre-treatment year = 100)", fontsize=8.5)
ax2.tick_params(labelsize=8)
ax2.legend(fontsize=6.5, framealpha=0.9, loc='lower left', ncol=1)
ax2.set_title("B  ·  Event study: jail rates fall under progressive DAs\n"
              f"(n = {len(good_counties)} treated counties vs. never-treated controls)",
              **TITLE_KW)


# ─────────────────────────────────────────────────────────────────────────────
# Panel C: Year-demeaned ideology vs jail pop rate
# vera_policy_merged cols: county_vera, year, mean_ideology,
#   jail_pop_rate, jail_adm_rate, black_white_disparity, jail_utilisation, pretrial_share
# ─────────────────────────────────────────────────────────────────────────────
jail_col = 'jail_pop_rate'

sub = merged.dropna(subset=['mean_ideology', jail_col, 'year']).copy()
sub['mean_ideology'] = pd.to_numeric(sub['mean_ideology'], errors='coerce')
sub[jail_col]        = pd.to_numeric(sub[jail_col], errors='coerce')
sub['year']          = pd.to_numeric(sub['year'], errors='coerce')
sub = sub.dropna()

# Year-demean
sub['ideo_r'] = sub.groupby('year')['mean_ideology'].transform(lambda x: x - x.mean())
sub['jail_r'] = sub.groupby('year')[jail_col].transform(lambda x: x - x.mean())

med3 = sub['mean_ideology'].median()
colors_c = [C_PROG if v > med3 else C_TRAD for v in sub['mean_ideology']]

ax3.scatter(sub['ideo_r'], sub['jail_r'],
            c=colors_c, s=28, alpha=0.45, edgecolors='none', zorder=2)

try:
    sl3, ic3, r3, p3, _ = stats.linregress(sub['ideo_r'], sub['jail_r'])
    xs3 = np.linspace(sub['ideo_r'].min(), sub['ideo_r'].max(), 100)
    ax3.plot(xs3, ic3 + sl3 * xs3, color=C_GOLD, linewidth=2.5, zorder=4,
             label=f"r = {r3:.2f}  p = {p3:.3f}")
    sig_note = f"r = {r3:.2f}  (p = {p3:.3f})  \nn = {len(sub)}"
    ax3.annotate(sig_note,
                 xy=(0.05, 0.93), xycoords='axes fraction',
                 fontsize=8.5, color=C_GOLD,
                 bbox=dict(boxstyle='round,pad=0.3', fc='white', ec=C_GOLD, alpha=0.9))
except Exception as e:
    print("Panel C regression:", e)

ax3.axhline(0, color=C_NEUT, linewidth=0.8, alpha=0.4)
ax3.axvline(0, color=C_NEUT, linewidth=0.8, alpha=0.4)

ax3.set_title("C  ·  More-progressive counties jail fewer people\n(within-year: year fixed effects removed)",
              **TITLE_KW)
ax3.set_xlabel("Ideology Residual (relative to CA avg, same year)", **AXIS_KW)
ax3.set_ylabel("Jail Pop Rate Residual (per 100k)", **AXIS_KW)
ax3.tick_params(labelsize=8)

leg_c = [
    Line2D([0],[0], marker='o', color='w', markerfacecolor=C_PROG, ms=8, label='Progressive county'),
    Line2D([0],[0], marker='o', color='w', markerfacecolor=C_TRAD, ms=8, label='Traditional county'),
    Line2D([0],[0], color=C_GOLD, linewidth=2.5, label='Year-controlled fit'),
]
ax3.legend(handles=leg_c, fontsize=7.5, framealpha=0.9, loc='upper right')

# ─────────────────────────────────────────────────────────────────────────────
# Panel D: Raw vs Year-Controlled correlations (bar chart)
# ─────────────────────────────────────────────────────────────────────────────
try:
    # vera_correlations_controlled.csv already has both raw and controlled in one file
    bars = ctrl_c.rename(columns={
        'Outcome':          'outcome',
        'Raw_r':            'r_raw',
        'Raw_p':            'p_raw',
        'Year_Controlled_r':'r_ctrl',
        'Year_Controlled_p':'p_ctrl',
    })
    bars = bars.dropna(subset=['r_raw', 'r_ctrl'])

    label_map = {
        'Jail Population Rate':           'Jail Pop\nRate',
        'Jail Admission Rate':            'Jail Adm\nRate',
        'Pretrial Share':                 'Pretrial\nShare',
        'Black/White Disparity Ratio':    'B/W\nDisparity',
        'Jail Utilisation (% capacity)':  'Jail\nUtilisation',
    }
    bars['label'] = bars['outcome'].map(lambda x: label_map.get(x, x))

    x  = np.arange(len(bars))
    w  = 0.37

    b_raw  = ax4.bar(x - w/2, bars['r_raw'],  w, color=C_NEUT, alpha=0.80, label='Raw correlation')
    b_ctrl = ax4.bar(x + w/2, bars['r_ctrl'], w, color=C_GOLD, alpha=0.90, label='Year-controlled')

    # Significance stars
    for i, row in bars.reset_index(drop=True).iterrows():
        for val, p_val, xpos in [
            (row['r_raw'],  row['p_raw'],  x[i] - w/2),
            (row['r_ctrl'], row['p_ctrl'], x[i] + w/2),
        ]:
            if pd.notna(p_val) and p_val < 0.05:
                ypos = val + (0.008 if val >= 0 else -0.02)
                ax4.text(xpos, ypos, '*', ha='center', fontsize=11, color=C_DARK)

    ax4.axhline(0, color=C_DARK, linewidth=0.8)
    ax4.set_xticks(x)
    ax4.set_xticklabels(bars['label'], fontsize=8)
    ax4.set_ylabel("Pearson  r", **AXIS_KW)
    ax4.tick_params(labelsize=8)
    ax4.legend(fontsize=8.5, framealpha=0.9, loc='upper right')

    ax4.annotate("* p < 0.05",
                 xy=(0.97, 0.06), xycoords='axes fraction',
                 fontsize=8, color=C_DARK, ha='right',
                 bbox=dict(boxstyle='round,pad=0.3', fc='white', ec=C_NEUT, alpha=0.8))
    ax4.set_title("D  ·  Ideology–jail link is not a COVID artifact\n(raw vs. year-controlled correlations)",
                  **TITLE_KW)

except Exception as e:
    print("Panel D error:", e)

# ── Super-title & row labels ───────────────────────────────────────────────────
fig.suptitle(
    "Prosecutorial Ideology & Jail Outcomes: A Four-Step Narrative for Funders",
    fontsize=13.5, fontweight='bold', color=C_DARK, y=0.97
)




# ── Save ──────────────────────────────────────────────────────────────────────
fig.savefig(OUT, dpi=180, bbox_inches='tight', facecolor='white')
print(f"Saved: {OUT}")
