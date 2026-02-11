# ACLU Prosecutor Policies Analysis

A comprehensive analysis pipeline for California District Attorney policy documents, from scraping to policy disruption detection.

## Pipeline Overview

```
01_raw_data/        → Source data (elections, metadata)
02_llm_coding/      → LLM-based policy coding with Claude API
03_data_cleaning/   → Data cleaning and validation
04_analysis/        → Statistical analysis and disruption detection
05_data/            → All datasets (intermediate, clean, results)
06_figures/         → Publication-ready visualizations
07_documentation/   → Research findings and summaries
```

## Data Sources

- **2,665 PDF documents** from ACLU NorCal's Racial Justice Act database
- **41 California counties** represented
- **Years 2015-2024** coverage
- **CA election data** for DA races

## Key Outputs

| File | Location | Description |
|------|----------|-------------|
| `prosecutor_policies_CLEANED.csv` | `05_data/clean/` | 1,865 coded policy documents |
| `policy_disruptions.csv` | `05_data/results/` | Policy disruption scores by county-year |
| `novel_reforms.csv` | `05_data/results/` | First-time policy adoptions |
| `final_post_election_analysis.csv` | `05_data/results/` | Election-linked policy data |

## Quick Start

### 1. LLM Policy Coding
```bash
cd 02_llm_coding
python prosecutor_policy_coder.py
```

### 2. Data Cleaning
```bash
cd 03_data_cleaning
python clean_prosecutor_policies_v2.py
```

### 3. Analysis
```bash
cd 04_analysis
python detect_disruptions.py        # Policy disruption detection
python comprehensive_analysis.py    # Full statistical analysis
```

## Policy Disruption Detection

The disruption detection system identifies when DA offices adopted new directions:

| Signal | Weight | Description |
|--------|--------|-------------|
| Ideology Velocity | 30% | Rate of ideology score change |
| Novelty Index | 25% | Proportion of new policy adoptions |
| Topic Shift | 20% | Jensen-Shannon divergence of topics |
| Margin Reversal | 15% | Extensive/intensive margin changes |
| DA Transition | 10% | New administration indicator |

**Classification thresholds:**
- Major disruption: ≥0.75
- Significant: 0.50-0.74
- Moderate: 0.25-0.49
- Minor: 0.10-0.24
- Stable: <0.10

## Key Findings

- **9 significant disruptions** detected (2020-2023)
- **San Francisco 2020** (Boudin): Highest disruption score (0.572)
- **347 novel reforms** tracked across counties
- Progressive policy surge 2020-2021 followed by stabilization

## Folder Structure

```
aclu_policies/
├── README.md
├── aclu_prosecutor_policies/
│   └── documents/              # 2,665 PDFs (6.1 GB)
├── 01_raw_data/
│   ├── ca_elections.xlsx
│   └── prosecutor_policies_metadata.csv
├── 02_llm_coding/
│   ├── prosecutor_policy_coder.py
│   ├── validate_coding.py
│   └── METHODOLOGY_GUIDE.md
├── 03_data_cleaning/
│   ├── clean_prosecutor_policies_v2.py
│   └── README.md
├── 04_analysis/
│   ├── comprehensive_analysis.py
│   ├── disruption_detector.py
│   ├── detect_disruptions.py
│   └── prosecutor_analysis_final.py
├── 05_data/
│   ├── intermediate/           # LLM-coded output
│   ├── clean/                  # Cleaned datasets
│   └── results/                # Analysis outputs
├── 06_figures/
│   ├── fig1_temporal_evolution.png
│   ├── fig2_geographic_patterns.png
│   └── ...
├── 07_documentation/
│   ├── COMPREHENSIVE_FINDINGS.md
│   └── FINAL_ANALYSIS_SUMMARY.md
└── archive/                    # Old/duplicate files
```

## Original Data Collection

Documents were scraped from ACLU NorCal's Racial Justice Act Public Records Database.

```bash
# To re-scrape (if needed):
python aclu_scraper_ultimate.py
```

## Citation

If you use this data in research:

```
ACLU of Northern California. (2020-2025). Racial Justice Act Public Records Database.
Retrieved from https://www.aclunc.org/racial-justice-act
```

## Requirements

- Python 3.8+
- Anthropic API key (for LLM coding)
- See `02_llm_coding/requirements.txt` for full dependencies
