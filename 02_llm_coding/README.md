# Prosecutor Policy Document Coding System

A comprehensive LLM-based pipeline for systematically coding prosecutor office policy documents to analyze ideological orientation across time and place.

**Author:** Dvir Yogev, CLJC, UC Berkeley School of Law  
**Institution:** Criminal Law & Justice Center, UC Berkeley Law

## Overview

This system uses Claude (Anthropic) to automatically code 2,665+ prosecutor policy documents from California DA offices on two key dimensions:

1. **Extensive vs Intensive Margin**: Whether policies affect who enters the system (extensive) vs how harshly people are treated once in the system (intensive)
2. **Progressive vs Traditional Ideology**: Whether policies reflect reform-oriented or traditional prosecutorial approaches

## Key Concepts

### Extensive Margin
Decisions about **WHO** enters the criminal justice system:
- Charging decisions
- Declination policies
- Diversion programs
- Pre-trial detention/release
- Case screening standards

### Intensive Margin
Decisions about **HOW SEVERELY** people in the system are treated:
- Sentencing recommendations
- Plea offers
- Enhancement charging
- Three strikes applications
- Parole opposition

### Progressive vs Traditional Orientation

**Progressive indicators:**
- Diversion emphasis
- Declination policies
- Racial justice focus
- Reduced enhancements
- Bail reform
- Alternatives to incarceration
- Restorative justice
- Implicit bias training

**Traditional indicators:**
- Strict charging
- Enhancement maximization
- Three strikes advocacy
- High bail
- Tough-on-crime rhetoric
- Victim-centered only focus

## System Components

### 1. Document Processing (`prosecutor_policy_coder.py`)
Main pipeline that:
- Extracts text from PDFs, DOCX, and DOC files
- Sends documents to Claude API for structured coding
- Handles batching, rate limiting, and checkpointing
- Outputs coded data to CSV

### 2. Validation (`validate_coding.py`)
Quality control that:
- Checks completeness and consistency
- Analyzes distributions of coded variables
- Identifies potential coding errors
- Generates validation reports

### 3. Analysis (`analyze_policies.py`)
Research analysis that:
- Examines temporal trends in ideology
- Compares counties
- Analyzes policy domains
- Creates visualizations
- Exports results for papers

## Installation

### Prerequisites
```bash
# Python 3.9+
python --version

# For legacy .doc files (optional)
sudo apt-get install antiword catdoc

# Anthropic API key
export ANTHROPIC_API_KEY="your-key-here"
```

### Python Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Step 1: Prepare Your Data

Organize files:
```
/path/to/your/data/
├── prosecutor_policies/           # Folder with all PDFs and DOCs
│   ├── 2021_Alameda County_....pdf
│   ├── 2020_Los Angeles_....pdf
│   └── ...
└── prosecutor_policies_metadata.csv  # Metadata file with columns:
                                       # filename, county, relevant_date
```

### Step 2: Configure the Pipeline

Edit `prosecutor_policy_coder.py`:

```python
# Update these paths at the bottom of the file
DOCUMENTS_DIR = "/path/to/your/prosecutor_policies"
METADATA_FILE = "/path/to/your/prosecutor_policies_metadata.csv"
OUTPUT_FILE = "/mnt/user-data/outputs/coded_prosecutor_policies.csv"
```

### Step 3: Test Run (Small Batch)

Start with 10 documents to test:

```bash
python prosecutor_policy_coder.py
```

The pipeline is configured by default to process only 10 documents. Check the output and logs.

### Step 4: Full Run

Once satisfied with test run, edit the main() function:

```python
pipeline.run_pipeline(
    batch_size=50,      # Save every 50 documents
    start_idx=0,        # Start from beginning
    max_docs=None       # Process all (change from 10)
)
```

Then run:
```bash
nohup python prosecutor_policy_coder.py > run.log 2>&1 &
```

This runs in the background. Monitor progress:
```bash
tail -f run.log
tail -f coding_pipeline.log
```

### Step 5: Validate Results

Check coding quality:

```bash
python validate_coding.py
```

This generates:
- Console output with completeness checks
- `coding_validation_summary.csv` with key statistics

Review flagged documents and re-code if necessary.

### Step 6: Analyze Results

Run full analysis:

```bash
python analyze_policies.py
```

This generates:
- Console output with statistical analyses
- `temporal_trends.csv` - ideology over time
- `county_comparisons.csv` - cross-sectional comparisons
- `progressive_trend.png` - time series visualization
- `county_comparison.png` - county rankings
- `margin_comparison.png` - extensive vs intensive trends

## Coding Schema

The LLM codes each document on the following dimensions:

### Document Classification
- `document_type`: policy_memo, training_material, etc.
- `primary_topic`: charging_decisions, sentencing, bail, diversion, etc.
- `secondary_topics`: Additional topics covered

### Margin Analysis
- `extensive_margin_impact`: high_impact, moderate_impact, low_impact, not_applicable
- `extensive_margin_direction`: more_lenient, more_punitive, neutral, mixed, not_applicable
- `extensive_margin_explanation`: Text explanation

