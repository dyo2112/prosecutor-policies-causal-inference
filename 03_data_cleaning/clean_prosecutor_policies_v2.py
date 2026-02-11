"""
COMPREHENSIVE Data Cleaning Script for Prosecutor Policies
Handles multiple data sources: JSON columns, individual columns, and hybrid fields
"""

import pandas as pd
import numpy as np
import json
import ast
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
INPUT_FILE = PROJECT_ROOT / '05_data' / 'intermediate' / 'coded_prosecutor_policies.csv'
OUTPUT_FILE = PROJECT_ROOT / '05_data' / 'clean' / 'prosecutor_policies_CLEANED.csv'


def safe_parse_json(value):
    """Safely parse JSON/dict strings"""
    if pd.isna(value):
        return None
    
    if isinstance(value, dict):
        return value
    
    if not isinstance(value, str):
        return None
    
    # Skip if it's a simple string (not JSON)
    if not value.strip().startswith('{'):
        return None
    
    # Try ast.literal_eval (handles Python dicts with single quotes)
    try:
        return ast.literal_eval(value)
    except:
        pass
    
    # Try JSON with fixed quotes
    try:
        fixed = value.replace("'", '"')
        return json.loads(fixed)
    except:
        pass
    
    return None


def safe_parse_list(value):
    """Safely parse list strings"""
    if pd.isna(value):
        return []
    
    if isinstance(value, list):
        return value
    
    if not isinstance(value, str):
        return []
    
    try:
        return ast.literal_eval(value)
    except:
        return []


def get_first_valid(*values):
    """Return the first non-null value from a list of values"""
    for val in values:
        if pd.notna(val) and val != '' and val != 'nan':
            return val
    return None


def extract_document_classification(row):
    """Extract document classification from multiple possible sources"""
    result = {}
    
    # Try JSON column first
    parsed = safe_parse_json(row.get('document_classification'))
    if parsed:
        result['document_type'] = parsed.get('document_type')
        result['primary_topic'] = parsed.get('primary_topic')
        result['secondary_topics'] = parsed.get('secondary_topics', [])
    
    # Fall back to individual columns
    if not result.get('document_type'):
        result['document_type'] = row.get('document_type')
    if not result.get('primary_topic'):
        result['primary_topic'] = row.get('primary_topic')
    if not result.get('secondary_topics'):
        result['secondary_topics'] = safe_parse_list(row.get('secondary_topics'))
    
    return result


def extract_extensive_margin(row):
    """Extract extensive margin from multiple possible sources"""
    result = {}
    
    # Try JSON column first
    parsed = safe_parse_json(row.get('extensive_margin'))
    if parsed:
        result['extensive_margin_impact'] = parsed.get('extensive_margin_impact')
        result['extensive_margin_direction'] = parsed.get('extensive_margin_direction')
        result['extensive_margin_explanation'] = parsed.get('extensive_margin_explanation')
    
    # Fall back to individual columns
    if not result.get('extensive_margin_impact'):
        result['extensive_margin_impact'] = row.get('extensive_margin_impact')
    if not result.get('extensive_margin_direction'):
        result['extensive_margin_direction'] = row.get('extensive_margin_direction')
    if not result.get('extensive_margin_explanation'):
        result['extensive_margin_explanation'] = row.get('extensive_margin_explanation')
    
    return result


def extract_intensive_margin(row):
    """Extract intensive margin from multiple possible sources"""
    result = {}
    
    # Try JSON column first
    parsed = safe_parse_json(row.get('intensive_margin'))
    if parsed:
        result['intensive_margin_impact'] = parsed.get('intensive_margin_impact')
        result['intensive_margin_direction'] = parsed.get('intensive_margin_direction')
        result['intensive_margin_explanation'] = parsed.get('intensive_margin_explanation')
    
    # Fall back to individual columns
    if not result.get('intensive_margin_impact'):
        result['intensive_margin_impact'] = row.get('intensive_margin_impact')
    if not result.get('intensive_margin_direction'):
        result['intensive_margin_direction'] = row.get('intensive_margin_direction')
    if not result.get('intensive_margin_explanation'):
        result['intensive_margin_explanation'] = row.get('intensive_margin_explanation')
    
    return result


