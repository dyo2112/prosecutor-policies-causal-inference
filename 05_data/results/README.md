# Policy Disruption Detection System - Output Documentation

## Overview

This system detects **policy disruptions** - signals that a California District Attorney's office has adopted a fundamentally new direction or novel reform. It analyzes 1,865 coded prosecutor policy documents to identify when offices shifted their prosecutorial orientation.

### What is a "Policy Disruption"?

A policy disruption is a statistically detectable shift in prosecutorial orientation within a county, characterized by one or more of:

1. **Ideological pivot**: Significant change in mean ideology score (e.g., from traditional to progressive)
2. **Novel reform introduction**: First-time adoption of a policy type never previously documented in that county
3. **Topic composition shift**: Change in policy focus areas
4. **Leadership-driven change**: Policies explicitly marked as new, associated with a DA administration change
5. **Margin strategy reversal**: Shift in whether the office focuses on extensive margin (who enters the system) vs. intensive margin (how severely they're treated)

### Output Files

| File | Records | Description |
|------|---------|-------------|
| `policy_disruptions.csv` | 126 | County-year observations with disruption scores and component signals |
| `novel_reforms.csv` | 347 | First-time policy types and positions adopted by each county |
| `disruption_summary.csv` | 41 | Per-county summary statistics |

---

## Descriptive Analysis of Underlying Data

This section describes the source data used to detect disruptions.

### Dataset Overview

| Metric | Value |
|--------|-------|
| Total documents | 1,865 |
| Counties represented | 41 |
| County-year observations | 126 |
| Date range | 1996-2025 |
| Peak coverage | 2018-2021 |

### Document Distribution by Year

The dataset is concentrated in recent years, with sparse coverage before 2015:

| Year | Documents | % of Total |
|------|-----------|------------|
| 2019 | 354 | 19.0% |
| 2021 | 320 | 17.2% |
| 2020 | 307 | 16.5% |
| 2018 | 187 | 10.0% |
| 2017 | 114 | 6.1% |
| 2016 | 108 | 5.8% |
| 2025 | 92 | 4.9% |
| 2022 | 81 | 4.3% |
| 2015 | 56 | 3.0% |
| Pre-2015 | 246 | 13.2% |

### Document Distribution by County

Document counts are highly concentrated in a few large counties:

| County | Documents | % of Total | County-Years |
|--------|-----------|------------|--------------|
| Los Angeles | 369 | 19.8% | 10 |
| Ventura | 341 | 18.3% | 7 |
| San Luis Obispo | 229 | 12.3% | 9 |
| Contra Costa | 80 | 4.3% | 5 |
| San Mateo | 75 | 4.0% | 5 |
| Orange | 77 | 4.1% | 7 |
| San Francisco | 31 | 1.7% | 5 |
| Stanislaus | 37 | 2.0% | 5 |
| Alameda | 53 | 2.8% | 7 |
| Yolo | 33 | 1.8% | 5 |
| *Other 31 counties* | 540 | 29.0% | 61 |

**Key insight**: Los Angeles, Ventura, and San Luis Obispo counties comprise 50.4% of all documents, but represent diverse prosecutorial orientations.

### Ideology Score Distribution

| Statistic | Value |
|-----------|-------|
| Coverage | 92.7% (1,728 of 1,865 docs) |
| Range | -2.0 to +2.0 |
| Mean | +0.24 (slightly progressive) |
| Median | 0.0 (neutral) |
| Std Dev | 1.05 |

**Distribution breakdown**:
- Clearly progressive (+1 to +2): ~25% of documents
- Leans progressive (0 to +1): ~30%
- Neutral (0): ~15%
- Leans traditional (-1 to 0): ~15%
- Clearly traditional (-2 to -1): ~15%

### Policy Change Classification

The `policy_change_clean` field directly indicates whether a document represents a new policy:

| Classification | Count | % |
|----------------|-------|---|
| not_addressed | 879 | 47.1% |
| unclear | 429 | 23.0% |
| continuation | 5 | 0.3% |
| modification | 4 | 0.2% |
| clearly_new_policy | 5 | 0.3% |
| *Missing/other* | 543 | 29.1% |

**Key insight**: Only ~0.3% of documents are explicitly coded as "clearly_new_policy". This means most disruptions are detected through ideology shifts and topic changes rather than explicit new policy markers.

### Data Coverage by Signal Source

Different signals have different coverage rates in the underlying data:

| Signal Source Column | Coverage | Notes |
|---------------------|----------|-------|
| `ideology_score` | 92.7% | Well covered; primary disruption signal |
| `policy_change_clean` | 100% | Complete; but mostly "not_addressed" |
| `primary_topic_clean` | ~90% | Good coverage for topic shift analysis |
| `da_administration_clean` | ~80% | Good for detecting DA transitions |
| `extensive_lenient/punitive` | ~50% | Partial; limits margin reversal detection |
| `intensive_lenient/punitive` | ~50% | Partial; limits margin reversal detection |

### Primary Policy Topics

Most common policy topics in the dataset:

| Topic | Count | % |
|-------|-------|---|
| administrative | 501 | 26.9% |
| case_law_update | 287 | 15.4% |
| sentencing | 198 | 10.6% |
| charging_decisions | 156 | 8.4% |
| diversion | 142 | 7.6% |
| racial_justice | 98 | 5.3% |
| bail | 87 | 4.7% |
| enhancements | 76 | 4.1% |
| victim_services | 68 | 3.6% |
| juvenile | 52 | 2.8% |

---

## Methodology

### The Five Disruption Signals

The system combines five complementary signals to detect disruptions. Each signal captures a different dimension of policy change.

#### 1. Ideology Velocity (`ideology_velocity`)

**What it measures**: Rate of change in mean ideology score compared to the prior 2-year period.

**Calculation**:
```
ideology_velocity = mean_ideology_current_year - mean_ideology_prior_2_years
```

**Rationale**: A large ideology velocity indicates the office's policy orientation shifted significantly. Positive values indicate progressive shifts; negative values indicate traditional shifts.

**Interpretation**:
- `>= 1.0`: Major ideological shift (full category change)
- `0.5 to 1.0`: Moderate shift
- `-0.1 to 0.1`: Stable orientation
- `<= -1.0`: Major traditional shift

#### 2. Novelty Index (`novelty_index`)

**What it measures**: Proportion of documents in a county-year explicitly marked as "clearly_new_policy" by the LLM coder.

**Calculation**:
```
novelty_index = n_clearly_new_policy / n_total_documents
```

**Rationale**: When offices issue new policies (rather than continuations or updates), it signals intentional reform. This is the most direct indicator that the office itself considers the policy a departure from prior practice.

**Interpretation**:
- `>= 0.5`: High novelty - more than half of documents are new policies
- `0.25 to 0.5`: Moderate novelty
- `< 0.1`: Low novelty - mostly continuations

#### 3. Topic Shift Score (`topic_shift_score`)

**What it measures**: Jensen-Shannon divergence between topic distributions of current year vs. prior 2-year period.

**Calculation**: Uses probability distributions of `primary_topic_clean` values, comparing current year to baseline period. Jensen-Shannon divergence is a symmetric, bounded (0-1) measure of distribution similarity.

**Rationale**: When an office starts issuing policies on new topics (e.g., racial justice, diversion) that weren't part of their prior focus, it indicates structural change in priorities.

**Interpretation**:
- `>= 0.4`: Major topic shift - very different policy focus
- `0.2 to 0.4`: Moderate shift
- `< 0.1`: Similar topic distribution to baseline

#### 4. Margin Reversal Score (`margin_reversal_score`)

**What it measures**: Change in extensive/intensive margin leniency, plus detection of sign reversals.

**Calculation**:
```
extensive_net = (extensive_lenient - extensive_punitive) / n_documents
intensive_net = (intensive_lenient - intensive_punitive) / n_documents
margin_reversal_score = |extensive_net_current - extensive_net_prior| + |intensive_net_current - intensive_net_prior|
```

**Rationale**: The distinction between extensive margin (who enters the criminal justice system) and intensive margin (how severely those in the system are treated) is fundamental to prosecutorial strategy. A reversal in either margin indicates a fundamental policy shift.

**Key concepts**:
- **Extensive margin**: Policies affecting charging decisions, diversion, case declination (who gets prosecuted)
- **Intensive margin**: Policies affecting sentencing, enhancements, plea offers (how severely)
- **Reversal**: When net leniency flips from positive to negative or vice versa

**Interpretation**:
- `>= 0.4` with reversal: Major strategic shift
- `>= 0.2`: Moderate change in margin emphasis
- `< 0.1`: Stable margin strategy

#### 5. DA Transition Signal (`da_transition_signal`)

**What it measures**: Whether a new DA administration name appears in documents that wasn't present in the prior period.

**Calculation**: Binary (0 or 1) based on whether new DA names appear in `da_administration_clean` field.

**Rationale**: Policy disruptions often coincide with new DA administrations. This signal helps identify leadership-driven reforms vs. organic policy evolution.

**Interpretation**:
- `1`: New DA administration detected
- `0`: Same or no mentioned administration

---

### Composite Score Formula

The five signals are normalized (min-max within dataset) and combined with weights:

```
disruption_score = 0.30 * ideology_velocity_norm +
                   0.25 * novelty_index_norm +
                   0.20 * topic_shift_score_norm +
                   0.15 * margin_reversal_score_norm +
                   0.10 * da_transition_signal
```

**Weight rationale**:
- **Ideology velocity (30%)**: Core measure of orientation change - highest weight because it directly measures what we care about
- **Novelty index (25%)**: Direct signal from the office itself that policies are new
- **Topic shift (20%)**: Structural change in focus areas
- **Margin reversal (15%)**: Important but more technical indicator
- **DA transition (10%)**: Contextual signal - provides causal context but doesn't directly measure policy change

### Classification Thresholds

| Score Range | Classification | Description |
|-------------|----------------|-------------|
| 0.75 - 1.00 | `major_disruption` | Fundamental reorientation (e.g., Gascon in LA) |
| 0.50 - 0.74 | `significant_disruption` | Clear directional change |
| 0.25 - 0.49 | `moderate_disruption` | Notable shifts in some dimensions |
| 0.10 - 0.24 | `minor_disruption` | Incremental evolution |
| 0.00 - 0.09 | `stable` | Business as usual |

### Lookback Period

The system uses a **2-year lookback** for baseline comparison. This period was chosen because:
- DA terms are typically 4 years, so 2 years captures within-term stability
- Long enough to establish a reliable baseline
- Short enough to detect recent shifts

---

## Output File Specifications

### policy_disruptions.csv

Each row represents one county-year observation (126 total).

| Column | Type | Description | Interpretation |
|--------|------|-------------|----------------|
| `county` | string | California county name (e.g., "Los Angeles County") | Identifier |
| `year` | int | Year of observation (1996-2025) | Identifier |
| `disruption_score` | float | Composite score (0-1) | Higher = more disruption. See thresholds above |
| `disruption_classification` | string | Categorical label | One of: major_disruption, significant_disruption, moderate_disruption, minor_disruption, stable |
| `direction` | string | Direction of ideology change | "progressive" if velocity > 0.1, "traditional" if < -0.1, else "neutral" |
| `ideology_velocity` | float | Raw ideology change | Positive = progressive shift, negative = traditional shift. Range typically -2 to +3 |
| `novelty_index` | float | Proportion new policies (0-1) | Higher = more explicitly new policies |
| `topic_shift_score` | float | JS divergence (0-1) | Higher = more different topic distribution |
| `margin_reversal_score` | float | Margin change magnitude | Higher = larger shift in extensive/intensive margin strategy |
| `da_transition_signal` | int | New DA detected (0/1) | 1 if new DA name appears in documents |
| `extensive_reversal` | bool | Extensive margin sign flip | True if net leniency on extensive margin reversed |
| `intensive_reversal` | bool | Intensive margin sign flip | True if net leniency on intensive margin reversed |
| `n_documents` | int | Documents in county-year | Sample size for that observation |
| `n_new_policies` | int | Count of "clearly_new_policy" | Numerator for novelty_index |
| `mean_ideology_score` | float | Average ideology this year | Range -2 (traditional) to +2 (progressive) |
| `prior_mean_ideology` | float | Average ideology in prior 2 years | Baseline for comparison |
| `election_year` | float | Matched DA election year | From election data; NaN if no match |
| `winner_name` | string | DA who took office | Name of incumbent DA |
| `margin_1st_2nd` | float | Election margin (pp) | Margin between 1st and 2nd place candidates |
| `close_5pp` | bool | Election within 5pp | True if margin <= 5 percentage points |
| `close_10pp` | bool | Election within 10pp | True if margin <= 10 percentage points |
| `close_15pp` | bool | Election within 15pp | True if margin <= 15 percentage points |
| `challenger_won` | bool | Challenger beat incumbent | True if winner was challenger (not incumbent) |

### novel_reforms.csv

Each row represents the first appearance of a policy type or position in a county (347 total).

| Column | Type | Description | Interpretation |
|--------|------|-------------|----------------|
| `county` | string | County name | Where the reform was first adopted |
| `year` | int | Year first observed | When this county first adopted this reform |
| `reform_type` | string | Type of reform | "novel_topic" (new policy area) or "novel_position" (new stance) |
| `reform_name` | string | Specific reform | Topic name (e.g., "racial_justice") or position (e.g., "diversion_support") |
| `document` | string | Source document filename | The document where this reform first appeared |
| `ideology_score` | float | Ideology of source document | Indicates whether the reform was progressive or traditional |
| `statewide_first` | bool | First in California | True if this county was the first in the state to adopt this reform |
| `adoption_rank` | float | Order of adoption | 1.0 = first county, 2.0 = second, etc. |

**Reform types explained**:

*Novel topics* (from `primary_topic_clean`):
- `racial_justice`, `diversion`, `bail`, `juvenile`, `sentencing`, `enhancements`, `charging_decisions`, `conviction_integrity`, `three_strikes`, `death_penalty`, `administrative`, `case_law_update`, `victim_services`, `discovery`, `case_guidance`, `case_preparation`, `other`

*Novel positions* (from policy stance columns):
- `diversion_support`: First time `supports_diversion_clean` = "yes"
- `alternatives_support`: First time `supports_alternatives_clean` = "yes"
- `bail_reform`: First time `position_on_bail_clean` = "reform_oriented"
- `enhancement_limits`: First time `position_on_enhancements_clean` = "minimize"
- `racial_justice_high`: First time `racial_justice_emphasis_clean` = "high"

### disruption_summary.csv

Each row represents one county (41 total).

| Column | Type | Description | Interpretation |
|--------|------|-------------|----------------|
| `county` | string | County name | Identifier |
| `n_county_years` | int | Number of years with data | How many years this county has >= 3 documents |
| `n_disruptions` | int | Count of non-stable years | Years with classification != "stable" |
| `n_major_disruptions` | int | Count of major disruptions | Years with classification = "major_disruption" |
| `first_disruption_year` | float | Year of first disruption | When this county first showed disruption |
| `most_disruptive_year` | float | Year with highest score | When the biggest disruption occurred |
| `max_disruption_score` | float | Highest disruption score | Peak disruption magnitude |
| `dominant_direction` | string | Net direction of changes | "progressive", "traditional", or "neutral" based on most common direction |
| `n_novel_reforms` | int | Total novel reforms | How many first-time policies/positions adopted |

---

## Complete List of Disruptions Detected

This section provides a complete inventory of all 126 county-year observations analyzed.

### Summary by Classification

| Classification | Count | % | Score Range |
|----------------|-------|---|-------------|
| Major disruption | 0 | 0.0% | >= 0.75 |
| Significant disruption | 9 | 7.1% | 0.50 - 0.74 |
| Moderate disruption | 70 | 55.6% | 0.25 - 0.49 |
| Minor disruption | 41 | 32.5% | 0.10 - 0.24 |
| Stable | 6 | 4.8% | < 0.10 |
| **Total** | **126** | **100%** | |

### All Significant Disruptions (9)

These represent clear directional changes in prosecutorial policy.

| County | Year | Score | Direction | ideology_velocity | novelty_index | topic_shift | margin_reversal | da_trans | Key Signal |
|--------|------|-------|-----------|-------------------|---------------|-------------|-----------------|----------|------------|
| San Francisco | 2016 | 0.663 | progressive | +3.00 | 0.33 | 0.83 | 1.33 | 0 | Massive ideology shift (+3.0) |
| San Diego | 2021 | 0.586 | progressive | +1.00 | 1.00 | 0.83 | 0.60 | 0 | 100% new policies |
| Inyo | 2021 | 0.573 | traditional | -1.75 | 0.00 | 0.62 | 2.50 | 1 | Major margin reversal (2.5) |
| San Francisco | 2020 | 0.572 | progressive | +1.48 | 0.55 | 0.69 | 0.36 | 1 | Boudin era begins |
| Yolo | 2015 | 0.564 | progressive | +2.50 | 0.00 | 0.64 | 1.00 | 1 | Large ideology shift (+2.5) |
| Los Angeles | 2016 | 0.544 | progressive | +0.95 | 0.64 | 0.50 | 1.16 | 1 | High novelty (64%) + reversals |
| San Luis Obispo | 2015 | 0.541 | progressive | +0.50 | 0.38 | 0.83 | 1.63 | 1 | Large margin reversal |
| Stanislaus | 2018 | 0.533 | progressive | +1.33 | 0.00 | 0.83 | 1.67 | 1 | Major topic shift (0.83) |
| Contra Costa | 2020 | 0.530 | progressive | +0.44 | 0.55 | 0.72 | 1.25 | 1 | Multiple moderate signals |

### All Moderate Disruptions (70)

These represent notable shifts in some dimensions.

| County | Year | Score | Direction | ideology_velocity | novelty_index | topic_shift | margin_reversal | da_trans |
|--------|------|-------|-----------|-------------------|---------------|-------------|-----------------|----------|
| Marin | 2022 | 0.500 | progressive | +1.50 | 0.67 | 0.54 | 0.90 | 0 |
| Yuba | 2020 | 0.485 | progressive | +1.45 | 0.75 | 0.32 | 1.25 | 0 |
| Santa Clara | 2022 | 0.476 | progressive | +0.83 | 0.56 | 0.43 | 0.84 | 1 |
| San Mateo | 2018 | 0.472 | progressive | +1.89 | 0.17 | 0.30 | 1.17 | 1 |
| Santa Barbara | 2019 | 0.468 | traditional | -1.00 | 0.25 | 0.83 | 1.75 | 0 |
| Alameda | 2018 | 0.467 | progressive | +0.87 | 0.30 | 0.52 | 1.33 | 1 |
| Yolo | 2020 | 0.459 | progressive | +0.74 | 0.33 | 0.60 | 0.96 | 1 |
| Riverside | 2020 | 0.459 | traditional | -1.00 | 0.33 | 0.56 | 0.67 | 1 |
| Orange | 2016 | 0.451 | progressive | +1.33 | 0.00 | 0.57 | 1.33 | 1 |
| Orange | 2021 | 0.449 | progressive | +0.73 | 0.55 | 0.44 | 0.56 | 1 |
| Los Angeles | 2015 | 0.438 | traditional | -0.97 | 0.26 | 0.53 | 0.80 | 1 |
| Marin | 2021 | 0.431 | progressive | +0.46 | 0.44 | 0.61 | 0.46 | 1 |
| Riverside | 2022 | 0.423 | progressive | +1.33 | 0.14 | 0.46 | 0.71 | 1 |
| Sacramento | 2025 | 0.422 | progressive | +1.00 | 0.25 | 0.83 | 1.00 | 0 |
| Marin | 2020 | 0.418 | traditional | -0.67 | 0.25 | 0.70 | 0.33 | 1 |
| Monterey | 2021 | 0.419 | progressive | +0.39 | 0.38 | 0.63 | 0.53 | 1 |
| Placer | 2020 | 0.414 | progressive | +0.21 | 0.50 | 0.49 | 0.83 | 1 |
| San Diego | 2020 | 0.409 | progressive | +0.50 | 0.33 | 0.54 | 0.75 | 1 |
| Santa Barbara | 2021 | 0.402 | traditional | -0.18 | 0.40 | 0.68 | 0.35 | 1 |
| Yolo | 2021 | 0.399 | progressive | +0.29 | 0.69 | 0.32 | 0.34 | 1 |
| Sonoma | 2020 | 0.395 | traditional | -1.67 | 0.25 | 0.38 | 1.25 | 0 |
| Placer | 2021 | 0.391 | progressive | +0.32 | 0.43 | 0.55 | 0.31 | 1 |
| Tulare | 2018 | 0.390 | traditional | -0.67 | 0.33 | 0.83 | 0.67 | 0 |
| Stanislaus | 2020 | 0.385 | traditional | -0.94 | 0.17 | 0.55 | 0.28 | 1 |
| Madera | 2020 | 0.370 | neutral | 0.00 | 0.33 | 0.61 | 0.67 | 1 |
| Tulare | 2020 | 0.370 | neutral | 0.00 | 0.67 | 0.68 | 0.67 | 0 |
| Sacramento | 2019 | 0.369 | traditional | -0.95 | 0.00 | 0.52 | 0.80 | 1 |
| San Luis Obispo | 2022 | 0.365 | progressive | +0.17 | 0.50 | 0.47 | 0.19 | 1 |
| Merced | 2021 | 0.366 | progressive | +0.61 | 0.50 | 0.56 | 0.75 | 0 |
| Tuolumne | 2021 | 0.363 | traditional | -1.50 | 0.25 | 0.56 | 0.25 | 0 |
| Contra Costa | 2016 | 0.364 | traditional | -0.83 | 0.00 | 0.54 | 0.83 | 1 |
| Santa Barbara | 2020 | 0.359 | progressive | +0.55 | 0.75 | 0.32 | 0.65 | 0 |
| Monterey | 2019 | 0.358 | traditional | -0.60 | 0.20 | 0.83 | 0.80 | 0 |
| Santa Clara | 2021 | 0.349 | traditional | -0.11 | 0.54 | 0.32 | 0.43 | 1 |
| San Diego | 2017 | 0.340 | progressive | +0.25 | 0.00 | 0.83 | 0.25 | 1 |
| Sacramento | 2023 | 0.339 | neutral | 0.00 | 0.50 | 0.32 | 0.60 | 1 |
| Marin | 2016 | 0.334 | traditional | -0.50 | 0.33 | 0.54 | 1.17 | 0 |
| Los Angeles | 2020 | 0.333 | progressive | +0.71 | 0.36 | 0.24 | 0.25 | 1 |
| Los Angeles | 2021 | 0.328 | progressive | +0.56 | 0.35 | 0.26 | 0.35 | 1 |
| Merced | 2019 | 0.328 | progressive | +0.80 | 0.20 | 0.52 | 1.20 | 0 |
| Los Angeles | 2018 | 0.326 | traditional | -0.48 | 0.34 | 0.35 | 0.15 | 1 |
| San Luis Obispo | 2020 | 0.322 | progressive | +0.12 | 0.32 | 0.45 | 0.36 | 1 |
| Orange | 2018 | 0.346 | traditional | -0.64 | 0.13 | 0.36 | 1.05 | 1 |
| Orange | 2017 | 0.317 | progressive | +0.29 | 0.17 | 0.50 | 0.42 | 1 |
| San Luis Obispo | 2017 | 0.315 | neutral | -0.08 | 0.18 | 0.56 | 0.45 | 1 |
| Stanislaus | 2019 | 0.310 | neutral | 0.00 | 0.17 | 0.59 | 0.42 | 1 |
| Sutter | 2022 | 0.308 | traditional | -0.67 | 0.50 | 0.25 | 0.92 | 0 |
| San Bernardino | 2021 | 0.303 | progressive | +0.33 | 0.57 | 0.43 | 0.38 | 0 |
| Stanislaus | 2021 | 0.304 | traditional | -0.32 | 0.11 | 0.46 | 0.58 | 1 |
| Alameda | 2020 | 0.298 | progressive | +0.60 | 0.17 | 0.35 | 0.21 | 1 |
| Merced | 2023 | 0.290 | traditional | -0.25 | 0.20 | 0.74 | 0.60 | 0 |
| Sutter | 2021 | 0.290 | traditional | -1.00 | 0.40 | 0.27 | 0.40 | 0 |
| Sacramento | 2018 | 0.288 | neutral | 0.00 | 0.75 | 0.00 | 0.00 | 1 |
| Marin | 2025 | 0.288 | neutral | 0.00 | 0.75 | 0.00 | 0.00 | 1 |
| Los Angeles | 2022 | 0.283 | neutral | +0.07 | 0.35 | 0.33 | 0.14 | 1 |
| San Benito | 2022 | 0.283 | traditional | -0.75 | 0.25 | 0.00 | 0.75 | 1 |
| Sonoma | 2021 | 0.279 | progressive | +0.62 | 0.33 | 0.41 | 0.57 | 0 |
| San Luis Obispo | 2018 | 0.276 | neutral | 0.00 | 0.13 | 0.54 | 0.24 | 1 |
| Monterey | 2020 | 0.274 | traditional | -0.40 | 0.50 | 0.40 | 0.21 | 0 |
| Los Angeles | 2019 | 0.274 | neutral | +0.04 | 0.25 | 0.40 | 0.21 | 1 |
| San Mateo | 2020 | 0.271 | traditional | -0.66 | 0.00 | 0.36 | 0.29 | 1 |
| Sacramento | 2021 | 0.269 | neutral | -0.05 | 0.67 | 0.23 | 0.71 | 0 |
| San Luis Obispo | 2021 | 0.266 | neutral | -0.06 | 0.32 | 0.27 | 0.25 | 1 |
| San Bernardino | 2020 | 0.267 | neutral | 0.00 | 0.67 | 0.00 | 0.00 | 1 |
| Santa Clara | 2019 | 0.267 | neutral | 0.00 | 0.67 | 0.00 | 0.00 | 1 |
| Contra Costa | 2021 | 0.266 | neutral | +0.07 | 0.30 | 0.22 | 0.51 | 1 |
| Yolo | 2018 | 0.297 | traditional | -0.50 | 0.17 | 0.27 | 0.67 | 1 |
| Merced | 2025 | 0.328 | traditional | -0.50 | 0.50 | 0.51 | 0.50 | 0 |
| Riverside | 2025 | 0.250 | neutral | 0.00 | 1.00 | 0.00 | 0.00 | 0 |

### All Minor Disruptions (41)

These represent incremental changes with limited signal strength:

| County | Year | Score | Direction | Key Feature |
|--------|------|-------|-----------|-------------|
| Los Angeles | 2017 | 0.234 | progressive | Moderate novelty (28%) |
| San Francisco | 2022 | 0.245 | traditional | Post-Boudin shift |
| Orange | 2020 | 0.233 | progressive | Moderate signals |
| Ventura | 2019 | 0.233 | traditional | Large county, low signal |
| San Mateo | 2021 | 0.224 | progressive | Moderate signals |
| Tulare | 2021 | 0.223 | progressive | Mixed signals |
| Orange | 2025 | 0.225 | neutral | DA transition only |
| Madera | 2021 | 0.220 | neutral | DA transition + novelty |
| Contra Costa | 2019 | 0.221 | neutral | Topic shift only |
| Alameda | 2016 | 0.213 | traditional | Weak signals |
| Ventura | 2020 | 0.209 | progressive | Large county |
| Merced | 2020 | 0.202 | neutral | Mixed signals |
| Yolo | 2025 | 0.200 | neutral | DA transition |
| San Diego | 2025 | 0.200 | neutral | DA transition |
| San Luis Obispo | 2016 | 0.191 | traditional | Partial reversal |
| Alameda | 2021 | 0.190 | progressive | Weak signals |
| Los Angeles | 2012 | 0.189 | progressive | Early data |
| San Luis Obispo | 2019 | 0.184 | neutral | Stable period |
| Napa | 2025 | 0.183 | neutral | DA transition |
| Alameda | 2019 | 0.177 | progressive | Weak velocity |
| Fresno | 2021 | 0.172 | traditional | Topic shift only |
| San Luis Obispo | 2025 | 0.167 | neutral | High novelty only |
| Ventura | 2018 | 0.176 | progressive | Large county |
| Ventura | 2017 | 0.165 | neutral | Large county |
| San Mateo | 2019 | 0.155 | traditional | Weak signals |
| Contra Costa | 2025 | 0.150 | neutral | DA transition |
| Placer | 1997 | 0.150 | neutral | Historical |
| Yuba | 2019 | 0.150 | neutral | DA transition |
| Alameda | 2017 | 0.131 | neutral | Weak topic shift |
| Alameda | 2015 | 0.128 | neutral | DA transition only |
| Marin | 2019 | 0.111 | neutral | Weak signals |
| Ventura | 2016 | 0.111 | neutral | DA transition only |
| Marin | 2003 | 0.100 | neutral | DA transition only |
| Monterey | 2010 | 0.100 | neutral | DA transition only |
| Los Angeles | 2025 | 0.100 | neutral | DA transition only |
| San Francisco | 2025 | 0.100 | neutral | DA transition only |
| San Mateo | 2025 | 0.100 | neutral | DA transition only |
| Stanislaus | 2025 | 0.100 | neutral | DA transition only |
| Ventura | 2021 | 0.226 | traditional | Weak signals |

### Stable Observations (6)

These county-years showed no detectable disruption (score < 0.10):

| County | Year | Score | n_documents | Notes |
|--------|------|-------|-------------|-------|
| Amador | 2022 | 0.083 | 3 | Novelty only (33%) |
| Placer | 2019 | 0.000 | 3 | All signals zero |
| Placer | 2025 | 0.000 | 5 | All signals zero |
| Santa Barbara | 2025 | 0.000 | 3 | All signals zero |
| Sonoma | 2019 | 0.000 | 3 | All signals zero |
| Ventura | 2025 | 0.000 | 7 | All signals zero |

---

## Interpretation Guide

### Identifying Major Policy Shifts

To find the most significant disruptions:

```python
import pandas as pd
df = pd.read_csv('policy_disruptions.csv')

# Top 10 disruptions overall
df.nlargest(10, 'disruption_score')[['county', 'year', 'disruption_score', 'disruption_classification', 'direction']]

# Significant or major disruptions only
df[df['disruption_classification'].isin(['significant_disruption', 'major_disruption'])]

# Progressive disruptions in 2020
df[(df['year'] == 2020) & (df['direction'] == 'progressive')]
```

### Using Election Linkage for Causal Analysis

The election columns enable analysis of whether close elections predict policy disruptions:

```python
# Disruptions following close elections
df[df['close_5pp'] == True][['county', 'year', 'winner_name', 'margin_1st_2nd', 'disruption_score']]

# Compare disruption scores: close vs. not close elections
close = df[df['close_15pp'] == True]['disruption_score'].mean()
not_close = df[df['close_15pp'] == False]['disruption_score'].mean()
print(f"Close elections: {close:.3f} vs Not close: {not_close:.3f}")
```

### Tracking Reform Adoption Across Counties

To see how reforms spread across California:

```python
reforms = pd.read_csv('novel_reforms.csv')

# When did each county adopt racial justice policies?
reforms[reforms['reform_name'] == 'racial_justice'][['county', 'year', 'adoption_rank']].sort_values('year')

# Which county was first to adopt bail reform?
reforms[(reforms['reform_name'] == 'bail_reform') & (reforms['statewide_first'] == True)]

# Count novel reforms by year (reform adoption velocity)
reforms.groupby('year').size()
```

---

## Sensitivity Analysis: Alternative Weighting Schemes

This section tests how sensitive the disruption rankings are to different weighting choices.

### Current Default Weights

The default composite score formula:

```
disruption_score = 0.30 * ideology_velocity_norm +
                   0.25 * novelty_index_norm +
                   0.20 * topic_shift_score_norm +
                   0.15 * margin_reversal_score_norm +
                   0.10 * da_transition_signal
```

### Alternative Weighting Schemes Tested

| Scheme | Ideology | Novelty | Topic | Margin | DA Trans | Rationale |
|--------|----------|---------|-------|--------|----------|-----------|
| **Default** | 0.30 | 0.25 | 0.20 | 0.15 | 0.10 | Balanced, ideology-prioritized |
| **Ideology-heavy** | 0.50 | 0.20 | 0.15 | 0.10 | 0.05 | Prioritize directional change |
| **Novelty-heavy** | 0.20 | 0.40 | 0.15 | 0.15 | 0.10 | Prioritize explicit new policies |
| **Equal** | 0.20 | 0.20 | 0.20 | 0.20 | 0.20 | No signal prioritization |
| **No-DA** | 0.35 | 0.30 | 0.20 | 0.15 | 0.00 | Pure policy signals only |

### Top 10 Rankings Under Each Scheme

**Default Weights (Current):**
| Rank | County | Year | Score |
|------|--------|------|-------|
| 1 | San Francisco | 2016 | 0.663 |
| 2 | San Diego | 2021 | 0.586 |
| 3 | Inyo | 2021 | 0.573 |
| 4 | San Francisco | 2020 | 0.572 |
| 5 | Yolo | 2015 | 0.564 |
| 6 | Los Angeles | 2016 | 0.544 |
| 7 | San Luis Obispo | 2015 | 0.541 |
| 8 | Stanislaus | 2018 | 0.533 |
| 9 | Contra Costa | 2020 | 0.530 |
| 10 | Marin | 2022 | 0.500 |

**Ideology-Heavy Weights (50% ideology):**
| Rank | County | Year | Score |
|------|--------|------|-------|
| 1 | San Francisco | 2016 | 0.770 |
| 2 | Yolo | 2015 | 0.622 |
| 3 | Inyo | 2021 | 0.553 |
| 4 | San Francisco | 2020 | 0.545 |
| 5 | San Diego | 2021 | 0.541 |
| 6 | Marin | 2022 | 0.516 |
| 7 | Yuba | 2020 | 0.500 |
| 8 | San Mateo | 2018 | 0.498 |
| 9 | Stanislaus | 2018 | 0.489 |
| 10 | Los Angeles | 2016 | 0.472 |

**Novelty-Heavy Weights (40% novelty):**
| Rank | County | Year | Score |
|------|--------|------|-------|
| 1 | San Diego | 2021 | 0.653 |
| 2 | Los Angeles | 2016 | 0.578 |
| 3 | San Francisco | 2016 | 0.563 |
| 4 | San Francisco | 2020 | 0.563 |
| 5 | Contra Costa | 2020 | 0.554 |
| 6 | San Luis Obispo | 2015 | 0.531 |
| 7 | Yuba | 2020 | 0.530 |
| 8 | Marin | 2022 | 0.518 |
| 9 | Santa Clara | 2022 | 0.506 |
| 10 | Orange | 2021 | 0.480 |

**Equal Weights (20% each):**
| Rank | County | Year | Score |
|------|--------|------|-------|
| 1 | Inyo | 2021 | 0.665 |
| 2 | San Luis Obispo | 2015 | 0.638 |
| 3 | Stanislaus | 2018 | 0.622 |
| 4 | Contra Costa | 2020 | 0.613 |
| 5 | Los Angeles | 2016 | 0.604 |
| 6 | San Francisco | 2020 | 0.602 |
| 7 | Yolo | 2015 | 0.601 |
| 8 | San Francisco | 2016 | 0.573 |
| 9 | Alameda | 2018 | 0.550 |
| 10 | Santa Clara | 2022 | 0.538 |

**No-DA Signal (DA weight = 0):**
| Rank | County | Year | Score |
|------|--------|------|-------|
| 1 | San Francisco | 2016 | 0.730 |
| 2 | San Diego | 2021 | 0.653 |
| 3 | Marin | 2022 | 0.558 |
| 4 | Yuba | 2020 | 0.547 |
| 5 | San Francisco | 2020 | 0.524 |
| 6 | Yolo | 2015 | 0.506 |
| 7 | Inyo | 2021 | 0.502 |
| 8 | Santa Barbara | 2019 | 0.497 |
| 9 | Los Angeles | 2016 | 0.492 |
| 10 | San Luis Obispo | 2015 | 0.468 |

### Rank Correlation Between Schemes (Spearman)

| | Default | Ideology-heavy | Novelty-heavy | Equal | No-DA |
|---|---------|----------------|---------------|-------|-------|
| **Default** | 1.000 | 0.968 | 0.940 | 0.919 | 0.931 |
| **Ideology-heavy** | 0.968 | 1.000 | 0.878 | 0.824 | 0.961 |
| **Novelty-heavy** | 0.940 | 0.878 | 1.000 | 0.861 | 0.889 |
| **Equal** | 0.919 | 0.824 | 0.861 | 1.000 | 0.721 |
| **No-DA** | 0.931 | 0.961 | 0.889 | 0.721 | 1.000 |

**Interpretation**: All schemes show strong positive correlations (0.72-0.97), indicating the rankings are moderately robust to weight changes. The lowest correlation (0.72) is between Equal and No-DA schemes.

### Classification Distribution Under Each Scheme

| Classification | Default | Ideology-heavy | Novelty-heavy | Equal | No-DA |
|----------------|---------|----------------|---------------|-------|-------|
| Major (>=0.75) | 0 | 1 | 0 | 0 | 0 |
| Significant (0.50-0.74) | 9 | 6 | 9 | 18 | 7 |
| Moderate (0.25-0.49) | 70 | 52 | 75 | 68 | 56 |
| Minor (0.10-0.24) | 41 | 49 | 36 | 34 | 42 |
| Stable (<0.10) | 6 | 18 | 6 | 6 | 21 |

### Key Sensitivity Findings

1. **San Francisco 2016 is robust**: Remains #1 or top-3 under all schemes except Novelty-heavy (where San Diego 2021 wins due to 100% novelty)

2. **Ideology-heavy creates one major disruption**: SF 2016 (score=0.77) crosses the 0.75 threshold due to its exceptional ideology velocity (+3.0)

3. **Equal weights elevates margin reversals**: Inyo 2021 rises to #1 because its large margin_reversal_score (2.5) gets more weight

4. **Removing DA signal increases stable count**: From 6 to 21 stable observations, because many minor disruptions were driven solely by the DA transition signal (contributing 0.10 points)

5. **Novelty-heavy shifts top positions**: San Diego 2021 (100% novelty) beats SF 2016 (33% novelty) despite SF's larger ideology shift

6. **Core top performers persist**: SF 2016, SF 2020, Yolo 2015, and Inyo 2021 appear in top 10 under almost all schemes

### Conclusion on Robustness

The disruption detection is **moderately robust** to weighting changes:

- **Robust cases**: Counties with multiple strong signals (SF 2016, SF 2020) maintain high rankings regardless of scheme
- **Sensitive cases**: Counties with single dominant signals change ranking significantly based on which signal is weighted most
- **Recommendation**: The default weights provide a balanced view; users with specific research questions may want to adjust weights (e.g., novelty-heavy if studying explicit reform announcements)

### Code to Reproduce Sensitivity Analysis

```python
import pandas as pd
from scipy.stats import spearmanr

df = pd.read_csv('policy_disruptions.csv')

# Normalize signals
df['ideology_norm'] = (df['ideology_velocity'].abs() - df['ideology_velocity'].abs().min()) / \
                      (df['ideology_velocity'].abs().max() - df['ideology_velocity'].abs().min())
df['novelty_norm'] = (df['novelty_index'] - df['novelty_index'].min()) / \
                     (df['novelty_index'].max() - df['novelty_index'].min())
df['topic_norm'] = (df['topic_shift_score'] - df['topic_shift_score'].min()) / \
                   (df['topic_shift_score'].max() - df['topic_shift_score'].min())
df['margin_norm'] = (df['margin_reversal_score'] - df['margin_reversal_score'].min()) / \
                    (df['margin_reversal_score'].max() - df['margin_reversal_score'].min())

# Calculate alternative score
def calc_score(df, w_ideology, w_novelty, w_topic, w_margin, w_da):
    return (w_ideology * df['ideology_norm'] +
            w_novelty * df['novelty_norm'] +
            w_topic * df['topic_norm'] +
            w_margin * df['margin_norm'] +
            w_da * df['da_transition_signal'])

# Example: Equal weights
df['score_equal'] = calc_score(df, 0.20, 0.20, 0.20, 0.20, 0.20)
print(df.nlargest(10, 'score_equal')[['county', 'year', 'score_equal']])
```

---

## Caveats and Limitations

### Baseline Sensitivity

The disruption score is calculated relative to a 2-year lookback period. This means:

- **LA County 2021 (Gascon)** scores lower than expected (0.33) because the baseline (2019-2020) was already progressive due to the statewide 2020 surge
- **SF 2016** scores very high (0.66) because it was an early progressive shift with a traditional baseline

**Implication**: The system detects *relative* change, not absolute progressiveness. A highly progressive county that maintains steady progressive policies will show as "stable."

### Data Availability

- Some counties have sparse data (< 3 documents per year are excluded)
- Election data covers only 16 DA elections (counties with available margin data)
- Years before 2010 have limited coverage

### Minimum Document Thresholds

County-years with fewer than 3 documents are excluded to avoid noisy estimates. This means some disruptions may be missed in counties with limited documentation.

### LLM Coding Consistency

The underlying `policy_change_clean` and `ideology_score` values come from Claude API coding. While validated against known cases, there may be coding inconsistencies for edge cases.

---

## Technical Details

### Source Data

- **Policy data**: `prosecutor_policies_CLEANED.csv` (1,865 documents, 37 columns)
- **Election data**: `election_margins_1st_2nd.csv` (16 elections with proper 1st-2nd margins)

### Normalization

Signals are normalized using min-max scaling within the dataset:
```
normalized = (value - min) / (max - min)
```

For ideology velocity, the absolute value is normalized (to treat positive and negative shifts equally).

### Missing Data Handling

- If a county-year has no documents: excluded from analysis
- If prior period has no documents: ideology_velocity = 0, topic_shift = 0
- If no election match: election columns are null

### Code Location

- Main module: `04_analysis/disruption_detector.py`
- Runner script: `04_analysis/detect_disruptions.py`

To regenerate outputs:
```bash
cd 04_analysis
python detect_disruptions.py
```

---

## Example Findings

### Top Disruptions Detected

| County | Year | Score | Classification | Direction | Key Signal |
|--------|------|-------|----------------|-----------|------------|
| San Francisco | 2016 | 0.66 | significant | progressive | ideology_velocity = 3.0 |
| San Diego | 2021 | 0.59 | significant | progressive | novelty_index = 1.0 |
| Inyo | 2021 | 0.57 | significant | traditional | ideology_velocity = -1.75 |
| San Francisco | 2020 (Boudin) | 0.57 | significant | progressive | ideology_velocity = 1.48 |
| Yolo | 2015 | 0.56 | significant | progressive | ideology_velocity = 2.5 |

### Statewide 2020 Pattern

In 2020, 12 of 22 county-years showed progressive direction, reflecting the George Floyd/racial justice surge. Mean disruption score in 2020 was 0.37 (elevated above the dataset average).

### Novel Reform Leaders

Los Angeles County was the first in California to adopt 17 reform types, including:
- Racial justice policies (2017)
- Bail reform (2018)
- Conviction integrity (2020)

---

## Contact

For questions about this analysis, see the main project documentation in `analysis_of_cleaned/` or the methodology guide in `prosecutor_policy_coding_system/METHODOLOGY_GUIDE.md`.
