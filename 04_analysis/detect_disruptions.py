"""
Detect Policy Disruptions - Runner Script
=========================================
Run the disruption detection pipeline on prosecutor policy data.

Usage:
    python detect_disruptions.py

Output files (in ./output/):
    - policy_disruptions.csv
    - novel_reforms.csv
    - disruption_summary.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
from disruption_detector import DisruptionDetector

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / '05_data'
OUTPUT_DIR = DATA_DIR / 'results'

POLICY_FILE = DATA_DIR / 'clean' / 'prosecutor_policies_CLEANED.csv'
ELECTION_FILE = DATA_DIR / 'results' / 'election_margins_1st_2nd.csv'


def main():
    print("=" * 80)
    print("POLICY DISRUPTION DETECTION")
    print("=" * 80)

    # Load policy data
    print(f"\nLoading policy data from {POLICY_FILE}...")
    policies = pd.read_csv(POLICY_FILE)
    print(f"  Loaded {len(policies)} documents")
    print(f"  Counties: {policies['county'].nunique()}")
    print(f"  Years: {policies['year'].min():.0f} - {policies['year'].max():.0f}")

    # Load election data
    elections = None
    if ELECTION_FILE.exists():
        print(f"\nLoading election data from {ELECTION_FILE}...")
        elections = pd.read_csv(ELECTION_FILE)
        print(f"  Loaded {len(elections)} election records")
    else:
        print(f"\nWarning: Election file not found at {ELECTION_FILE}")
        print("  Proceeding without election data linkage")

    # Initialize detector
    print("\nInitializing disruption detector...")
    detector = DisruptionDetector(policies, elections)

    # Run detection
    print("\n" + "=" * 80)
    print("RUNNING DETECTION")
    print("=" * 80)
    results = detector.run_full_detection(min_docs=3, lookback=2)

    # Display top disruptions
    print("\n" + "=" * 80)
    print("TOP DISRUPTIONS (by score)")
    print("=" * 80)

    disruptions = results['disruptions']
    top_disruptions = disruptions.nlargest(15, 'disruption_score')[
        ['county', 'year', 'disruption_score', 'disruption_classification',
         'direction', 'ideology_velocity', 'novelty_index', 'n_documents']
    ]
    print(top_disruptions.to_string(index=False))

    # Display major disruptions
    print("\n" + "=" * 80)
    print("MAJOR DISRUPTIONS (score >= 0.75)")
    print("=" * 80)

    major = disruptions[disruptions['disruption_classification'] == 'major_disruption']
    if len(major) > 0:
        print(major[['county', 'year', 'disruption_score', 'direction',
                     'ideology_velocity', 'da_transition_signal']].to_string(index=False))
    else:
        print("No major disruptions detected")

    # Display significant disruptions
    print("\n" + "=" * 80)
    print("SIGNIFICANT DISRUPTIONS (score 0.50-0.74)")
    print("=" * 80)

    significant = disruptions[disruptions['disruption_classification'] == 'significant_disruption']
    if len(significant) > 0:
        print(significant[['county', 'year', 'disruption_score', 'direction',
                          'ideology_velocity', 'da_transition_signal']].to_string(index=False))
    else:
        print("No significant disruptions detected")

    # Display novel reforms
    print("\n" + "=" * 80)
    print("NOVEL REFORMS (first appearances)")
    print("=" * 80)

    novel = results['novel_reforms']
    if len(novel) > 0:
        # Show statewide firsts
        statewide_firsts = novel[novel['statewide_first'] == True]
        print(f"\nStatewide First Appearances ({len(statewide_firsts)} reforms):")
        if len(statewide_firsts) > 0:
            print(statewide_firsts[['county', 'year', 'reform_type', 'reform_name']].head(20).to_string(index=False))

        # Novel reforms by year
        print("\n\nNovel Reforms by Year:")
        novel_by_year = novel.groupby('year').size()
        print(novel_by_year.tail(10))

        # Most common novel reform types
        print("\n\nMost Common Novel Reforms:")
        print(novel['reform_name'].value_counts().head(10))
    else:
        print("No novel reforms detected")

    # Display summary
    print("\n" + "=" * 80)
    print("COUNTY SUMMARY")
    print("=" * 80)

    summary = results['summary']
    if len(summary) > 0:
        print(summary.head(15).to_string(index=False))

    # Validation checks
    print("\n" + "=" * 80)
    print("VALIDATION CHECKS")
    print("=" * 80)

    # Check LA County 2021 (Gascon)
    la_2021 = disruptions[
        (disruptions['county'] == 'Los Angeles County') &
        (disruptions['year'] == 2021)
    ]
    if len(la_2021) > 0:
        score = la_2021.iloc[0]['disruption_score']
        classification = la_2021.iloc[0]['disruption_classification']
        print(f"\n[OK] LA County 2021 (Gascon): score={score:.3f}, class={classification}")
        if classification in ['major_disruption', 'significant_disruption']:
            print("  -> PASS: Detected as major/significant disruption")
        else:
            print("  -> WARNING: Expected major/significant disruption")
    else:
        print("\n[X] LA County 2021: No data found")

    # Check SF 2020 (Boudin)
    sf_2020 = disruptions[
        (disruptions['county'] == 'San Francisco County') &
        (disruptions['year'] == 2020)
    ]
    if len(sf_2020) > 0:
        score = sf_2020.iloc[0]['disruption_score']
        classification = sf_2020.iloc[0]['disruption_classification']
        print(f"\n[OK] SF County 2020 (Boudin): score={score:.3f}, class={classification}")
        if classification in ['major_disruption', 'significant_disruption']:
            print("  -> PASS: Detected as major/significant disruption")
        else:
            print("  -> WARNING: Expected major/significant disruption")
    else:
        print("\n[X] SF County 2020: No data found")

    # Check Stanislaus (should be stable)
    stanislaus = disruptions[disruptions['county'] == 'Stanislaus County']
    if len(stanislaus) > 0:
        max_score = stanislaus['disruption_score'].max()
        n_stable = (stanislaus['disruption_classification'] == 'stable').sum()
        print(f"\n[OK] Stanislaus County: max_score={max_score:.3f}, {n_stable}/{len(stanislaus)} stable")
        if max_score < 0.5:
            print("  -> PASS: Consistently traditional/stable")
        else:
            print("  -> NOTE: Some disruption detected (expected for 2018 progressive shift)")
    else:
        print("\n[X] Stanislaus County: No data found")

    # 2020 statewide check
    year_2020 = disruptions[disruptions['year'] == 2020]
    if len(year_2020) > 0:
        mean_score = year_2020['disruption_score'].mean()
        n_progressive = (year_2020['direction'] == 'progressive').sum()
        print(f"\n[OK] 2020 Statewide: mean_score={mean_score:.3f}, {n_progressive}/{len(year_2020)} progressive direction")
    else:
        print("\n[X] 2020: No data found")

    # Export results
    print("\n" + "=" * 80)
    print("EXPORTING RESULTS")
    print("=" * 80)

    detector.export_results(OUTPUT_DIR)

    print("\n" + "=" * 80)
    print("DETECTION COMPLETE")
    print("=" * 80)

    # Print file locations
    print(f"\nOutput files saved to: {OUTPUT_DIR}")
    print("  - policy_disruptions.csv")
    print("  - novel_reforms.csv")
    print("  - disruption_summary.csv")


if __name__ == '__main__':
    main()