def extract_ideology(row):
    """Extract ideology from multiple possible sources - handles hybrid field"""
    result = {}
    
    # Try the prosecutorial_ideology JSON column first
    parsed = safe_parse_json(row.get('prosecutorial_ideology'))
    if parsed:
        result['ideological_orientation'] = parsed.get('ideological_orientation')
        result['confidence_level'] = parsed.get('confidence_level')
        result['progressive_indicators'] = parsed.get('progressive_indicators', [])
        result['traditional_indicators'] = parsed.get('traditional_indicators', [])
        result['ideological_explanation'] = parsed.get('ideological_explanation')
    
    # Try the ideological_orientation field - could be JSON or simple string
    if not result.get('ideological_orientation'):
        ideo_val = row.get('ideological_orientation')
        parsed_ideo = safe_parse_json(ideo_val)
        
        if parsed_ideo:
            # It's JSON
            result['ideological_orientation'] = parsed_ideo.get('ideological_orientation')
            result['confidence_level'] = parsed_ideo.get('confidence_level')
            result['progressive_indicators'] = parsed_ideo.get('progressive_indicators', [])
            result['traditional_indicators'] = parsed_ideo.get('traditional_indicators', [])
            result['ideological_explanation'] = parsed_ideo.get('ideological_explanation')
        elif pd.notna(ideo_val) and isinstance(ideo_val, str):
            # It's a simple string
            result['ideological_orientation'] = ideo_val
    
    # Fall back to individual columns for other fields
    if not result.get('confidence_level'):
        result['confidence_level'] = row.get('confidence_level')
    if not result.get('progressive_indicators'):
        result['progressive_indicators'] = safe_parse_list(row.get('progressive_indicators'))
    if not result.get('traditional_indicators'):
        result['traditional_indicators'] = safe_parse_list(row.get('traditional_indicators'))
    if not result.get('ideological_explanation'):
        result['ideological_explanation'] = row.get('ideological_explanation')
    
    return result


def extract_policy_positions(row):
    """Extract specific policy positions from multiple possible sources"""
    result = {}
    
    # Try JSON column first
    parsed = safe_parse_json(row.get('specific_policy_positions'))
    if parsed:
        result['supports_diversion'] = parsed.get('supports_diversion')
        result['supports_alternatives_to_incarceration'] = parsed.get('supports_alternatives_to_incarceration')
        result['position_on_enhancements'] = parsed.get('position_on_enhancements')
        result['position_on_three_strikes'] = parsed.get('position_on_three_strikes')
        result['position_on_bail'] = parsed.get('position_on_bail')
        result['position_on_juvenile_transfer'] = parsed.get('position_on_juvenile_transfer')
        result['racial_justice_emphasis'] = parsed.get('racial_justice_emphasis')
    
    # Fall back to individual columns
    if not result.get('supports_diversion'):
        result['supports_diversion'] = row.get('supports_diversion')
    if not result.get('supports_alternatives_to_incarceration'):
        result['supports_alternatives_to_incarceration'] = row.get('supports_alternatives_to_incarceration')
    if not result.get('position_on_enhancements'):
        result['position_on_enhancements'] = row.get('position_on_enhancements')
    if not result.get('position_on_three_strikes'):
        result['position_on_three_strikes'] = row.get('position_on_three_strikes')
    if not result.get('position_on_bail'):
        result['position_on_bail'] = row.get('position_on_bail')
    if not result.get('position_on_juvenile_transfer'):
        result['position_on_juvenile_transfer'] = row.get('position_on_juvenile_transfer')
    if not result.get('racial_justice_emphasis'):
        result['racial_justice_emphasis'] = row.get('racial_justice_emphasis')
    
    return result


def extract_administrative_context(row):
    """Extract administrative context from multiple possible sources"""
    result = {}
    
    # Try JSON column first
    parsed = safe_parse_json(row.get('administrative_context'))
    if parsed:
        result['da_administration_mentioned'] = parsed.get('da_administration_mentioned')
        result['reflects_office_wide_policy'] = parsed.get('reflects_office_wide_policy')
        result['policy_change_indicator'] = parsed.get('policy_change_indicator')
        result['mandates_vs_guidance'] = parsed.get('mandates_vs_guidance')
    
    # Fall back to individual columns
    if not result.get('da_administration_mentioned'):
        result['da_administration_mentioned'] = row.get('da_administration_mentioned')
    if not result.get('reflects_office_wide_policy'):
        result['reflects_office_wide_policy'] = row.get('reflects_office_wide_policy')
    if not result.get('policy_change_indicator'):
        result['policy_change_indicator'] = row.get('policy_change_indicator')
    if not result.get('mandates_vs_guidance'):
        result['mandates_vs_guidance'] = row.get('mandates_vs_guidance')
    
    return result


