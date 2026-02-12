# Quick Start Guide: Prosecutor Policy Coding System

**For: Dvir Yogev, CLJC, UC Berkeley School of Law**  
**Project: Analyzing Prosecutorial Ideology Across Time and Place**

## What You Have

A complete LLM-based system to code 2,665 prosecutor policy documents on:
1. **Extensive vs Intensive Margins** - who enters system vs how severely treated
2. **Progressive vs Traditional Ideology** - reform-oriented vs traditional approaches

## Files Created

### Core Pipeline
1. **`prosecutor_policy_coder.py`** - Main coding pipeline using Claude API
2. **`validate_coding.py`** - Quality control and validation
3. **`analyze_policies.py`** - Statistical analysis and visualization
4. **`requirements.txt`** - Python dependencies

### Documentation
5. **`README.md`** - Complete system documentation
6. **`METHODOLOGY_GUIDE.md`** - Research design guidance
7. **`EXAMPLE_OUTPUT.py`** - What the coded data looks like
8. **`quickstart.py`** - Interactive setup script

## Getting Started in 5 Steps

### Step 1: Install Dependencies (5 minutes)
```bash
pip install -r requirements.txt
```

For legacy .doc files (optional):
```bash
sudo apt-get install antiword catdoc
```

### Step 2: Set API Key (1 minute)
```bash
export ANTHROPIC_API_KEY="your-api-key-here"

# Or add to ~/.bashrc or ~/.zshrc for persistence
echo 'export ANTHROPIC_API_KEY="your-key"' >> ~/.bashrc
```

Get API key from: https://console.anthropic.com/

### Step 3: Run Interactive Setup (5 minutes)
```bash
python quickstart.py
```

This will:
- Check your environment
- Ask for file paths
- Run a 10-document test batch
- Cost: ~$0.30

### Step 4: Review Test Results (10 minutes)
```python
import pandas as pd
df = pd.read_csv('coded_prosecutor_policies.csv')

# Look at the data
print(df.head())
print(df['ideological_orientation'].value_counts())

# Check a few examples
for i in range(3):
    print(f"\n{df.iloc[i]['filename']}:")
    print(f"  Ideology: {df.iloc[i]['ideological_orientation']}")
    print(f"  Summary: {df.iloc[i]['summary'][:200]}...")
```

### Step 5: Run Full Pipeline (2-3 hours)

If test results look good:

1. Edit `prosecutor_policy_coder.py` (line ~280):
```python
pipeline.run_pipeline(
    batch_size=50,
    max_docs=None  # Change from 10 to None
)
```

2. Run in background:
```bash
nohup python prosecutor_policy_coder.py > coding.log 2>&1 &
```

3. Monitor progress:
```bash
tail -f coding.log
# Or check the output file periodically
```

**Expected time:** ~2-3 hours for 2,665 documents  
**Expected cost:** ~$80 in Claude API credits

## After Coding is Complete

### Validate Results
```bash
python validate_coding.py
```

This generates:
- Completeness checks
- Distribution analysis  
- Consistency checks
- `coding_validation_summary.csv`

### Analyze Results
```bash
python analyze_policies.py
```

This generates:
- Temporal trend analysis
- County comparisons
- Margin analysis (extensive vs intensive)
- Visualizations (PNG files)
- CSV files with aggregated results

### Use in Your Research

The coded data is now ready for:
- Cross-sectional comparisons of DA offices
- Time series analysis (2015-2021)
- Event studies (DA transitions)
- Regression discontinuity designs (if you have election data)
- Topic modeling and text analysis

See `METHODOLOGY_GUIDE.md` for detailed research designs.

## Key Features

### Automatic Checkpointing
- Pipeline saves every 50 documents
- Can restart from any point
- Already-coded documents are skipped

### Rate Limiting
- Built-in delays between API calls
- Exponential backoff for rate limits
- Respects Anthropic API limits

### Error Handling
- Logs all errors
- Continues processing if one document fails
- Can re-run failed documents later

### Multiple Output Formats
- Main CSV with all coded variables
- Aggregated county-year data
- Temporal trends
- Visualizations

## Expected Results

Based on the metadata analysis:

### Cross-Sectional Patterns
- **Progressive counties** (SF, Alameda, Contra Costa): 60-80% progressive documents
- **Traditional counties** (Orange, Fresno, Kern): 20-40% progressive documents
- **Mixed counties**: 40-60% progressive documents

### Temporal Trends (2015-2021)
- Increasing progressive orientation over time
- Spike in 2018-2020 (progressive DA wave)
- More emphasis on extensive margin (who gets charged)
- Racial justice emphasis increases

### Policy Domains
- Diversion/alternatives most progressive
- Sentencing more mixed
- Training materials mostly neutral

## Cost Breakdown

### One-Time Costs
- **Testing (10 docs):** $0.30
- **Full pipeline (2,665 docs):** ~$80
- **Re-coding subsample:** $3-8 (for 100-200 docs)

**Total estimated cost:** $80-90

### Time Investment
- **Setup:** 30 minutes
- **Testing:** 15 minutes  
- **Full run:** 2-3 hours (automated)
- **Validation:** 30 minutes
- **Analysis:** 1-2 hours

**Total active time:** ~3-4 hours  
**Total elapsed time:** 1 day (with overnight run)

## Troubleshooting

### "API key not set"
```bash
export ANTHROPIC_API_KEY="your-key"
```

### "File not found"
- Check file paths in configuration
- Make sure documents folder exists
- Verify metadata CSV path

### "No text extracted"
- Some PDFs may be scanned (images only)
- Try OCR if needed (pytesseract)
- Check if file is corrupted

### "Rate limit errors"
- Pipeline handles automatically
- If persistent, increase delay: `time.sleep(5)`

### "Inconsistent coding"
- Run validation script
- Check logs for specific documents
- Consider manual review of unclear cases

## Next Steps

1. **After initial coding:**
   - Run validation
   - Review sample of coded documents
   - Check face validity (SF progressive? Orange traditional?)

2. **For research:**
   - Merge with other data sources
   - Design specific analyses (see METHODOLOGY_GUIDE.md)
   - Consider manual coding subsample for reliability check

3. **For publication:**
   - Report intercoder reliability
   - Provide sample documents and coding
   - Make code and (redacted) data available
   - Address limitations transparently

## Support

Questions? Check:
1. `README.md` - Full documentation
2. `METHODOLOGY_GUIDE.md` - Research design
3. `EXAMPLE_OUTPUT.py` - Data structure
4. Logs: `coding_pipeline.log`

Contact: dyo@berkeley.edu

## Citation

```bibtex
@software{karp2025prosecutor,
  author = {Karp, Dvir},
  title = {Prosecutor Policy Document Coding System},
  year = {2025},
  publisher = {Berkeley Empirical Research in Quantitative Justice},
  institution = {UC Berkeley School of Law}
}
```

---

**You're all set!** Run `python quickstart.py` to begin.

Good luck with your research! 🚀
