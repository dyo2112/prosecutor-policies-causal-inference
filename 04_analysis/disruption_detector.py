"""
Policy Disruption Detection System
==================================
Detects when a DA office adopted a new direction or novel reform.

Disruption Signals:
1. ideology_velocity - Rate of change in mean ideology score
2. novelty_index - Proportion of documents marked as clearly_new_policy
3. topic_shift_score - Jensen-Shannon divergence of topic distributions
4. margin_reversal_score - Change in extensive/intensive margin leniency
5. da_transition_signal - New DA administration appears in documents

Output:
- policy_disruptions.csv - County-year disruption scores
- novel_reforms.csv - First-time policy types by county
- disruption_summary.csv - Per-county summary statistics
"""

import pandas as pd
import numpy as np
from scipy.spatial.distance import jensenshannon
from scipy import stats
from typing import Optional, Dict, List, Tuple
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


class DisruptionDetector:
    """Main class for detecting policy disruptions in prosecutor offices."""

    # Default weights for composite score
    DEFAULT_WEIGHTS = {
        'ideology_velocity': 0.30,
        'novelty_index': 0.25,
        'topic_shift_score': 0.20,
        'margin_reversal_score': 0.15,
        'da_transition_signal': 0.10
    }

    # Classification thresholds
    CLASSIFICATION_THRESHOLDS = {
        'major_disruption': 0.75,
        'significant_disruption': 0.50,
        'moderate_disruption': 0.25,
        'minor_disruption': 0.10
    }

    def __init__(self, policy_df: pd.DataFrame, election_df: Optional[pd.DataFrame] = None):
        """
        Initialize the disruption detector.

        Args:
            policy_df: DataFrame with prosecutor policy data (prosecutor_policies_CLEANED.csv)
            election_df: Optional DataFrame with election margins (election_margins_1st_2nd.csv)
        """
        self.df = policy_df.copy()
        self.elections = election_df.copy() if election_df is not None else None

        # Ensure date column is datetime
        if 'date' in self.df.columns:
            self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')

        # Ensure year column exists
        if 'year' not in self.df.columns and 'date' in self.df.columns:
            self.df['year'] = self.df['date'].dt.year

        # Results storage
        self.disruptions = None
        self.novel_reforms = None
        self.summary = None

        # Get valid counties and years
        self.counties = self.df['county'].unique()
        self.years = sorted(self.df['year'].dropna().unique())

    def calculate_ideology_velocity(self, county: str, year: int, lookback: int = 2) -> float:
        """
        Calculate rate of ideology change compared to prior period.

        Args:
            county: County name
            year: Target year
            lookback: Number of years to look back for baseline

        Returns:
            Ideology velocity (positive = progressive shift, negative = traditional shift)
        """
        county_df = self.df[self.df['county'] == county]

        # Current period
        current = county_df[county_df['year'] == year]['ideology_score'].dropna()
        if len(current) == 0:
            return 0.0
        current_mean = current.mean()

        # Prior period
        prior = county_df[
            (county_df['year'] >= year - lookback) &
            (county_df['year'] < year)
        ]['ideology_score'].dropna()

        if len(prior) == 0:
            return 0.0
        prior_mean = prior.mean()

        return current_mean - prior_mean

    def calculate_novelty_index(self, county: str, year: int) -> float:
        """
        Calculate proportion of documents marked as clearly_new_policy.

        Args:
            county: County name
            year: Target year

        Returns:
            Novelty index (0-1)
        """
        county_year = self.df[
            (self.df['county'] == county) &
            (self.df['year'] == year)
        ]

        if len(county_year) == 0:
            return 0.0

        n_new = (county_year['policy_change_clean'] == 'clearly_new_policy').sum()
        return n_new / len(county_year)

    def calculate_topic_shift(self, county: str, year: int, lookback: int = 2) -> float:
        """
        Calculate Jensen-Shannon divergence between topic distributions.

        Args:
            county: County name
            year: Target year
            lookback: Number of years to look back for baseline

        Returns:
            Topic shift score (0-1, higher = more different)
        """
        county_df = self.df[self.df['county'] == county]

        # Current period topics
        current = county_df[county_df['year'] == year]['primary_topic_clean']
        current = current[current.notna()]

        # Prior period topics
        prior = county_df[
            (county_df['year'] >= year - lookback) &
            (county_df['year'] < year)
        ]['primary_topic_clean']
        prior = prior[prior.notna()]

        if len(current) == 0 or len(prior) == 0:
            return 0.0

        # Get all unique topics
        all_topics = list(set(current.unique()) | set(prior.unique()))

        # Create frequency distributions
        current_counts = current.value_counts()
        prior_counts = prior.value_counts()

        current_dist = np.array([current_counts.get(t, 0) for t in all_topics])
        prior_dist = np.array([prior_counts.get(t, 0) for t in all_topics])

        # Normalize to probabilities
        current_dist = current_dist / current_dist.sum() if current_dist.sum() > 0 else current_dist
        prior_dist = prior_dist / prior_dist.sum() if prior_dist.sum() > 0 else prior_dist

        # Add small epsilon to avoid division by zero
        epsilon = 1e-10
        current_dist = current_dist + epsilon
        prior_dist = prior_dist + epsilon
        current_dist = current_dist / current_dist.sum()
        prior_dist = prior_dist / prior_dist.sum()

        return jensenshannon(current_dist, prior_dist)

    def calculate_margin_reversal(self, county: str, year: int, lookback: int = 2) -> Tuple[float, bool, bool]:
        """
        Detect margin strategy reversals.

        Args:
            county: County name
            year: Target year
            lookback: Number of years to look back for baseline

        Returns:
            Tuple of (score, extensive_reversal, intensive_reversal)
        """
        county_df = self.df[self.df['county'] == county]

        # Current period
        current = county_df[county_df['year'] == year]
        prior = county_df[
            (county_df['year'] >= year - lookback) &
            (county_df['year'] < year)
        ]

        if len(current) == 0 or len(prior) == 0:
            return 0.0, False, False

        # Calculate net leniency for each margin
        def net_leniency(df, lenient_col, punitive_col):
            lenient = df[lenient_col].sum() if lenient_col in df.columns else 0
            punitive = df[punitive_col].sum() if punitive_col in df.columns else 0
            total = len(df)
            return (lenient - punitive) / total if total > 0 else 0

        ext_prior = net_leniency(prior, 'extensive_lenient', 'extensive_punitive')
        ext_current = net_leniency(current, 'extensive_lenient', 'extensive_punitive')

        int_prior = net_leniency(prior, 'intensive_lenient', 'intensive_punitive')
        int_current = net_leniency(current, 'intensive_lenient', 'intensive_punitive')

        # Detect sign reversals
        ext_reversal = (ext_prior * ext_current < 0) and (abs(ext_prior) > 0.05 or abs(ext_current) > 0.05)
        int_reversal = (int_prior * int_current < 0) and (abs(int_prior) > 0.05 or abs(int_current) > 0.05)

        # Magnitude of change
        score = abs(ext_current - ext_prior) + abs(int_current - int_prior)

        return score, ext_reversal, int_reversal

    def detect_da_transition(self, county: str, year: int, lookback: int = 2) -> int:
        """
        Detect if a new DA administration appears in documents.

        Args:
            county: County name
            year: Target year
            lookback: Number of years to look back for baseline

        Returns:
            1 if new DA detected, 0 otherwise
        """
        county_df = self.df[self.df['county'] == county]

        # Current DA names
        current = county_df[county_df['year'] == year]['da_administration_clean']
        current = set(current[current.notna() & (current != 'not_mentioned')].unique())

        # Prior DA names
        prior = county_df[
            (county_df['year'] >= year - lookback) &
            (county_df['year'] < year)
        ]['da_administration_clean']
        prior = set(prior[prior.notna() & (prior != 'not_mentioned')].unique())

        # New DA names that weren't in prior period
        new_das = current - prior

        return 1 if len(new_das) > 0 else 0

    def normalize_signal(self, values: pd.Series, method: str = 'minmax') -> pd.Series:
        """Normalize signal values to 0-1 range."""
        if len(values) == 0 or values.isna().all():
            return values

        if method == 'minmax':
            min_val = values.min()
            max_val = values.max()
            if max_val == min_val:
                return pd.Series([0.5] * len(values), index=values.index)
            return (values - min_val) / (max_val - min_val)
        elif method == 'zscore':
            mean_val = values.mean()
            std_val = values.std()
            if std_val == 0:
                return pd.Series([0.5] * len(values), index=values.index)
            z = (values - mean_val) / std_val
            # Convert z-scores to 0-1 range using sigmoid
            return 1 / (1 + np.exp(-z))
        else:
            return values

    def classify_disruption(self, score: float) -> str:
        """Convert numeric score to classification."""
        if score >= self.CLASSIFICATION_THRESHOLDS['major_disruption']:
            return 'major_disruption'
        elif score >= self.CLASSIFICATION_THRESHOLDS['significant_disruption']:
            return 'significant_disruption'
        elif score >= self.CLASSIFICATION_THRESHOLDS['moderate_disruption']:
            return 'moderate_disruption'
        elif score >= self.CLASSIFICATION_THRESHOLDS['minor_disruption']:
            return 'minor_disruption'
        else:
            return 'stable'

    def compute_disruption_score(
        self,
        county: str,
        year: int,
        weights: Optional[Dict[str, float]] = None,
        lookback: int = 2
    ) -> Dict:
        """
        Compute composite disruption score for a county-year.

        Args:
            county: County name
            year: Target year
            weights: Optional custom weights for signals
            lookback: Number of years to look back for baseline

        Returns:
            Dictionary with all signals and composite score
        """
        if weights is None:
            weights = self.DEFAULT_WEIGHTS

        # Calculate individual signals
        ideology_velocity = self.calculate_ideology_velocity(county, year, lookback)
        novelty_index = self.calculate_novelty_index(county, year)
        topic_shift_score = self.calculate_topic_shift(county, year, lookback)
        margin_reversal_score, ext_reversal, int_reversal = self.calculate_margin_reversal(county, year, lookback)
        da_transition_signal = self.detect_da_transition(county, year, lookback)

        # Get document counts and stats
        county_year = self.df[
            (self.df['county'] == county) &
            (self.df['year'] == year)
        ]
        n_documents = len(county_year)
        n_new_policies = (county_year['policy_change_clean'] == 'clearly_new_policy').sum()
        mean_ideology = county_year['ideology_score'].mean() if len(county_year) > 0 else np.nan

        # Get prior mean ideology
        prior = self.df[
            (self.df['county'] == county) &
            (self.df['year'] >= year - lookback) &
            (self.df['year'] < year)
        ]
        prior_mean_ideology = prior['ideology_score'].mean() if len(prior) > 0 else np.nan

        # Determine direction of change
        if ideology_velocity > 0.1:
            direction = 'progressive'
        elif ideology_velocity < -0.1:
            direction = 'traditional'
        else:
            direction = 'neutral'

        # Get primary topics for this county-year
        primary_topics = county_year['primary_topic_clean'].value_counts().head(3).index.tolist()

        return {
            'county': county,
            'year': year,
            'ideology_velocity': ideology_velocity,
            'novelty_index': novelty_index,
            'topic_shift_score': topic_shift_score,
            'margin_reversal_score': margin_reversal_score,
            'extensive_reversal': ext_reversal,
            'intensive_reversal': int_reversal,
            'da_transition_signal': da_transition_signal,
            'direction': direction,
            'n_documents': n_documents,
            'n_new_policies': n_new_policies,
            'mean_ideology_score': mean_ideology,
            'prior_mean_ideology': prior_mean_ideology,
            'primary_topics': primary_topics
        }

    def detect_novel_reforms(self) -> pd.DataFrame:
        """
        Identify first-time policy types by county.

        Returns:
            DataFrame of novel reforms with county, year, reform details
        """
        novel_reforms = []

        # Track first appearance of topics statewide
        statewide_first_topics = {}

        for county in self.counties:
            county_df = self.df[self.df['county'] == county].sort_values('year')

            seen_topics = set()
            seen_positions = {}

            for idx, row in county_df.iterrows():
                year = row['year']
                if pd.isna(year):
                    continue
                year = int(year)

                # Track novel primary topics
                topic = row['primary_topic_clean']
                if pd.notna(topic) and topic not in seen_topics:
                    # Check if statewide first
                    statewide_first = False
                    if topic not in statewide_first_topics:
                        statewide_first_topics[topic] = (county, year)
                        statewide_first = True

                    novel_reforms.append({
                        'county': county,
                        'year': year,
                        'reform_type': 'novel_topic',
                        'reform_name': topic,
                        'document': row['filename'],
                        'ideology_score': row['ideology_score'],
                        'statewide_first': statewide_first
                    })
                    seen_topics.add(topic)

                # Track novel policy positions
                position_cols = [
                    ('supports_diversion_clean', 'yes', 'diversion_support'),
                    ('supports_alternatives_clean', 'yes', 'alternatives_support'),
                    ('position_on_bail_clean', 'reform_oriented', 'bail_reform'),
                    ('position_on_enhancements_clean', 'minimize', 'enhancement_limits'),
                    ('racial_justice_emphasis_clean', 'high', 'racial_justice_high'),
                ]

                for col, trigger_value, reform_name in position_cols:
                    if col in row.index:
                        value = row[col]
                        if value == trigger_value:
                            if reform_name not in seen_positions:
                                novel_reforms.append({
                                    'county': county,
                                    'year': year,
                                    'reform_type': 'novel_position',
                                    'reform_name': reform_name,
                                    'document': row['filename'],
                                    'ideology_score': row['ideology_score'],
                                    'statewide_first': False  # Will calculate below
                                })
                                seen_positions[reform_name] = year

        # Convert to DataFrame
        novel_df = pd.DataFrame(novel_reforms)

        if len(novel_df) > 0:
            # Calculate adoption rank (order of county adoption for each reform)
            novel_df['adoption_rank'] = novel_df.groupby('reform_name')['year'].rank(method='dense')

            # Sort by year
            novel_df = novel_df.sort_values(['year', 'county']).reset_index(drop=True)

        self.novel_reforms = novel_df
        return novel_df

    def detect_gradual_acceleration(self, county: str, window: int = 3) -> pd.Series:
        """
        Detect sustained directional change over multiple years.

        Args:
            county: County name
            window: Rolling window size for trend calculation

        Returns:
            Series of acceleration scores by year
        """
        county_df = self.df[self.df['county'] == county]

        # Calculate yearly mean ideology
        yearly_means = county_df.groupby('year')['ideology_score'].mean()

        if len(yearly_means) < window:
            return pd.Series()

        # Calculate rolling slope (trend)
        def calculate_slope(x):
            if len(x) < 2:
                return 0
            return np.polyfit(range(len(x)), x, 1)[0]

        rolling_trend = yearly_means.rolling(window).apply(calculate_slope)

        return rolling_trend

    def link_to_elections(self) -> pd.DataFrame:
        """
        Match disruptions to DA election events.

        Returns:
            Disruptions DataFrame with election information added
        """
        if self.disruptions is None:
            raise ValueError("Must run run_full_detection() first")

        if self.elections is None:
            print("Warning: No election data provided. Skipping election linkage.")
            return self.disruptions

        # Standardize county names
        elections = self.elections.copy()
        if 'county' not in elections.columns and 'district' in elections.columns:
            elections['county'] = elections['district']

        # Create election lookup by county and tenure_start
        election_cols = ['election_year', 'winner_name', 'margin_1st_2nd',
                        'close_5pp', 'close_10pp', 'close_15pp', 'n_candidates',
                        'winner_incum_chall']

        # Match disruptions to elections
        matched = []
        for idx, row in self.disruptions.iterrows():
            county = row['county'].replace(' County', '')
            year = row['year']

            # Find matching election (where tenure_start <= year <= tenure_end)
            county_elections = elections[elections['county'] == county]
            incumbent = county_elections[
                (county_elections['tenure_start'] <= year) &
                (county_elections['tenure_end'] >= year)
            ]

            match_data = row.to_dict()

            if len(incumbent) > 0:
                election = incumbent.sort_values('election_year').iloc[-1]
                for col in election_cols:
                    if col in election.index:
                        match_data[col] = election[col]
                match_data['challenger_won'] = election.get('winner_incum_chall') == 'C'
            else:
                for col in election_cols:
                    match_data[col] = None
                match_data['challenger_won'] = None

            matched.append(match_data)

        self.disruptions = pd.DataFrame(matched)
        return self.disruptions

    def run_full_detection(self, min_docs: int = 3, lookback: int = 2) -> Dict:
        """
        Execute complete disruption detection pipeline.

        Args:
            min_docs: Minimum documents in a county-year to analyze
            lookback: Years to look back for baseline comparison

        Returns:
            Dictionary with disruptions, novel_reforms, and summary DataFrames
        """
        print("Running disruption detection...")

        # Calculate disruption scores for all county-years
        results = []

        for county in self.counties:
            county_years = self.df[self.df['county'] == county]['year'].dropna().unique()

            for year in sorted(county_years):
                year = int(year)

                # Check minimum documents
                n_docs = len(self.df[
                    (self.df['county'] == county) &
                    (self.df['year'] == year)
                ])
                if n_docs < min_docs:
                    continue

                # Compute disruption score
                result = self.compute_disruption_score(county, year, lookback=lookback)
                results.append(result)

        # Convert to DataFrame
        self.disruptions = pd.DataFrame(results)

        if len(self.disruptions) == 0:
            print("No disruptions detected (insufficient data)")
            return {'disruptions': self.disruptions, 'novel_reforms': pd.DataFrame(), 'summary': pd.DataFrame()}

        # Normalize signals and compute composite score
        signal_cols = ['ideology_velocity', 'novelty_index', 'topic_shift_score', 'margin_reversal_score']

        for col in signal_cols:
            self.disruptions[f'{col}_norm'] = self.normalize_signal(
                self.disruptions[col].abs(), method='minmax'
            )

        # Compute composite score
        weights = self.DEFAULT_WEIGHTS
        self.disruptions['disruption_score'] = (
            weights['ideology_velocity'] * self.disruptions['ideology_velocity_norm'] +
            weights['novelty_index'] * self.disruptions['novelty_index_norm'] +
            weights['topic_shift_score'] * self.disruptions['topic_shift_score_norm'] +
            weights['margin_reversal_score'] * self.disruptions['margin_reversal_score_norm'] +
            weights['da_transition_signal'] * self.disruptions['da_transition_signal']
        )

        # Classify disruptions
        self.disruptions['disruption_classification'] = self.disruptions['disruption_score'].apply(
            self.classify_disruption
        )

        # Detect novel reforms
        print("Detecting novel reforms...")
        self.detect_novel_reforms()

        # Link to elections if available
        if self.elections is not None:
            print("Linking to election data...")
            self.link_to_elections()

        # Generate summary
        print("Generating summary statistics...")
        self.summary = self._generate_summary()

        print(f"Detection complete: {len(self.disruptions)} county-years analyzed")
        print(f"  Major disruptions: {(self.disruptions['disruption_classification'] == 'major_disruption').sum()}")
        print(f"  Significant disruptions: {(self.disruptions['disruption_classification'] == 'significant_disruption').sum()}")
        print(f"  Novel reforms detected: {len(self.novel_reforms)}")

        return {
            'disruptions': self.disruptions,
            'novel_reforms': self.novel_reforms,
            'summary': self.summary
        }

    def _generate_summary(self) -> pd.DataFrame:
        """Generate per-county summary statistics."""
        if self.disruptions is None:
            return pd.DataFrame()

        summary = []
        for county in self.disruptions['county'].unique():
            county_data = self.disruptions[self.disruptions['county'] == county]

            n_disruptions = len(county_data[county_data['disruption_classification'] != 'stable'])
            n_major = (county_data['disruption_classification'] == 'major_disruption').sum()

            first_disruption = county_data[
                county_data['disruption_classification'] != 'stable'
            ]['year'].min() if n_disruptions > 0 else None

            max_idx = county_data['disruption_score'].idxmax()
            most_disruptive_year = county_data.loc[max_idx, 'year'] if pd.notna(max_idx) else None
            max_score = county_data['disruption_score'].max()

            # Dominant direction
            directions = county_data[county_data['direction'] != 'neutral']['direction']
            dominant_direction = directions.mode()[0] if len(directions) > 0 else 'neutral'

            # Novel reforms for this county
            n_novel = len(self.novel_reforms[self.novel_reforms['county'] == county]) if self.novel_reforms is not None else 0

            summary.append({
                'county': county,
                'n_county_years': len(county_data),
                'n_disruptions': n_disruptions,
                'n_major_disruptions': n_major,
                'first_disruption_year': first_disruption,
                'most_disruptive_year': most_disruptive_year,
                'max_disruption_score': max_score,
                'dominant_direction': dominant_direction,
                'n_novel_reforms': n_novel
            })

        return pd.DataFrame(summary).sort_values('max_disruption_score', ascending=False)

    def export_results(self, output_dir: str) -> None:
        """
        Export all results to CSV files.

        Args:
            output_dir: Directory to save output files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        if self.disruptions is not None and len(self.disruptions) > 0:
            # Select columns for export (exclude normalized and list columns)
            export_cols = [
                'county', 'year', 'disruption_score', 'disruption_classification', 'direction',
                'ideology_velocity', 'novelty_index', 'topic_shift_score', 'margin_reversal_score',
                'da_transition_signal', 'extensive_reversal', 'intensive_reversal',
                'n_documents', 'n_new_policies', 'mean_ideology_score', 'prior_mean_ideology'
            ]

            # Add election columns if present
            election_cols = ['election_year', 'winner_name', 'margin_1st_2nd', 'close_5pp',
                           'close_10pp', 'close_15pp', 'challenger_won']
            for col in election_cols:
                if col in self.disruptions.columns:
                    export_cols.append(col)

            export_df = self.disruptions[[c for c in export_cols if c in self.disruptions.columns]]
            export_df.to_csv(output_path / 'policy_disruptions.csv', index=False)
            print(f"Saved: {output_path / 'policy_disruptions.csv'}")

        if self.novel_reforms is not None and len(self.novel_reforms) > 0:
            self.novel_reforms.to_csv(output_path / 'novel_reforms.csv', index=False)
            print(f"Saved: {output_path / 'novel_reforms.csv'}")

        if self.summary is not None and len(self.summary) > 0:
            self.summary.to_csv(output_path / 'disruption_summary.csv', index=False)
            print(f"Saved: {output_path / 'disruption_summary.csv'}")

    def generate_validation_report(self, county: str, year: int) -> Dict:
        """
        Create evidence summary for manual review of a detected disruption.

        Args:
            county: County name
            year: Year of disruption

        Returns:
            Dictionary with quantitative and qualitative evidence
        """
        county_df = self.df[self.df['county'] == county]
        current = county_df[county_df['year'] == year]
        prior = county_df[county_df['year'] < year]

        return {
            'county': county,
            'year': year,

            # Quantitative evidence
            'n_documents': len(current),
            'ideology_change': current['ideology_score'].mean() - prior['ideology_score'].mean() if len(prior) > 0 else None,
            'n_new_policies': (current['policy_change_clean'] == 'clearly_new_policy').sum(),
            'pct_progressive': current['is_progressive'].mean() * 100 if len(current) > 0 else None,

            # Topic distribution
            'current_topics': current['primary_topic_clean'].value_counts().head(5).to_dict(),
            'prior_topics': prior['primary_topic_clean'].value_counts().head(5).to_dict() if len(prior) > 0 else {},

            # DA administration
            'da_mentioned': current['da_administration_clean'].value_counts().head(3).to_dict(),

            # Sample documents
            'sample_new_policies': current[
                current['policy_change_clean'] == 'clearly_new_policy'
            ][['filename', 'primary_topic_clean', 'ideology_score']].head(3).to_dict('records')
        }


def main():
    """Main function for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(description='Detect policy disruptions in prosecutor offices')
    parser.add_argument('--policy-file', type=str, required=True, help='Path to prosecutor_policies_CLEANED.csv')
    parser.add_argument('--election-file', type=str, help='Path to election_margins_1st_2nd.csv (optional)')
    parser.add_argument('--output-dir', type=str, default='./output', help='Output directory')
    parser.add_argument('--min-docs', type=int, default=3, help='Minimum documents per county-year')
    parser.add_argument('--lookback', type=int, default=2, help='Years to look back for baseline')

    args = parser.parse_args()

    # Load data
    print(f"Loading policy data from {args.policy_file}...")
    policies = pd.read_csv(args.policy_file)

    elections = None
    if args.election_file:
        print(f"Loading election data from {args.election_file}...")
        elections = pd.read_csv(args.election_file)

    # Run detection
    detector = DisruptionDetector(policies, elections)
    results = detector.run_full_detection(min_docs=args.min_docs, lookback=args.lookback)

    # Export results
    detector.export_results(args.output_dir)

    print("\nDone!")


if __name__ == '__main__':
    main()