- `intensive_margin_impact`: [same options]
- `intensive_margin_direction`: [same options]
- `intensive_margin_explanation`: Text explanation

### Ideology
- `ideological_orientation`: clearly_progressive, leans_progressive, neutral, leans_traditional, clearly_traditional, mixed, unclear
- `confidence_level`: high, medium, low
- `progressive_indicators`: List of progressive elements
- `traditional_indicators`: List of traditional elements
- `ideological_explanation`: Detailed explanation

### Specific Policies
- `supports_diversion`: yes, no, unclear, not_addressed
- `supports_alternatives_to_incarceration`: yes, no, unclear, not_addressed
- `position_on_enhancements`: maximize, selective, minimize, not_addressed
- `position_on_three_strikes`: strict_enforcement, flexible, reform_oriented, not_addressed
- `position_on_bail`: high_bail, moderate, reform_oriented, not_addressed
- `position_on_juvenile_transfer`: supports_transfer, case_by_case, opposes_transfer, not_addressed
- `racial_justice_emphasis`: high, moderate, low, not_addressed

### Administrative Context
- `da_administration_mentioned`: DA name if mentioned
- `reflects_office_wide_policy`: yes, no, unclear
- `policy_change_indicator`: clearly_new_policy, modification, continuation, unclear
- `mandates_vs_guidance`: mandatory, strong_guidance, suggestion, informational

## Cost Estimates

### Claude API Costs (approximate)
- **Input**: $3 per million tokens
- **Output**: $15 per million tokens

Average document: ~5,000 tokens input, ~1,000 tokens output
- Cost per document: ~$0.03
- **Total for 2,665 documents: ~$80**

Processing time: ~2 hours for full dataset (with rate limiting)

## Best Practices

### 1. Batch Processing
- Save results every 50 documents (built-in)
- Pipeline automatically skips already-coded documents
- Can restart from any point without losing progress

### 2. Rate Limiting
- Built-in 2-second delay between requests
- Handles rate limit errors with exponential backoff
- Respects Anthropic API limits

### 3. Quality Control
- Start with 10-20 documents to validate coding
- Manually review a random sample
- Check validation reports for inconsistencies
- Consider double-coding a subsample

### 4. Handling Errors
- Check `coding_pipeline.log` for extraction errors
- Some documents may fail (scanned PDFs, corrupted files)
- Re-run specific documents if needed

## Research Applications

### Time Series Analysis
Track how DA office policies evolved:
- Before/after DA elections
- Response to state reforms (Prop 47, 57)
- Progressive prosecutor wave (2018-2020)

### Cross-Sectional Comparison
Compare ideological orientation across:
- Progressive vs traditional counties
- Large vs small offices
- Bay Area vs Southern California
- Urban vs rural counties

### Policy Domain Analysis
Examine variation within offices:
- Which domains get progressive treatment?
- Where do progressive DAs maintain traditional approaches?
- Extensive vs intensive margin emphasis

### Regression Analysis
Model predictors of progressive orientation:
- Time trends
- County characteristics
- DA administration
- State-level reforms

## Troubleshooting

### Common Issues

**Error: "ANTHROPIC_API_KEY must be set"**
```bash
export ANTHROPIC_API_KEY="your-key-here"
# Or add to your .bashrc or .zshrc
```

**Error extracting .doc files**
```bash
# Install conversion tools
sudo apt-get install antiword catdoc
```

**Rate limit errors**
- Pipeline handles automatically with backoff
- If persistent, increase delay in code: `time.sleep(5)`

**Memory errors with large PDFs**
- System handles truncation automatically
- Very large documents use first 50,000 tokens

**Inconsistent coding**
- Lower temperature (currently 0.1) for more consistency
- Re-run validation script
- Consider manual review of unclear cases

## Validation Strategies

### 1. Face Validity
- Manually review 20-30 random documents
- Check if coding matches your understanding
- Look for obvious errors

### 2. Known Cases
- Code documents from known progressive DAs (e.g., SF, LA under Gascon)
- Code documents from known traditional DAs
- Verify expected patterns

### 3. Inter-rater Reliability
- Have humans code ~50 documents
- Compare with LLM coding
- Calculate agreement metrics (kappa, correlation)

### 4. Consistency Checks
- Run validation script
- Review flagged inconsistencies
- Check temporal continuity within offices

## Citation

If you use this system in your research, please cite:

```bibtex
@software{karp2025prosecutor,
  author = {Karp, Dvir},
  title = {Prosecutor Policy Document Coding System},
  year = {2025},
  publisher = {Berkeley Empirical Research in Quantitative Justice},
  institution = {UC Berkeley School of Law}
}
```

## Contact

Questions or issues:
- GitHub: [Your repository]
- Email: dyo@berkeley.edu
- CLJC: https://www.law.berkeley.edu/research/criminal-law-justice-center/

## License

[Your chosen license - e.g., MIT, GPL-3.0]

## Acknowledgments

- ACLU of Northern California (document collection)
- Criminal Law & Justice Center, UC Berkeley Law
- Anthropic Claude API
- Arnold Ventures (potential funding)

---

**Version:** 1.0  
**Last Updated:** October 2025