def extract_all_fields(df):
    """Extract all fields from all possible sources for each row"""
    
    print("="*80)
    print("EXTRACTING DATA FROM ALL SOURCES")
    print("="*80)
    
    # Initialize new columns
    new_cols = {
        'document_type_clean': [],
        'primary_topic_clean': [],
        'secondary_topics_clean': [],
        'extensive_margin_impact_clean': [],
        'extensive_margin_direction_clean': [],
        'extensive_margin_explanation_clean': [],
        'intensive_margin_impact_clean': [],
        'intensive_margin_direction_clean': [],
        'intensive_margin_explanation_clean': [],
        'ideological_orientation_clean': [],
        'confidence_level_clean': [],
        'progressive_indicators_clean': [],
        'traditional_indicators_clean': [],
        'ideological_explanation_clean': [],
        'supports_diversion_clean': [],
        'supports_alternatives_clean': [],
        'position_on_enhancements_clean': [],
        'position_on_three_strikes_clean': [],
        'position_on_bail_clean': [],
        'position_on_juvenile_transfer_clean': [],
        'racial_justice_emphasis_clean': [],
        'da_administration_clean': [],
        'office_wide_policy_clean': [],
        'policy_change_clean': [],
        'mandates_vs_guidance_clean': []
    }
    
    print(f"\nProcessing {len(df)} documents...")
    
    for idx, row in df.iterrows():
        if idx % 100 == 0:
            print(f"  Processing row {idx}...")
        
        # Extract from all sources
        doc_class = extract_document_classification(row)
        ext_margin = extract_extensive_margin(row)
        int_margin = extract_intensive_margin(row)
        ideology = extract_ideology(row)
        policies = extract_policy_positions(row)
        admin = extract_administrative_context(row)
        
        # Append to new columns
        new_cols['document_type_clean'].append(doc_class.get('document_type'))
        new_cols['primary_topic_clean'].append(doc_class.get('primary_topic'))
        new_cols['secondary_topics_clean'].append(str(doc_class.get('secondary_topics', [])))
        
        new_cols['extensive_margin_impact_clean'].append(ext_margin.get('extensive_margin_impact'))
        new_cols['extensive_margin_direction_clean'].append(ext_margin.get('extensive_margin_direction'))
        new_cols['extensive_margin_explanation_clean'].append(ext_margin.get('extensive_margin_explanation'))
        
        new_cols['intensive_margin_impact_clean'].append(int_margin.get('intensive_margin_impact'))
        new_cols['intensive_margin_direction_clean'].append(int_margin.get('intensive_margin_direction'))
        new_cols['intensive_margin_explanation_clean'].append(int_margin.get('intensive_margin_explanation'))
        
        new_cols['ideological_orientation_clean'].append(ideology.get('ideological_orientation'))
        new_cols['confidence_level_clean'].append(ideology.get('confidence_level'))
        new_cols['progressive_indicators_clean'].append(str(ideology.get('progressive_indicators', [])))
        new_cols['traditional_indicators_clean'].append(str(ideology.get('traditional_indicators', [])))
        new_cols['ideological_explanation_clean'].append(ideology.get('ideological_explanation'))
        
        new_cols['supports_diversion_clean'].append(policies.get('supports_diversion'))
        new_cols['supports_alternatives_clean'].append(policies.get('supports_alternatives_to_incarceration'))
        new_cols['position_on_enhancements_clean'].append(policies.get('position_on_enhancements'))
        new_cols['position_on_three_strikes_clean'].append(policies.get('position_on_three_strikes'))
        new_cols['position_on_bail_clean'].append(policies.get('position_on_bail'))
        new_cols['position_on_juvenile_transfer_clean'].append(policies.get('position_on_juvenile_transfer'))
        new_cols['racial_justice_emphasis_clean'].append(policies.get('racial_justice_emphasis'))
        
        new_cols['da_administration_clean'].append(admin.get('da_administration_mentioned'))
        new_cols['office_wide_policy_clean'].append(admin.get('reflects_office_wide_policy'))
        new_cols['policy_change_clean'].append(admin.get('policy_change_indicator'))
        new_cols['mandates_vs_guidance_clean'].append(admin.get('mandates_vs_guidance'))
    
    # Add all new columns to dataframe
    for col_name, col_data in new_cols.items():
        df[col_name] = col_data
    
    print("\n✓ Extraction complete!")
    return df


