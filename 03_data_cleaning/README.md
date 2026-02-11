# Prosecutor Policy Database - Comprehensive Data Cleaning

## Overview

This document explains the data cleaning process for the prosecutor policy database, which contained coded documents stored in multiple different column formats.

## The Problem

The original dataset had **two different coding schemas** that were used for different documents:

1. **Individual columns** (used for ~106 documents):
   - `document_type`, `primary_topic`, `extensive_margin_impact`, etc.
   - Each field stored as a separate column

2. **JSON/aggregate columns** (used for ~1,759 documents):
   - `document_classification`, `extensive_margin`, `intensive_margin`, etc.
   - Multiple fields stored as JSON strings within single columns

3. **Hybrid column** (`ideological_orientation`):
   - Sometimes contained simple strings like "unclear" or "neutral"
   - Sometimes contained full JSON with detailed ideology coding

## The Solution

The cleaning script (`clean_prosecutor_policies_v2.py`) intelligently merges data from all sources:

### Extraction Strategy

For each document, the script:
1. **Tries JSON columns first** (since they contain the most data)
2. **Falls back to individual columns** if JSON is empty
3. **Handles hybrid fields** that can be either JSON or simple strings
4. **Merges all sources** into clean, standardized columns

### Key Functions

- `extract_document_classification()`: Extracts document type, topic, secondary topics
- `extract_extensive_margin()`: Extracts extensive margin coding (who enters the system)
- `extract_intensive_margin()`: Extracts intensive margin coding (severity of treatment)
- `extract_ideology()`: Handles hybrid ideological orientation field
- `extract_policy_positions()`: Extracts specific policy stances
- `extract_administrative_context()`: Extracts DA administration and policy context

## Results

### Coverage
- **100% coverage** achieved for all key fields
- All 1,865 documents successfully processed
- No data loss from the multiple encoding schemas

### Ideology Distribution
- **Clearly Progressive**: 232 documents (12.4%)
- **Leans Progressive**: 341 documents (18.3%)
- **Clearly Traditional**: 122 documents (6.5%)
- **Leans Traditional**: 196 documents (10.5%)
- **Neutral**: 441 documents (23.6%)
- **Mixed**: 62 documents (3.3%)
- **Unclear**: 471 documents (25.3%)

### Progressive vs Traditional
- **Progressive Total**: 573 documents (30.7%)
- **Traditional Total**: 318 documents (17.1%)

### Margin Impacts

**Extensive Margin** (who enters the system):
- High Impact: 397 docs (21.3%)
- Moderate Impact: 426 docs (22.8%)
- Low Impact: 395 docs (21.2%)
- Not Applicable: 647 docs (34.7%)

**Intensive Margin** (severity of treatment):
- High Impact: 385 docs (20.6%)
- Moderate Impact: 576 docs (30.9%)
- Low Impact: 417 docs (22.4%)
- Not Applicable: 487 docs (26.1%)

## Output Files

### Main Output: `prosecutor_policies_CLEANED.csv`

Contains 37 clean columns organized into categories:

#### Identification
- `filename`, `county`, `relevant_date`, `date`, `year`

#### Document Classification
- `document_type_clean`: Type of document (policy_memo, training_material, etc.)
- `primary_topic_clean`: Main topic (sentencing, enhancements, bail, etc.)
- `secondary_topics_clean`: Additional topics covered

#### Ideological Orientation
- `ideology`: Standardized ideology (clearly_progressive, leans_traditional, etc.)
- `is_progressive`: Binary indicator (1/0)
- `is_traditional`: Binary indicator (1/0)
- `ideology_score`: Numeric score from -2 (clearly_traditional) to +2 (clearly_progressive)
- `ideological_orientation_clean`: Raw ideological orientation
- `confidence_level_clean`: Coding confidence
- `progressive_indicators_clean`: List of progressive indicators
- `traditional_indicators_clean`: List of traditional indicators

#### Extensive Margin (Who Enters the System)
- `extensive_margin_impact_clean`: Impact level (high/moderate/low/not_applicable)
- `extensive_margin_direction_clean`: Direction (more_lenient/more_punitive/neutral)
- `extensive_lenient`: Binary indicator for lenient direction
- `extensive_punitive`: Binary indicator for punitive direction

#### Intensive Margin (Severity of Treatment)
- `intensive_margin_impact_clean`: Impact level
- `intensive_margin_direction_clean`: Direction
- `intensive_lenient`: Binary indicator
- `intensive_punitive`: Binary indicator

#### Specific Policy Positions
- `supports_diversion_clean`: Position on diversion programs
- `supports_alternatives_clean`: Support for alternatives to incarceration
- `position_on_enhancements_clean`: Stance on sentencing enhancements
- `position_on_three_strikes_clean`: Three strikes law position
- `position_on_bail_clean`: Bail reform position
- `position_on_juvenile_transfer_clean`: Juvenile transfer to adult court
- `racial_justice_emphasis_clean`: Emphasis on racial justice

#### Administrative Context
- `da_administration_clean`: DA administration mentioned
- `office_wide_policy_clean`: Whether reflects office-wide policy
- `policy_change_clean`: Policy change indicator
- `mandates_vs_guidance_clean`: Whether mandatory or guidance

#### Text Content
- `summary`: Document summary
- `key_quotes`: Important quotes from document

## County-Level Highlights

### Most Documents
1. Los Angeles County: 373 docs
2. Ventura County: 347 docs
3. San Luis Obispo County: 232 docs

### Most Progressive (by %)
Counties with highest percentage of progressive documents (min 25 docs):
- San Francisco County
- Los Angeles County
- San Diego County

### Most Traditional (by %)
Counties with highest percentage of traditional documents (min 25 docs):
- Stanislaus County: 47.4%
- Placer County: 41.4%
- Monterey County: 30.8%

## Usage Notes

### For Analysis

The cleaned dataset is ready for:
- Time series analysis of prosecutorial ideology
- County-level comparisons
- Policy impact assessment
- Progressive prosecutor research
- Media bias detection studies

### Key Variables for Analysis

**Dependent Variables:**
- `ideology_score`: Continuous measure of ideology
- `is_progressive`: Binary progressive indicator
- `extensive_margin_direction_clean`: Charging leniency
- `intensive_margin_direction_clean`: Sentencing leniency

**Independent Variables:**
- `county`: Geographic variation
- `year`: Temporal trends
- `da_administration_clean`: By administration

**Control Variables:**
- `document_type_clean`: Document type
- `primary_topic_clean`: Policy area
- `confidence_level_clean`: Coding confidence

## Validation

The script includes validation checks using known documents:
- ✓ Calaveras County Defense Attorney Report (individual columns)
- ✓ LA County Parole Memo (JSON columns)
- ✓ Random sample verification

All test cases passed with 100% data extraction.

## Script Files

- `clean_prosecutor_policies_v2.py`: Comprehensive cleaning script
- `clean_data_correctly.py`: Original script (for reference)

## Contact

For questions about the data cleaning process or the BERQ-J prosecutor database project:
- Criminal Law & Justice Center, UC Berkeley School of Law
- Berkeley Empirical Research in Quantitative Justice (BERQ-J)
