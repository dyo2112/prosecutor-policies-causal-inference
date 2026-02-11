"""
FINAL IMPROVED Analysis: CA Prosecutor Policies and Elections
--------------------------------------------------------------
Key improvement: Define "close elections" as margin between 1st and 2nd place,
not absolute vote percentage (critical for multi-candidate races)
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RAW_DATA = PROJECT_ROOT / '01_raw_data'
CLEAN_DATA = PROJECT_ROOT / '05_data' / 'clean'
RESULTS_DATA = PROJECT_ROOT / '05_data' / 'results'

print("="*80)
print("FINAL ANALYSIS: MARGINS BETWEEN 1ST AND 2ND PLACE")
print("="*80)

# ============================================================================
# PART 1: CALCULATE PROPER ELECTION MARGINS
# ============================================================================

print("\n" + "="*80)
print("PART 1: CALCULATING 1ST-2ND PLACE MARGINS")
print("="*80)

# Load data
elections = pd.read_excel(RAW_DATA / 'ca_elections.xlsx')
policies = pd.read_csv(CLEAN_DATA / 'prosecutor_policies_CLEANED.csv')
policies['county'] = policies['county'].str.replace(' County', '', regex=False)

# Calculate margins between 1st and 2nd place
def calculate_election_margins(df):
    """Calculate margin between 1st and 2nd place in general elections"""
    candidates = df[df['ran_general'] == 'Y'].copy()
    
    results = []
    for (district, year), group in candidates.groupby(['district', 'election_year']):
        group_sorted = group.sort_values('vote_percent_general', ascending=False)
        
        if len(group_sorted) == 0:
            continue
            
        first = group_sorted.iloc[0]
        second = group_sorted.iloc[1] if len(group_sorted) > 1 else None
        
        first_pct = first['vote_percent_general']
        second_pct = second['vote_percent_general'] if second is not None else 0.0
        margin = first_pct - second_pct
        
        results.append({
            'county': district,  # Renamed from district
            'election_year': year,
            'n_candidates': len(group_sorted),
            'winner_name': first['cand_fname'] + ' ' + first['cand_lname'],
            'winner_pct': first_pct,
            'runnerup_name': (second['cand_fname'] + ' ' + second['cand_lname']) if second is not None else None,
            'runnerup_pct': second_pct,
            'margin_1st_2nd': margin,  # KEY: This is the proper margin
            'winner_incum_chall': first['incum_chall'],
            'contested': first['general_contested_reconciled'],
            'tenure_start': year + 1,
            'tenure_end': year + 4
        })
    
    return pd.DataFrame(results)

election_margins = calculate_election_margins(elections)

print(f"\nElections analyzed: {len(election_margins)}")
print(f"\nMargin statistics (pp between 1st and 2nd):")
print(election_margins['margin_1st_2nd'].describe())

print("\n--- All Elections Sorted by Margin ---")
print(election_margins[['county', 'election_year', 'n_candidates', 'winner_name', 
                         'winner_pct', 'runnerup_pct', 'margin_1st_2nd']].sort_values('margin_1st_2nd'))

# Define close elections using different thresholds
print("\n--- Close Election Definitions ---")
for threshold in [5, 10, 15]:
    close_count = (election_margins['margin_1st_2nd'] <= threshold).sum()
    print(f"Margin ≤{threshold} pp: {close_count} elections ({100*close_count/len(election_margins):.1f}%)")

# Create close election indicators
election_margins['close_5pp'] = election_margins['margin_1st_2nd'] <= 5
election_margins['close_10pp'] = election_margins['margin_1st_2nd'] <= 10
election_margins['close_15pp'] = election_margins['margin_1st_2nd'] <= 15

# ============================================================================
# PART 2: MATCH POLICIES TO DAs WITH PROPER MARGINS
# ============================================================================

print("\n" + "="*80)
print("PART 2: MATCHING POLICIES TO DAs")
print("="*80)

def find_incumbent_da_with_margin(row, da_data):
    """Find which DA was incumbent when this policy was published"""
    county_das = da_data[da_data['county'] == row['county']]
    incumbent = county_das[
        (county_das['tenure_start'] <= row['year']) & 
        (county_das['tenure_end'] >= row['year'])
    ]
    if len(incumbent) == 0:
        # Return None for all columns except county
        null_series = pd.Series({col: None for col in da_data.columns if col != 'county'})
        return null_series
    incumbent = incumbent.sort_values('election_year').iloc[-1]
    # Return all columns except county
    return incumbent[[col for col in incumbent.index if col != 'county']]

# Match policies to incumbent DAs
incumbent_info = policies.apply(lambda row: find_incumbent_da_with_margin(row, election_margins), axis=1)
policies_matched = pd.concat([policies, incumbent_info], axis=1)

print(f"\nPolicies matched: {policies_matched['winner_name'].notna().sum()} / {len(policies_matched)}")

# ============================================================================
# PART 3: AGGREGATE POLICY CHARACTERISTICS
# ============================================================================

print("\n" + "="*80)
print("PART 3: AGGREGATING POLICY CHARACTERISTICS")
print("="*80)

def aggregate_policies_rich(group):
    """Aggregate with rich policy measures"""
    return pd.Series({
        'n_documents': len(group),
        'n_progressive': group['is_progressive'].sum(),
        'n_traditional': group['is_traditional'].sum(),
        'pct_progressive': group['is_progressive'].mean() * 100,
        'pct_traditional': group['is_traditional'].mean() * 100,
        'mean_ideology_score': group['ideology_score'].mean(),
        'pct_extensive_lenient': group['extensive_lenient'].mean() * 100,
        'pct_extensive_punitive': group['extensive_punitive'].mean() * 100,
        'pct_intensive_lenient': group['intensive_lenient'].mean() * 100,
        'pct_intensive_punitive': group['intensive_punitive'].mean() * 100,
        'pct_supports_diversion': ((group['supports_diversion_clean'] == 'yes').sum() / 
                                   group['supports_diversion_clean'].notna().sum() * 100 
                                   if group['supports_diversion_clean'].notna().sum() > 0 else np.nan),
        'pct_bail_reform': ((group['position_on_bail_clean'] == 'reform_oriented').sum() / 
                           group['position_on_bail_clean'].notna().sum() * 100 
                           if group['position_on_bail_clean'].notna().sum() > 0 else np.nan),
        'pct_racial_justice': ((group['racial_justice_emphasis_clean'] == 'high').sum() / 
                              group['racial_justice_emphasis_clean'].notna().sum() * 100 
                              if group['racial_justice_emphasis_clean'].notna().sum() > 0 else np.nan),
        # DA info (constant within group)
        'da_name': group['winner_name'].mode()[0] if group['winner_name'].notna().any() else None,
        'election_year': group['election_year'].mode()[0] if group['election_year'].notna().any() else None,
        'margin_1st_2nd': group['margin_1st_2nd'].mode()[0] if group['margin_1st_2nd'].notna().any() else None,
        'close_5pp': group['close_5pp'].mode()[0] if group['close_5pp'].notna().any() else None,
        'close_10pp': group['close_10pp'].mode()[0] if group['close_10pp'].notna().any() else None,
        'close_15pp': group['close_15pp'].mode()[0] if group['close_15pp'].notna().any() else None,
        'winner_pct': group['winner_pct'].mode()[0] if group['winner_pct'].notna().any() else None,
        'n_candidates': group['n_candidates'].mode()[0] if group['n_candidates'].notna().any() else None,
        'tenure_start': group['tenure_start'].mode()[0] if group['tenure_start'].notna().any() else None,
    })

county_year = policies_matched.groupby(['county', 'year']).apply(aggregate_policies_rich).reset_index()

print(f"\nCounty-year observations: {len(county_year)}")
print(f"With DA info: {county_year['da_name'].notna().sum()}")

# Calculate years into tenure
county_year['years_into_tenure'] = county_year['year'] - county_year['tenure_start'] + 1

# Filter to post-election (policies after DA took office)
post_election = county_year[(county_year['da_name'].notna()) & 
                            (county_year['years_into_tenure'] > 0)].copy()

print(f"Post-election observations: {len(post_election)}")

# ============================================================================
# PART 4: ANALYZE BY CLOSE ELECTION (PROPER DEFINITION)
# ============================================================================

print("\n" + "="*80)
print("PART 4: ANALYSIS BY CLOSE ELECTIONS (PROPER MARGINS)")
print("="*80)

# Function to compare close vs not close
def analyze_by_closeness(data, threshold_col, threshold_name):
    """Compare policies by election closeness"""
    print(f"\n{'='*60}")
    print(f"ANALYSIS: {threshold_name}")
    print(f"{'='*60}")
    
    close = data[data[threshold_col] == True]
    not_close = data[data[threshold_col] == False]
    
    print(f"\nSample sizes:")
    print(f"  Close elections: {len(close)} county-years, {close['n_documents'].sum():.0f} documents")
    print(f"  Not close: {len(not_close)} county-years, {not_close['n_documents'].sum():.0f} documents")
    
    print("\n1. IDEOLOGY")
    ideology_stats = data.groupby(threshold_col).agg({
        'pct_progressive': ['mean', 'std', 'count'],
        'pct_traditional': 'mean',
        'mean_ideology_score': 'mean'
    }).round(2)
    print(ideology_stats)
    
    # T-test for progressive
    if len(close) > 1 and len(not_close) > 1:
        t_stat, p_val = stats.ttest_ind(close['pct_progressive'].dropna(), 
                                        not_close['pct_progressive'].dropna(),
                                        equal_var=False)
        mean_diff = close['pct_progressive'].mean() - not_close['pct_progressive'].mean()
        print(f"\n  Progressive %: Close = {close['pct_progressive'].mean():.1f}%, Not Close = {not_close['pct_progressive'].mean():.1f}%")
        print(f"  Difference: {mean_diff:.1f} pp (t={t_stat:.2f}, p={p_val:.4f}{'***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else ''})")
    
    print("\n2. EXTENSIVE MARGIN")
    extensive_stats = data.groupby(threshold_col).agg({
        'pct_extensive_lenient': 'mean',
        'pct_extensive_punitive': 'mean'
    }).round(2)
    print(extensive_stats)
    
    print("\n3. INTENSIVE MARGIN")
    intensive_stats = data.groupby(threshold_col).agg({
        'pct_intensive_lenient': 'mean',
        'pct_intensive_punitive': 'mean'
    }).round(2)
    print(intensive_stats)
    
    print("\n4. SPECIFIC POLICIES")
    policy_stats = data.groupby(threshold_col).agg({
        'pct_supports_diversion': 'mean',
        'pct_bail_reform': 'mean',
        'pct_racial_justice': 'mean'
    }).round(2)
    print(policy_stats)
    
    return {
        'threshold': threshold_name,
        'n_close': len(close),
        'n_not_close': len(not_close),
        'prog_close': close['pct_progressive'].mean(),
        'prog_not_close': not_close['pct_progressive'].mean(),
        'diff': mean_diff if len(close) > 1 and len(not_close) > 1 else np.nan,
        'p_value': p_val if len(close) > 1 and len(not_close) > 1 else np.nan
    }

# Analyze with all three thresholds
results_5pp = analyze_by_closeness(post_election, 'close_5pp', 'Margin ≤5pp')
results_10pp = analyze_by_closeness(post_election, 'close_10pp', 'Margin ≤10pp')
results_15pp = analyze_by_closeness(post_election, 'close_15pp', 'Margin ≤15pp')

# ============================================================================
# PART 5: CORRELATION WITH ACTUAL MARGIN
# ============================================================================

print("\n" + "="*80)
print("PART 5: CORRELATIONS WITH 1ST-2ND PLACE MARGIN")
print("="*80)

policy_vars = [
    'pct_progressive', 'pct_traditional', 'mean_ideology_score',
    'pct_extensive_lenient', 'pct_intensive_lenient',
    'pct_supports_diversion', 'pct_bail_reform', 'pct_racial_justice'
]

print("\n--- Correlation: 1st-2nd Place Margin vs Policy ---")
print("(Negative = progressive policies with close margins)")

correlations = []
for var in policy_vars:
    valid_data = post_election[[var, 'margin_1st_2nd']].dropna()
    if len(valid_data) > 5:
        corr, p_val = stats.pearsonr(valid_data[var], valid_data['margin_1st_2nd'])
        correlations.append({
            'variable': var,
            'correlation': corr,
            'p_value': p_val,
            'n': len(valid_data),
            'sig': '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else ''
        })

corr_df = pd.DataFrame(correlations).sort_values('correlation')
print("\n" + corr_df.to_string(index=False))

# ============================================================================
# PART 6: MULTI-CANDIDATE RACES
# ============================================================================

print("\n" + "="*80)
print("PART 6: MULTI-CANDIDATE RACES (3+ candidates)")
print("="*80)

multi_candidate = post_election[post_election['n_candidates'] >= 3].copy()
two_candidate = post_election[post_election['n_candidates'] == 2].copy()

print(f"\nMulti-candidate races: {len(multi_candidate)} county-years")
print(f"Two-candidate races: {len(two_candidate)} county-years")

if len(multi_candidate) > 0:
    print("\n--- Multi-Candidate Race Details ---")
    print(multi_candidate[['county', 'year', 'da_name', 'winner_pct', 'margin_1st_2nd', 
                           'pct_progressive', 'pct_traditional']].to_string(index=False))
    
    print(f"\n--- Policy Comparison ---")
    print(f"Multi-candidate (3+): {multi_candidate['pct_progressive'].mean():.1f}% progressive")
    print(f"Two-candidate: {two_candidate['pct_progressive'].mean():.1f}% progressive")

# ============================================================================
# PART 7: REGRESSION ANALYSIS
# ============================================================================

print("\n" + "="*80)
print("PART 7: REGRESSION ANALYSIS")
print("="*80)

from sklearn.linear_model import LinearRegression

reg_data = post_election[['margin_1st_2nd', 'pct_progressive', 'year']].dropna()

if len(reg_data) > 10:
    print(f"\nRegression sample: {len(reg_data)} observations")
    
    # Simple regression
    X = reg_data[['margin_1st_2nd']].values
    y = reg_data['pct_progressive'].values
    
    model = LinearRegression()
    model.fit(X, y)
    r_squared = model.score(X, y)
    
    print(f"\nSimple Regression: Progressive % = β0 + β1*(1st-2nd Margin)")
    print(f"  β1 (margin coef): {model.coef_[0]:.3f}")
    print(f"  β0 (intercept): {model.intercept_:.3f}")
    print(f"  R-squared: {r_squared:.3f}")
    print(f"\nInterpretation: Each 1 pp increase in margin between 1st and 2nd")
    print(f"  → {model.coef_[0]:.2f} pp change in progressive policies")
    
    # Multiple regression
    X_multi = reg_data[['margin_1st_2nd', 'year']].values
    model_multi = LinearRegression()
    model_multi.fit(X_multi, y)
    
    print(f"\nMultiple Regression (controlling for year):")
    print(f"  Margin coef: {model_multi.coef_[0]:.3f}")
    print(f"  Year coef: {model_multi.coef_[1]:.3f}")
    print(f"  R-squared: {model_multi.score(X_multi, y):.3f}")

# ============================================================================
# PART 8: SAVE RESULTS
# ============================================================================

print("\n" + "="*80)
print("PART 8: SAVING RESULTS")
print("="*80)

# Save main datasets
post_election.to_csv(RESULTS_DATA / 'final_post_election_analysis.csv', index=False)
print("Saved: final_post_election_analysis.csv")

election_margins.to_csv(RESULTS_DATA / 'election_margins_1st_2nd.csv', index=False)
print("Saved: election_margins_1st_2nd.csv")

corr_df.to_csv(RESULTS_DATA / 'margin_correlations_proper.csv', index=False)
print("Saved: margin_correlations_proper.csv")

# Save summary of results
summary_results = pd.DataFrame([results_5pp, results_10pp, results_15pp])
summary_results.to_csv(RESULTS_DATA / 'close_election_thresholds_comparison.csv', index=False)
print("Saved: close_election_thresholds_comparison.csv")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)

# Print final summary
print("\n" + "="*80)
print("FINAL SUMMARY")
print("="*80)

print("\n--- Close Election Effects by Threshold ---")
print(summary_results[['threshold', 'n_close', 'n_not_close', 'prog_close', 
                       'prog_not_close', 'diff', 'p_value']].to_string(index=False))

print("\n--- Key Multi-Candidate Races ---")
multi_summary = election_margins[election_margins['n_candidates'] >= 3][
    ['county', 'election_year', 'winner_name', 'winner_pct', 'runnerup_pct', 'margin_1st_2nd']
]
print(multi_summary.to_string(index=False))