def standardize_values(df):
    """Standardize and clean extracted values"""
    
    print("\n" + "="*80)
    print("STANDARDIZING VALUES")
    print("="*80)
    
    # Standardize ideology
    def clean_ideology(val):
        if pd.isna(val):
            return 'unclear'
        val_lower = str(val).lower().strip()
        if 'clearly_progressive' in val_lower or 'clearly progressive' in val_lower:
            return 'clearly_progressive'
        elif 'leans_progressive' in val_lower or 'leans progressive' in val_lower:
            return 'leans_progressive'
        elif 'progressive' in val_lower:
            return 'progressive'
        elif 'clearly_traditional' in val_lower or 'clearly traditional' in val_lower:
            return 'clearly_traditional'
        elif 'leans_traditional' in val_lower or 'leans traditional' in val_lower:
            return 'leans_traditional'
        elif 'traditional' in val_lower:
            return 'traditional'
        elif 'neutral' in val_lower:
            return 'neutral'
        elif 'mixed' in val_lower:
            return 'mixed'
        else:
            return 'unclear'
    
    df['ideology'] = df['ideological_orientation_clean'].apply(clean_ideology)
    
    # Create binary progressive
    df['is_progressive'] = df['ideology'].isin([
        'clearly_progressive', 'leans_progressive', 'progressive'
    ]).astype(int)
    
    # Create binary traditional
    df['is_traditional'] = df['ideology'].isin([
        'clearly_traditional', 'leans_traditional', 'traditional'
    ]).astype(int)
    
    # Standardize margin fields
    for margin in ['extensive', 'intensive']:
        impact_col = f'{margin}_margin_impact_clean'
        direction_col = f'{margin}_margin_direction_clean'
        
        if impact_col in df.columns:
            df[impact_col] = df[impact_col].fillna('not_applicable')
            df[impact_col] = df[impact_col].astype(str).str.lower().str.strip()
            df[impact_col] = df[impact_col].replace('nan', 'not_applicable')
        
        if direction_col in df.columns:
            df[direction_col] = df[direction_col].fillna('not_applicable')
            df[direction_col] = df[direction_col].astype(str).str.lower().str.strip()
            df[direction_col] = df[direction_col].replace('nan', 'not_applicable')
            
            # Create binary indicators
            df[f'{margin}_lenient'] = df[direction_col].str.contains(
                'lenient', case=False, na=False
            ).astype(int)
            
            df[f'{margin}_punitive'] = df[direction_col].str.contains(
                'punitive', case=False, na=False
            ).astype(int)
    
    # Parse dates
    df['date'] = pd.to_datetime(df['relevant_date'], errors='coerce')
    df['year'] = df['date'].dt.year
    
    # Create ideology score
    ideology_scores = {
        'clearly_progressive': 2,
        'leans_progressive': 1,
        'progressive': 1.5,
        'neutral': 0,
        'mixed': 0,
        'unclear': np.nan,
        'leans_traditional': -1,
        'traditional': -1.5,
        'clearly_traditional': -2
    }
    df['ideology_score'] = df['ideology'].map(ideology_scores)
    
    # Standardize yes/no fields
    yes_no_fields = [
        'supports_diversion_clean',
        'supports_alternatives_clean'
    ]
    
    for field in yes_no_fields:
        if field in df.columns:
            df[field] = df[field].astype(str).str.lower().str.strip()
            df[field] = df[field].replace({'nan': 'not_addressed', 'none': 'not_addressed'})
    
    print("\n✓ Standardization complete!")
    return df


