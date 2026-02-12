# Methodological Guide: Research with Coded Prosecutor Policy Data

**Center for Law and Justice (CLJC), UC Berkeley School of Law**  
**Author: Dvir Yogev**

## Overview

This document provides methodological guidance for using LLM-coded prosecutor policy documents in empirical research. It covers research designs, measurement considerations, threats to validity, and best practices.

## 1. Measurement & Construct Validity

### 1.1 What We're Actually Measuring

The coded data captures **revealed policy preferences** through official documents. This is distinct from:
- **Actual prosecutorial behavior** (outcomes in cases)
- **DA rhetoric** (campaign promises, public statements)
- **Office culture** (informal norms, prosecutorial discretion in practice)

**Strengths:**
- Official documents represent intended policy direction
- More concrete than rhetoric alone
- Captures institutional priorities

**Limitations:**
- Policy documents ≠ implementation
- May miss informal practices
- Selective document retention/production

### 1.2 Key Constructs

#### Progressive Prosecutorial Ideology
**Definition:** Orientation toward reducing criminal justice system involvement, addressing racial disparities, and emphasizing alternatives to incarceration.

**Measurement Approach:**
- Primary: `ideological_orientation` (5-point scale)
- Alternative: Binary `is_progressive` derived variable
- Validation: Count of `progressive_indicators`

