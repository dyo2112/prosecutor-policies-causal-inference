# Document-Level Policy Shocks — Data Guide

## What This Is

`document_shocks.csv` contains **122 precisely-dated internal DA documents** from California prosecutor offices that represent clear policy breaks — memos and directives that instructed ADAs to change enforcement behavior. Each row is a single document with an exact date.

## How It Was Constructed

We started from 1,865 internal DA documents obtained via ACLU public records requests, each coded (via LLM) for ideology, policy type, scope, and enforcement direction. We then filtered to documents meeting **all five criteria**:

1. **New policy** (`policy_change_clean == 'clearly_new_policy'`) — not a continuation or restatement
2. **Office-wide** (`office_wide_policy_clean == 'yes'`) — applies to all ADAs, not a single case
3. **Mandatory or strong guidance** — actually directs prosecutors to change behavior
4. **Strong ideological signal** (`|ideology_score| >= 1.5` on a -2 to +2 scale) — clear directional shift
5. **Has a date** — usable for event timing

Each document shock was then **cross-referenced against 24 externally-curated policy events** (statewide legislation like Prop 47, DA inaugurations like Gascón in LA) by matching on county, date proximity (±1 year), and enforcement channel overlap.

Result: **95 documents matched** to known external events; **27 are novel** — county-level policy shifts not captured by any external event.

## Key Numbers

| | |
|---|---|
| Total document shocks | 122 |
| Progressive (relaxed enforcement) | 119 |
| Traditional (tightened enforcement) | 3 |
| Counties represented | 24 |
| Matched to known external events | 95 |
| Novel shocks | 27 |

## Most Likely Shocks to Affect Foot Traffic

The strongest candidates are **county-level clusters of mandatory progressive directives** — moments when a DA office issued multiple directives simultaneously shifting enforcement. Ranked by likely behavioral impact:

### Tier 1: Major DA Regime Changes

**1. Los Angeles County — Gascón day-one directives (Dec 7, 2020)**
- 18 documents in one month (Dec 2020), covering bail, enhancements, sentencing, diversion, juvenile justice, death penalty
- All mandatory, all ideology_score = 2.0
- Widely covered in media → high salience for behavioral response
- Matched to external shock: Gascón inauguration

**2. San Francisco — Boudin-era directives (Jan 2021)**
- 4 documents covering racial justice and administrative reforms
- Follows Boudin's Jan 2020 inauguration (captured in external calendar)
- SF had intense public debate about enforcement → high salience

### Tier 2: Significant County Shifts

**3. Santa Clara County — Bail reform memos (Nov 2021 – May 2022)**
- 7 documents, mostly bail reform directives
- Novel — no matching external shock (no progressive DA inauguration)
- Represents an internal policy evolution, not a regime change

**4. Contra Costa County — Post-Becton reforms (2020–2021)**
- 6 documents on racial justice and enforcement policy
- Matched to Becton appointment (Sep 2017) but documents cluster 3+ years later

**5. Los Angeles County — Pre-Gascón diversion directives (Apr 2017)**
- 3 mandatory diversion directives under DA Lacey
- Novel — these predate Gascón and represent reform under a traditional DA

### Tier 3: Statewide Ripple Effects

Many documents (especially racial justice training, bail reform memos) cluster around statewide legislation effective dates:
- **Jan 2019**: SB 1437 (felony murder reform), SB 1393 (enhancement discretion)
- **Jan 2021**: AB 3234 (misdemeanor diversion), AB 1950 (probation reform)
- **Jan 2022**: SB 81 (enhancement presumption)

These represent counties implementing statewide mandates — useful as a "dosage" measure (which counties responded quickly vs. slowly to the same law).

## COVID Confound and Recommended Designs


### Design 1: Boudin Inauguration (Jan 8, 2020) — Cleanest County Shock

- ~9 weeks of clean pre-COVID weekly foot traffic data (Jan 8 → mid-March)
- SF vs. comparable Bay Area counties (San Mateo, Santa Clara, Marin) as controls
- Our data confirms SF issued a pretrial release directive on Jan 22, 2020
- **Limitation**: short post-treatment window before COVID, but enough for a sharp event study showing the immediate jump

### Design 2: Gascón LA (Dec 7, 2020) — Biggest Shock, Within-CA DiD

- 18 document shocks in one month — largest cluster in the data
- **COVID solution**: LA vs. Orange/San Diego/San Bernardino — similar COVID trajectories, no DA regime change. Our data confirms these counties had zero progressive document shocks in Dec 2020
- Identify off the *differential* break in LA at the Gascón moment
- Hourly distribution test: if LA's night-hour visit share drops relative to Orange County, that's not COVID

### Design 3: Statewide Laws with Staggered County Adoption — Best Use of Document Shocks

Key finding: when statewide laws pass, counties adopt at different times:

- **SB 1437 (felony murder, Jan 2019)**: 8 counties with implementing docs, **fully pre-COVID** — most defensible statewide design
- **AB 3234 (misdemeanor diversion, Jan 2021)**: 21 counties with docs — largest cross-county variation, but COVID-period
- **SB 81 (enhancement presumption, Jan 2022)**: 5 counties with docs — late COVID recovery

Design: staggered DiD where treatment onset = the document date (not the law's effective date). Counties that never produced implementing memos serve as never-treated.

### Design 4: Post-COVID Shocks — Pamela Price / LA Zero-Bail (2023)

- Price sworn in Jan 10, 2023; LA zero-bail reinstated May 24, 2023
- Fully post-COVID, foot traffic normalized
- Alameda vs. Contra Costa/Santa Clara for Price; LA vs. Orange/San Diego for zero-bail
- **Limitation**: few internal implementing documents in our data for this period

### What we can plan to do

**Primary**: Boudin (Jan 2020) + Gascón LA (Dec 2020, within-CA DiD). **Robustness**: SB 1437 staggered adoption (2019, fully pre-COVID). **Extension**: Price/LA zero-bail (2023) for out-of-sample validation.

## Column Reference

| Column | Description |
|--------|-------------|
| `date` | Exact document date |
| `county` | County |
| `policy_name` | Human-readable name |
| `ideology_score` | -2.0 to +2.0 (positive = progressive/relaxed) |
| `direction` | `progressive` or `traditional` |
| `enforcement_channel` | `charging`, `bail`, `sentencing`, `enhancements`, `diversion` |
| `severity` | `significant` (mandatory + ideology=±2.0) or `moderate` |
| `summary` | What the document directs (from LLM coding) |
| `nearest_external_shock_id` | Matched external event (or NaN if novel) |
| `days_from_external_shock` | Days between document and external event |
| `external_shock_match_type` | `statewide_legislation`, `county_da_directive`, or NaN |

## Regeneration

```bash
python 04_analysis/policy_shock_calendar.py --link-documents --detect-document-shocks
```