def validate_extraction(df):
    """Validate the extraction with known examples"""
    
    print("\n" + "="*80)
    print("VALIDATION")
    print("="*80)
    
    # Test case 1: Defense Attorney Report (should have data from individual columns)
    test1 = df[df['filename'] == '2021_Calaveras County_Defense Attorney Report.pdf']
    if len(test1) > 0:
        row = test1.iloc[0]
        print("\n✓ Test 1: Defense Attorney Report (from individual columns)")
        print(f"  Document type: {row['document_type_clean']}")
        print(f"  Ideology: {row['ideology']}")
        print(f"  Has data: {pd.notna(row['document_type_clean'])}")
    
    # Test case 2: LA County Parole memo (should have data from JSON columns)
    test2 = df[df['filename'] == '2020.09.08_Los Angeles County_Parole Periods and Prison Closures (with CDCR Demographics Data).pdf']
    if len(test2) > 0:
        row = test2.iloc[0]
        print("\n✓ Test 2: LA County Parole Memo (from JSON columns)")
        print(f"  Document type: {row['document_type_clean']}")
        print(f"  Ideology: {row['ideology']}")
        print(f"  Extensive margin direction: {row['extensive_margin_direction_clean']}")
        print(f"  Intensive margin direction: {row['intensive_margin_direction_clean']}")
        print(f"  Has data: {pd.notna(row['document_type_clean'])}")
    
    # Overall coverage check
    print("\n" + "="*80)
    print("COVERAGE CHECK")
    print("="*80)
    
    print(f"\nTotal documents: {len(df)}")
    print(f"Documents with document type: {df['document_type_clean'].notna().sum()} ({df['document_type_clean'].notna().mean()*100:.1f}%)")
    print(f"Documents with ideology: {df['ideological_orientation_clean'].notna().sum()} ({df['ideological_orientation_clean'].notna().mean()*100:.1f}%)")
    print(f"Documents with extensive margin data: {df['extensive_margin_impact_clean'].notna().sum()} ({df['extensive_margin_impact_clean'].notna().mean()*100:.1f}%)")
    print(f"Documents with intensive margin data: {df['intensive_margin_impact_clean'].notna().sum()} ({df['intensive_margin_impact_clean'].notna().mean()*100:.1f}%)")


def main():
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  COMPREHENSIVE PROSECUTOR POLICY DATA CLEANING".center(78) + "║")
    print("║" + "  Intelligently Merging All Data Sources".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    print("\n")
    
    # Load data
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} documents with {len(df.columns)} columns")
    
    # Extract from all sources
    df = extract_all_fields(df)
    
    # Standardize
    df = standardize_values(df)
    
    # Validate
    validate_extraction(df)
    
    # Summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    
    print(f"\nIdeology distribution:")
    print(df['ideology'].value_counts().sort_index())
    
    print(f"\nProgressive: {df['is_progressive'].sum()} ({df['is_progressive'].mean()*100:.1f}%)")
    print(f"Traditional: {df['is_traditional'].sum()} ({df['is_traditional'].mean()*100:.1f}%)")
    
    print(f"\nExtensive Margin Impact:")
    ext_impact = df['extensive_margin_impact_clean'].value_counts()
    for val, count in ext_impact.head(10).items():
        print(f"  {val}: {count} ({count/len(df)*100:.1f}%)")
    
    print(f"\nIntensive Margin Impact:")
    int_impact = df['intensive_margin_impact_clean'].value_counts()
    for val, count in int_impact.head(10).items():
        print(f"  {val}: {count} ({count/len(df)*100:.1f}%)")
    
    # Save cleaned data
    output_file = OUTPUT_FILE
    
    # Select the most important columns for the output
    output_cols = [
        'filename', 'county', 'relevant_date', 'date', 'year',
        'document_type_clean', 'primary_topic_clean', 'secondary_topics_clean',
        'ideology', 'is_progressive', 'is_traditional', 'ideology_score',
        'ideological_orientation_clean', 'confidence_level_clean',
        'progressive_indicators_clean', 'traditional_indicators_clean',
        'extensive_margin_impact_clean', 'extensive_margin_direction_clean',
        'extensive_lenient', 'extensive_punitive',
        'intensive_margin_impact_clean', 'intensive_margin_direction_clean',
        'intensive_lenient', 'intensive_punitive',
        'supports_diversion_clean', 'supports_alternatives_clean',
        'position_on_enhancements_clean', 'position_on_three_strikes_clean',
        'position_on_bail_clean', 'position_on_juvenile_transfer_clean',
        'racial_justice_emphasis_clean',
        'da_administration_clean', 'office_wide_policy_clean',
        'policy_change_clean', 'mandates_vs_guidance_clean',
        'summary', 'key_quotes'
    ]
    
    # Only include columns that exist
    output_cols = [col for col in output_cols if col in df.columns]
    
    df[output_cols].to_csv(output_file, index=False)
    print(f"\n\n✓ Saved cleaned dataset to: {output_file}")
    print(f"  Output contains {len(output_cols)} columns")
    
    return df


if __name__ == "__main__":
    df = main()