**Conceptual Issues:**
- Progressive ≠ universally lenient (may be tough on certain crimes)
- Context-dependent (what's progressive in Orange County vs SF?)
- Time-varying standards (2015 progressive policy may be mainstream by 2021)

#### Extensive vs Intensive Margins
**Definitions:**
- Extensive: WHO enters the system (charging, diversion, declination)
- Intensive: HOW HARSHLY people are treated once in (sentencing, enhancements)

**Measurement:**
- Impact level: high/moderate/low
- Direction: more_lenient/more_punitive/neutral

**Conceptual Issues:**
- Not mutually exclusive (one policy can affect both)
- Intensive margin changes may indirectly affect extensive margin
- Measurement of "impact" is subjective

### 1.3 Reliability & Validity Assessment

#### Inter-rater Reliability
**Recommended approach:**
1. Manually code 50-100 documents
2. Compare with LLM coding
3. Calculate:
   - Percent agreement (simple)
   - Cohen's kappa (chance-adjusted)
   - Correlation on ordinal scales

**Expected benchmarks:**
- Ideology (5-point): κ > 0.60 acceptable, > 0.75 good
- Binary progressive: κ > 0.70 acceptable, > 0.80 good
- Margin direction: κ > 0.65 acceptable, > 0.75 good

#### Convergent Validity
**Cross-validate with:**
1. **Electoral outcomes** - Progressive DAs should have progressive documents
2. **Media coding** - Newspaper characterizations of DA ideology
3. **Advocacy group ratings** - ACLU, reform organizations
4. **Case outcomes** - Actual charging/sentencing patterns (if available)

#### Face Validity
**Manual review checklist:**
- Does SF (Boudin) code as progressive? (should be yes)
- Does Orange County code as traditional? (should be yes)
- Do training documents code as neutral? (most should be)
- Are temporal trends plausible? (progressive wave 2018-2020)

## 2. Research Designs

### 2.1 Cross-Sectional Comparison

**Research Question:** Do progressive and traditional DA offices differ in policy orientation?

**Design:**
```
Compare: San Francisco, Alameda, Contra Costa (progressive)
     vs: Orange, Fresno, Kern (traditional)
Outcome: Mean progressive orientation score
Controls: County demographics, crime rates, office size
```

**Statistical Approach:**
- T-tests or Mann-Whitney U for group comparisons
- OLS regression with county fixed effects
- Include controls for document type, year

**Challenges:**
- Selection bias in document production
- Confounding by county characteristics
- May reflect policy emphasis rather than true differences

### 2.2 Time Series / Panel Analysis

**Research Question:** Did DA offices become more progressive over time (2015-2021)?

**Design:**
```
Panel: County-Year observations
Outcome: Proportion of documents coded progressive
Predictors: Year trend, state reforms, DA changes
```

**Statistical Approach:**
- Two-way fixed effects (county + year)
- Difference-in-differences for DA transitions
- Time series with ARIMA for single counties

**Challenges:**
- Unbalanced panel (varying document counts)
- Temporal autocorrelation
- Changing composition of document types over time
- Possible time-varying selection into document production

### 2.3 Event Study: DA Transitions

**Research Question:** Do policies change when a progressive DA takes office?

**Design:**
```
Treatment: Progressive DA election (e.g., SF 2019, LA 2020)
Outcome: Change in progressive orientation of documents
Method: Difference-in-differences or interrupted time series
```

**Example (SF):**
```
Treatment group: San Francisco (Boudin elected 2019)
Control group: Similar counties without DA change
Time periods: 2017-2018 (pre) vs 2020-2021 (post)
```

**Statistical Approach:**
- DiD with parallel trends assumption
- Synthetic control (create synthetic SF from other counties)
- Interrupted time series (if long enough within-county series)

**Challenges:**
- Anticipation effects (policy changes before/after election)
- Selection into treatment (progressive DAs elected in liberal counties)
- Spillover effects (other counties adopt similar policies)
- Small N (few DA transitions in dataset)

### 2.4 Regression Discontinuity Design

**Research Question:** Do close elections reveal causal effect of prosecutor ideology?

**Design:**
```
Running variable: Vote margin in DA election
Cutoff: 50% vote share
Outcome: Progressive orientation of subsequent documents
```

**Feasibility Check:**
- Need DA election results data (not in current dataset)
- Need multiple close elections for power
- RDD works best with 50+ elections; CA has ~58 counties
- Requires merging election data with policy documents

**Statistical Approach:**
- Local linear regression near cutoff
- Bandwidth selection (CCT optimal)
- Robustness checks with varying bandwidths

**Challenges:**
- Small N (few close DA elections in 2015-2021 window)
- Validity threats: manipulation, sorting, measurement error
- Incumbency advantage may affect close elections
- May not identify effect if close elections in moderate counties

### 2.5 Topic Modeling / Text Analysis

**Research Question:** What distinguishes progressive vs traditional policy documents?

**Design:**
```
Method: Structural topic model with ideology as covariate
Data: Full text of documents + LLM ideology coding
Analysis: Which topics correlate with progressive orientation?
```

**Alternative: Keyword Analysis**
```
Progressive keywords: diversion, restorative, racial justice, alternatives
Traditional keywords: enhancement, habitual offender, mandatory, victim impact
Validate: Do these distinguish LLM-coded progressive vs traditional docs?
```

**Statistical Approach:**
- STM with ideology + county covariates
- Topic prevalence by ideology
- LASSO regression of ideology on ngrams

**Challenges:**
- May find topics that are artifacts of document collection
- Circular if keywords used in LLM coding prompt
- Need to validate that topics aren't just document types

## 3. Statistical Considerations

### 3.1 Units of Analysis

**Document-level analysis:**
- Each row = one document
- Appropriate for: document characteristics, topic analysis
- Problem: Multiple documents per office-year (not independent)

**Office-year analysis:**
- Aggregate documents to county-year level
- Appropriate for: time series, panel models
- Problem: Varying number of documents (need weights?)

**Office-level analysis:**
- Aggregate all documents per county
- Appropriate for: cross-sectional comparison
- Problem: Loses temporal variation

**Recommendation:** Choose based on research question, but always cluster standard errors by county (or county-year).

### 3.2 Weighting Issues

**Should you weight documents?**

**Equal weighting (default):**
- Each document counts equally
- Problem: Over-represents offices that produce more documents
- Problem: Training materials may dominate substantive policies

**Weight by inverse document frequency:**
```python
df['weight'] = 1 / df.groupby('county')['filename'].transform('count')
```
- Balances across offices
- Problem: Down-weights well-documented offices (LA, SF)

**Weight by document importance:**
- Weight policy memos > training materials
- Weight office-wide policies > case-specific guidance
- Requires subjective judgment

**Recommendation:** Report both weighted and unweighted results. If results differ substantially, investigate why.

### 3.3 Missing Data

**Types of missingness:**
1. **No documents for county-year:** County didn't produce policies, or didn't respond to PRR
2. **Unclear/not_addressed coding:** Document didn't address topic
3. **Failed extraction:** Scanned PDFs, corrupted files

**Handling:**
- **Complete case analysis:** Drop missing observations (default)
- **Imputation:** Probably not appropriate for categorical data
- **Selection model:** Model probability of having documents
- **Sensitivity analysis:** Bound estimates under different missingness assumptions

### 3.4 Clustered Standard Errors

**Why clustering is essential:**
- Documents within same office are not independent
- Policies may be related across years (serial correlation)
- Residuals correlated within county-year

**Clustering options:**
```stata
# Stata
reg progressive i.year, vce(cluster county)

# R  
library(lmtest)
library(sandwich)
coeftest(model, vcov=vcovCL(model, cluster=~county))

# Python
from linearmodels import PanelOLS
model = PanelOLS(y, X, entity_effects=True)
results = model.fit(cov_type='clustered', cluster_entity=True)
```

**Conservative approach:** Two-way clustering (county + year)

## 4. Threats to Validity

### 4.1 Internal Validity

**Selection bias:**
- Problem: Documents obtained through PRRs may not be representative
- ACLU NC may have targeted progressive-friendly counties
- Offices may strategically produce/withhold certain documents

**Measurement error:**
- LLM coding not perfect (though likely high reliability)
- Some documents are ambiguous (training materials)
- Temporal mismatch (document dated vs actual implementation)

**Confounding:**
- Counties that produce more documents differ on many dimensions
- Progressive counties may have more capacity, resources
- Crime rates, demographics correlate with both docs and ideology

### 4.2 External Validity

**Generalizability:**
- California only (very progressive state)
- 2015-2021 period (specific reform era)
- Counties that responded to PRRs (may be more transparent)

**SUTVA violations:**
- Policies may spill over across counties
- DAs in one county may copy policies from others
- State-level reforms affect all counties simultaneously

### 4.3 Construct Validity

**Are we measuring what we think?**
- Policy documents ≠ actual behavior
- Progressive documents ≠ progressive outcomes
- Office-wide policies may not reflect line prosecutor behavior

**Alternative explanations:**
- "Progressive" policies could be strategic (reducing workload)
- Documents could be performative (signaling without implementation)
- Emphasis on certain topics could reflect external pressure, not ideology

## 5. Best Practices & Recommendations

### 5.1 Transparency & Replication

**Make available:**
- Complete coding protocol (including LLM prompts)
- Random sample of documents with coding
- All code for analysis
- Sensitivity analyses

**Report:**
- Intercoder reliability statistics
- Distribution of unclear/not_addressed responses
- Number of documents per county (show imbalance)
- Robustness to different coding decisions

### 5.2 Sensitivity Analyses

**Essential robustness checks:**
1. Binary vs ordinal ideology measures
2. Weighted vs unweighted analyses
3. Different time periods (drop early/late years)
4. Different document types (exclude training materials)
5. Different thresholds (vary what counts as "progressive")

### 5.3 Triangulation

**Validate with other data sources:**
- Case outcomes (charging rates, sentence lengths)
- Election results (DA ideology should predict policy ideology)
- Media content analysis (news coverage of DA)
- Stakeholder perceptions (defense attorneys, judges)

### 5.4 Qualitative Integration

**Don't rely on quantitative coding alone:**
- Read exemplar documents closely
- Present case studies of specific policy shifts
- Interview DAs, line prosecutors, defense attorneys
- Use quantitative patterns to identify interesting cases

## 6. Example Research Papers

### Paper 1: Cross-Sectional Comparison
**Title:** "Progressive Prosecutors in Practice: Variation in Policy Orientation Across California District Attorneys"

**RQ:** To what extent do progressive and traditional DA offices differ in policy orientation on extensive vs intensive margins?

**Method:**
- Compare 7 progressive counties (SF, Alameda, CC) vs 7 traditional counties
- Outcome: Mean progressive orientation, extensive margin emphasis
- Controls: County demographics, crime rates, office size
- Robustness: Multiple ideology measures, weighted analyses

**Expected findings:**
- Progressive offices score 0.6-0.8 points higher on 5-point scale
- Progressive offices emphasize extensive margin (who gets charged)
- Traditional offices emphasize intensive margin (sentence severity)

### Paper 2: Time Series
**Title:** "The Progressive Prosecutor Wave: Policy Change in California, 2015-2021"

**RQ:** Did DA offices become more progressive during the reform era?

**Method:**
- County-year panel with two-way fixed effects
- Outcome: Proportion progressive documents
- Predictors: Year trend, Prop 47/57 implementation, DA transitions
- IV: Close DA elections as instrument for progressive DA

**Expected findings:**
- 3-5 percentage point increase in progressive orientation per year
- Accelerated after 2018 (progressive DA wave)
- Effect concentrated in charging policies (extensive margin)

### Paper 3: Event Study
**Title:** "Do Progressive Prosecutors Change Policy? Evidence from DA Elections"

**RQ:** Causal effect of electing progressive DA on office policy orientation

**Method:**
- Difference-in-differences comparing SF (Boudin 2019) vs similar counties
- Interrupted time series for LA (Gascon 2020)
- Synthetic control for counties with progressive DA transitions

**Expected findings:**
- 15-25 percentage point increase in progressive documents post-election
- Largest changes in charging, diversion, bail policies
- Effects larger for extensive than intensive margin

## 7. Common Pitfalls to Avoid

1. **Treating documents as equivalent:** A comprehensive policy manual ≠ a 2-page memo
2. **Ignoring document type:** Training materials and policy directives serve different functions
3. **Over-interpreting "not addressed":** Absence of policy ≠ traditional approach
4. **Assuming causality:** Cross-sectional correlations don't imply causation
5. **Ignoring power:** Small N of counties limits ability to detect effects
6. **Overlooking heterogeneity:** One "progressive" county may differ from another
7. **Mechanically applying coding:** Check face validity of surprising results

## 8. Future Directions

### 8.1 Linking to Outcomes
- Merge with case-level data (e.g., UniCourt)
- Do progressive policies predict progressive outcomes?
- Is there policy-practice gap?

### 8.2 Mechanism Studies
- How do policies get implemented?
- Line prosecutor compliance with directives?
- Resistance or buy-in?

### 8.3 Comparative Analysis
- Code documents from other states
- Compare California to national trends
- State-level policy differences

### 8.4 Longitudinal Extension
- Continue coding new documents (2022+)
- Track policy evolution under current DAs
- Measure policy stability vs change

---

## Appendix: Regression Model Specifications

### Model 1: Cross-Sectional OLS
```
progressive_i = β0 + β1*bay_area_i + β2*log(pop)_i + β3*crime_rate_i + ε_i

where i = county
```

### Model 2: Two-Way Fixed Effects
```
progressive_ct = β1*year_t + α_c + γ_t + ε_ct

where c = county, t = year
α_c = county fixed effects
γ_t = year fixed effects
```

### Model 3: Difference-in-Differences
```
progressive_ct = β0 + β1*treat_c + β2*post_t + β3*(treat*post)_ct + X'_ct*γ + ε_ct

where:
treat = 1 if county elected progressive DA
post = 1 if after DA took office
β3 = causal effect of progressive DA
```

### Model 4: Event Study
```
progressive_ct = β0 + Σ_{k≠-1} β_k*D_k_ct + X'_ct*γ + α_c + γ_t + ε_ct

where:
D_k = indicator for k years relative to DA election
k = -3, -2, -1, 0, 1, 2, 3
Omit k=-1 (pre-period)
Plot β_k coefficients to show dynamic effects
```

---

**Version:** 1.0  
**Last Updated:** February 2026  
**Contact:** dyo@berkeley.edu
