# QUICK START GUIDE

## Setup (First Time Only)

### Mac/Linux:
```bash
# Install dependencies
pip install -r requirements.txt
```

### Windows:
```cmd
# Install dependencies
pip install -r requirements.txt
```

## Running the Scripts

### 1. Test First (Recommended)
Check if the scraper works:
```bash
python test_aclu_scraper.py
```
This creates `page_source.html` - check it to see what data is available.

### 2. Get Metadata Only (Fast - ~1 minute)
Download just the list of documents without the files:
```bash
python aclu_prosecutor_policies_scraper.py --no-download
```
Creates: `aclu_prosecutor_policies/prosecutor_policies_metadata.csv`

### 3. Analyze What's Available
See what counties and time periods are covered:
```bash
python analyze_metadata.py
```
This shows statistics and creates visualizations.

### 4. Download Specific Documents
Interactive mode (recommended):
```bash
python selective_download.py --interactive
```

Or specify filters directly:
```bash
# Just LA County
python selective_download.py --counties "Los Angeles"

# Multiple counties
python selective_download.py --counties "Los Angeles,San Francisco,Alameda"

# Date range
python selective_download.py --start-date 2020-01-01 --end-date 2023-12-31

# Keywords
python selective_download.py --keywords "charging,sentencing"
```

### 5. Download Everything (Slow - hours)
Download all 2,666+ documents:
```bash
python aclu_prosecutor_policies_scraper.py
```
⚠️ This will take several hours and use several GB of disk space!

## Troubleshooting

**"ModuleNotFoundError"**: Run `pip install -r requirements.txt`

**"File not found"**: Make sure you're in the directory with the scripts

**Scraper not working**: The ACLU website may have changed structure. Run `test_aclu_scraper.py` and check `page_source.html` to see the current HTML structure.

**Connection errors**: Check your internet connection and try again. The script has rate limiting built in.

## Output Files

- `aclu_prosecutor_policies/prosecutor_policies_metadata.csv` - All metadata
- `aclu_prosecutor_policies/documents/` - Downloaded PDF/Excel files
- `counties_barchart.png` - Visualization of county coverage
- `timeline.png` - Timeline of documents by date
- `county_year_heatmap.png` - Heatmap of counties over time

## For Your Research

1. Start with metadata only
2. Analyze coverage
3. Download relevant subset
4. Use NLP to extract policy features
5. Create coded variables for quantitative analysis

## Need Help?

See the full README.md for detailed documentation.
