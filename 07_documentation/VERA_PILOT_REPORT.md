# Vera Jail Data x Prosecutor Policies: Pilot Report

**BERQ-J, UC Berkeley School of Law**
**February 2025**

---

## Objective

This pilot tests whether the AI-coded prosecutor policy ideology scores predict real downstream outcomes — county jail populations, admission rates, and racial disparities — using the Vera Institute's Incarceration Trends dataset.

## Data Linkage

| Dataset | Records | Scope |
|---------|---------|-------|
| **Prosecutor Policies** (AI-coded) | 1,865 documents, aggregated to county-year | 41 CA counties, 2015-2024 |
| **Vera Incarceration Trends** | 245,840 quarterly observations | All US counties, 1970-2024 |
| **Merged panel** | 137 county-year observations | 34 CA counties, 2015-2023 |

---

## Results

### Analysis A: Cross-Sectional Correlations (Ideology vs Jail Outcomes)

| Outcome | r | p-value | Sig |
|---------|---|---------|-----|
| **Jail Population Rate** (per 100k) | **-0.233** | **0.006** | ** |
| **Jail Admission Rate** (per 100k) | **-0.236** | **0.006** | ** |
| Pretrial Share (%) | +0.004 | 0.964 | |
| Black/White Jail Rate Ratio | +0.104 | 0.262 | |
| Jail Utilisation (% capacity) | -0.117 | 0.172 | |

> **Key finding:** More progressive prosecutor ideology correlates significantly with **lower jail population rates** and **lower jail admission rates** (both p < 0.01). No significant relationship with pretrial share or racial disparities in the raw cross-section.

---

### Analysis B: Progressive vs Traditional County Comparison

Counties classified by tercile of mean ideology score:

| Outcome | Progressive | Traditional | Difference | Cohen's d | p |
|---------|-------------|-------------|------------|-----------|---|
| **Jail Pop Rate** (per 100k) | **244.4** | **312.8** | **-68.5** | **-0.81** | **<0.001 \*\*\*** |
| Jail Admission Rate | 3,896.7 | 4,543.3 | -646.5 | -0.32 | 0.169 |
| **Pretrial Share** (%) | **71.0** | **76.8** | **-5.8** | **-0.48** | **0.044 \*** |
| B/W Jail Rate Ratio | 6.9 | 5.0 | +2.0 | +0.57 | 0.014 * |
| Jail Utilisation | 77.0 | 76.0 | +1.0 | +0.06 | 0.777 |

> **Key finding:** Progressive counties have **68.5 fewer people per 100k** in jail than traditional counties — a **large effect** (d = -0.81, p < 0.001). They also have significantly lower pretrial share. However, progressive counties show *higher* Black/White disparity ratios — possibly reflecting the urban demographics of progressive counties where racial disparities are structurally higher.

---

### Analysis C: LA County Natural Experiment (Gascon DiD Preview)

| Outcome | Pre-Gascon (2015-2020) | Gascon Era (2021-2024) | Change |
|---------|----------------------|----------------------|--------|
| **Jail Pop Rate** | 234.3 | 201.9 | **-13.8%** |
| **Jail Admission Rate** | 1,967.5 | 1,210.9 | **-38.5%** |
| **Pretrial Rate** | 146.0 | 105.5 | **-27.7%** |

> **Key finding:** After Gascon took office, LA County saw dramatic declines in all jail metrics — jail admissions fell by nearly **40%**. While confounded by COVID, the magnitude and persistence of the decline is consistent with a real policy effect. This is an ideal candidate for a formal DiD or synthetic control study.

---

### Analysis D: Two-Way Fixed Effects Panel Regression

Within-county, within-year variation (county + year FE):

| Outcome | Beta | SE | t | p | N |
|---------|------|-----|---|---|---|
| Jail Pop Rate | -1.53 | 4.45 | -0.34 | 0.732 | 137 |
| Jail Adm Rate | -42.59 | 71.92 | -0.59 | 0.555 | 137 |
| Pretrial Share | +1.71 | 1.21 | 1.41 | 0.161 | 121 |

> **Note:** TWFE estimates are not significant — **this is expected** given the small panel (137 obs, 34 counties, 9 years). Within-county variation in ideology is limited. This highlights the need for better identification strategies (DiD, RDD, synthetic control) and more data (multi-state expansion).

---

## Figure

![Vera Pilot Analysis](../06_figures/vera_pilot_analysis.png)

---

## Interpretation and Causal Inference Implications

### What the pilot establishes

1. **The data link works.** Policy ideology scores and Vera jail outcomes merge cleanly at county-year level with good coverage (34 of 41 policy counties matched).

2. **There are strong descriptive associations.** Progressive counties have significantly lower jail populations (d = -0.81), and ideology correlates negatively with jail pop and admission rates.

3. **LA County is a compelling natural experiment.** The drop in jail admissions (-38.5%) and population (-13.8%) under Gascon aligns with the progressive policy shift documented in the policy data.

4. **TWFE alone is underpowered.** Within-county variation is insufficient for naive panel regression — we need better identification.

### What a funded extension would enable

| Strategy | What's Needed | Power Implications |
|----------|---------------|-------------------|
| **Difference-in-Differences** | 3-5 more DA transitions with pre/post jail data | Feasible with current CA data |
| **Synthetic Control** | Donor pool of 30+ untreated counties | Already available in Vera data |
| **Regression Discontinuity** | Close election margins + jail outcomes | Need more states for sufficient close elections |
| **Multi-State Expansion** | Code DA documents from 5+ additional states | Dramatically increases power for all designs |

### The key question this pilot can't yet answer

> *Do progressive policy documents actually cause lower jail populations, or do progressive counties simply have lower baseline incarceration for other reasons?*

The cross-sectional associations are **necessary but insufficient** for causation. The LA County natural experiment is **suggestive** but confounded by COVID. A funded extension using formal causal inference methods — with the infrastructure already built — would provide the first credible causal estimates linking prosecutorial ideology to incarceration outcomes.

---

## Replication

```bash
cd 04_analysis
python vera_jail_pilot.py
```

**Output files:**
- `05_data/results/vera_policy_merged.csv` — merged panel
- `05_data/results/vera_correlations.csv` — correlation table
- `05_data/results/vera_group_comparison.csv` — group comparison
- `06_figures/vera_pilot_analysis.png` — 6-panel figure
