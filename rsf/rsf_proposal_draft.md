# Prosecutorial Policy, Racial Justice Reform, and Disparities in California's Criminal Justice System

**Principal Investigators:** Dvir Yogev, UC Berkeley School of Law, Center for Law and Justice; Rebecca Goldstein, New York University

---

## 1. Introduction and Research Question

What if the most celebrated criminal justice reforms of the past decade made racial disparities *worse* — not by design, but by disproportionately benefiting the white defendants easiest to divert, while leaving Black and Hispanic defendants trapped in the serious-charge pipeline that reform never reached? This question sits at the center of a heated national debate: the wave of progressive district attorneys elected after 2020 promised to dismantle systemic racism in charging and sentencing, yet systematic evidence on whether their policies actually narrow racial disparities remains scarce. We lack this evidence not because the question is intractable, but because no measurement infrastructure exists to capture what prosecutors *do* inside their offices — the policies, directives, and memoranda that translate electoral mandates into daily charging decisions.

This project addresses that gap. Building on a pilot that coded 1,865 internal district attorney policy documents from 41 California counties using large language models, we propose to (1) complete the remaining 17 counties to build a full state panel covering all 58 California DA offices, (2) link this policy panel to race-disaggregated outcome data from the California Department of Justice, and (3) estimate the causal effects of prosecutorial policy variation on racial disparities in charging, sentencing, and incarceration. The project is situated within the institutional context of California's Racial Justice Act (AB 2542, 2020), which, for the first time, allows defendants to challenge convictions on the basis of statistical evidence of racial disparities — making the measurement of prosecutorial policy variation not only scientifically important but legally consequential.

**Central Research Questions:**

1. Do counties whose DA offices adopt progressive policies — particularly those emphasizing racial justice — exhibit smaller racial disparities in charging, sentencing, and incarceration?
2. Does the election of reform-oriented prosecutors causally reduce racial disparities, or do aggregate reductions mask persistent or widening racial gaps?
3. Has the California Racial Justice Act's passage altered the relationship between prosecutorial policy and racial disparities?

## 2. Literature Review

Prosecutors wield more discretion over case outcomes than any other actor in the criminal justice system (Pfaff, 2017; Davis, 2007). Charging decisions — which offenses to file, whether to seek enhancements, whom to divert — largely determine defendants' exposure to incarceration, yet these decisions occur behind closed doors with minimal oversight (Sklansky, 2018). A growing literature documents that this discretion produces racial disparities: Black defendants face more serious charges (Rehavi and Starr, 2014), longer sentences (the U.S. Sentencing Commission, 2017), and less access to diversion (Kutateladze et al., 2014) than similarly situated white defendants.

Recent work has begun to examine whether the election of progressive prosecutors alters these patterns. Agan, Doleac, and Harvey (2023) show that progressive prosecutors in large jurisdictions reduce incarceration without increasing crime, but their analysis focuses on aggregate outcomes rather than racial disparities. Krumholz (2022) finds that progressive DAs reduce racial disparities in some charging categories but not others, highlighting the heterogeneity of reform effects. The challenge in this literature is measurement: researchers typically classify prosecutors as "progressive" or "traditional" based on a single dimension (campaign platform, endorsements, or party affiliation), obscuring the multidimensional policy variation within and across offices (Bellin, 2019).

Our project addresses this measurement problem directly. Using large language models to code the actual internal policy documents DA offices produce, we capture variation along multiple dimensions — ideology, charging posture, enhancement policy, diversion support, and racial justice emphasis — at the document level. This approach has precedent in computational text analysis of legal and political documents (Ash and Chen, 2024), but has not been applied to prosecutorial policy. Preliminary coding of 1,865 documents from 41 California counties reveals that the measurement is both valid and informative: racial justice content surged 30 percentage points in 2020, closely tracking the national reckoning following George Floyd's murder, and racial justice emphasis emerged as the single strongest predictor of progressive prosecutorial ideology ($\chi^2$ = 421, p < 0.001, Cramer's V = 0.47).

The California Racial Justice Act (RJA) provides a critical institutional context. Enacted in 2020 and expanded retroactively by AB 256 (2022), the RJA allows defendants to challenge convictions using statistical evidence of racial disparities in charging and sentencing — explicitly overriding the McCleskey v. Kemp (1987) standard that had required proof of intentional discrimination. Early applications demonstrate the Act's significance: in Contra Costa County (2024), gang enhancements were dismissed after data showed Black men were 44% more likely to receive enhancements (Byrne, Kuang, and Steel, 2025). Critically, the court in People v. Windom (2023) cited the *absence* of formal charging policies as evidence of RJA violations, establishing that prosecutorial policy documents — or their absence — are now legally material to racial disparity claims. Yet no systematic data exists on what policies California DA offices actually have, making it impossible to evaluate the RJA's effectiveness at scale.

## 3. Hypotheses

**H1 (Policy-Disparity Link):** Counties whose DA offices adopt policies emphasizing racial justice, diversion, and limits on sentence enhancements will exhibit smaller Black-white and Hispanic-white disparities in felony charging rates, sentence lengths, and incarceration rates.

**H2 (Reform Prosecutor Effect):** The election of progressive prosecutors in close races causally reduces racial disparities in charging and sentencing, not merely aggregate case volumes. We test whether the extensive margin (who enters the system) narrows racial gaps more than the intensive margin (severity of treatment).

**H3 (RJA Interaction):** The passage of the Racial Justice Act in 2020 amplified the relationship between prosecutorial racial justice policies and downstream disparities — DA offices that adopted RJA-responsive policies post-2020 show greater disparity reduction than those maintaining pre-2020 postures.

**H4 (Lowest-Hanging-Fruit Retrenchment):** Progressive reforms disproportionately benefit non-minority defendants by targeting the most easily diverted, least serious cases — populations that skew whiter. If reform prosecutors expand diversion, reduce low-level charging, or decline misdemeanors, the marginal defendants who exit the system may be disproportionately white, while Black and Hispanic defendants — who face more serious charges, longer criminal histories inflated by prior over-policing, and enhancement-heavy cases — remain. Under this hypothesis, aggregate caseloads fall but racial disparities *widen*, producing a perverse equity outcome that headline statistics obscure.

**H5 (Policy Heterogeneity):** The effect of prosecutorial policy on racial disparities varies by policy dimension. Enhancement limitations and diversion expansion disproportionately benefit Black defendants, given documented baseline disparities in enhancement application (92% of gang-enhanced defendants are Black or Hispanic) and diversion access. H5 stands in tension with H4: if reforms target enhancements and gang allegations specifically, they may reach the populations where racial disparities are most concentrated. The empirical question is which policy dimensions dominate in practice.

## 4. Data

### 4.1 Prosecutorial Policy Data (Existing + Extension)

The ACLU of Northern California's Racial Justice Act Public Records Database contains 2,665 internal DA policy documents obtained through public records requests to all 58 California counties. Our pilot used the Anthropic Claude API to code 1,865 documents from 41 counties across 37 dimensions, including ideological orientation (7-point scale), extensive- and intensive-margin posture, specific policy positions (diversion, enhancements, bail, racial justice), and document metadata. Total coding cost was approximately $80 in API fees, completed in under 2 hours — demonstrating the approach's scalability.

The requested funding would complete the panel along two dimensions. First, we will file new public records requests to obtain documents from the 17 counties not covered by the ACLU's original requests, which targeted specific offices and time periods. Second, we will expand temporal coverage for the 41 existing counties, where the ACLU's FOIAs were often narrowly scoped — some counties provided documents only from a single administration or a limited date range. Filling these geographic and temporal gaps is essential for causal designs: the missing counties are disproportionately rural and conservative, biasing cross-sectional estimates, and incomplete time series within covered counties undermine the pre-period data needed for difference-in-differences and event-study designs.

### 4.2 Criminal Justice Outcome Data (Race-Disaggregated)

We will link the policy panel to race-disaggregated outcome data from three sources:

- **California DOJ OpenJustice**: County-level data on arrests, felony filings, dispositions, and sentences disaggregated by race/ethnicity. Available annually for all 58 counties.
- **California DOJ Sentencing Data**: Individual-level sentencing records including offense, enhancements, sentence length, and defendant demographics.
- **Vera Institute Incarceration Trends**: County-level jail population, admission rates, and pretrial detention disaggregated by race. Our pilot merged this with policy data for 34 counties (137 county-years), finding that progressive-coded counties jail 68.5 fewer people per 100,000 (Cohen's d = -0.81, p < 0.001).

### 4.3 Election Data

DA election results with candidate vote totals for computing 1st-2nd place margins, enabling regression discontinuity designs. Our pilot identified 16 elections with proper margin data, including extremely close races (LA 2020: 0.03pp margin; SF 2019: 4.63pp). The full 58-county panel will approximately double this sample.

### 4.4 Human Validation Sample

We will dual-code 200 documents (stratified by county, year, and pilot-coded ideology) with trained research assistants to establish inter-rater reliability and validate the LLM coding pipeline.

## 5. Research Methods and Analytic Plan

### 5.1 Completing the Policy Panel

Completing the panel requires two efforts. First, we will file targeted public records requests to the 17 uncovered counties to obtain their internal policy documents. Second, we will file supplemental requests to the 41 existing counties to fill temporal gaps left by the ACLU's original FOIAs, which were often scoped to narrow time windows or specific administrations. Once obtained, all new documents will be coded using the existing LLM pipeline (prosecutor_policy_coder.py), which uses structured prompts to extract 37 variables per document with high consistency. Quality control includes automated validation checks and manual review of flagged cases. Upon completion, we will have a full 58-county panel with consistent temporal coverage, enabling the pre/post comparisons that causal designs require.

### 5.2 Measurement Validation

To establish that our AI-coded measures capture meaningful policy variation, we will:

1. **Inter-rater reliability**: Dual-code 200 documents with trained RAs; compute Cohen's kappa for categorical variables and ICC for continuous measures.
2. **Construct validity**: Correlate coded ideology with known ground truth (e.g., LA County's Gascón transition shows a Cohen's d = 0.75 shift, p < 0.001; close elections produce 31.2pp more progressive policies, p = 0.010).
3. **Predictive validity**: Test whether coded policy dimensions predict race-disaggregated outcomes beyond what aggregate ideology captures.

### 5.3 Causal Identification Strategies

We employ three complementary designs to isolate causal effects on racial disparities:

**Design 1: Difference-in-Differences (DiD)**

We exploit the staggered adoption of progressive policies across California counties. Our policy shock calendar identifies 24 precisely-dated policy changes (2011-2023) linked to 350+ internal documents. For each shock, we estimate:

$$Y_{ct} = \alpha_c + \gamma_t + \beta \cdot \text{PostPolicy}_{ct} + X_{ct}\delta + \epsilon_{ct}$$

where $Y_{ct}$ is a racial disparity measure (e.g., Black-white felony charging rate ratio) in county $c$ and year $t$, and $\text{PostPolicy}_{ct}$ indicates the adoption of a progressive policy shift. We use the Callaway and Sant'Anna (2021) estimator to handle staggered treatment timing and test for parallel pre-trends.

Our pilot's COVID-controlled DiD for LA County's Gascón transition found clean parallel pre-trends for pretrial detention rates (pre-trend p = 0.897), yielding a DiD estimate of -32.1 per 100,000 — but racial disparity estimates require the race-disaggregated DOJ data this grant would fund.

**Outcome variables for racial disparity:**
- Black-white and Hispanic-white ratios in felony filing rates
- Racial gaps in sentence length conditional on offense
- Racial disparity in enhancement application (particularly gang enhancements)
- Racial gaps in diversion rates
- Black-white incarceration rate ratios

**Design 2: Regression Discontinuity (RDD) Around Close DA Elections**

Close DA elections provide quasi-random assignment of prosecutorial ideology. Our pilot found that elections decided by ≤15pp margins produce 31.2 percentage points more progressive policies than wider margins (p = 0.010), with a continuous relationship between margin and ideology (r = -0.50, p = 0.009). The complete 58-county panel will approximately double the number of close elections available for RDD, increasing statistical power.

The RDD estimator compares racial disparity outcomes in counties where a progressive candidate barely won versus barely lost:

$$\text{Disparity}_{c,t+k} = f(\text{Margin}_c) + \tau \cdot \mathbf{1}[\text{Margin}_c > 0] + \epsilon_c$$

where $\text{Margin}_c$ is the progressive candidate's margin of victory and $\tau$ captures the local average treatment effect on racial disparities.

**Design 3: Event Study Around the Racial Justice Act**

The RJA's passage in 2020 and its retroactive extension in 2022 provide a common shock whose effects vary by county-level policy responsiveness. We estimate:

$$Y_{ct} = \alpha_c + \gamma_t + \sum_{k \neq -1} \beta_k \cdot \mathbf{1}[t = t^* + k] \times \text{HighRJPolicy}_c + X_{ct}\delta + \epsilon_{ct}$$

where $\text{HighRJPolicy}_c$ indicates counties with above-median racial justice policy emphasis post-2020. This design tests whether the RJA's legal infrastructure translates into differential reductions in disparity across counties that substantively engaged with racial justice in their prosecutorial policies versus those that did not.

### 5.4 Racial Disparity Outcomes

Our primary disparity measures are:

| Outcome | Source | Level | Available |
|---------|--------|-------|-----------|
| Felony filing rate ratios (B/W, H/W) | CA DOJ OpenJustice | County-year | Annual, all 58 counties |
| Sentence length gaps | CA DOJ Sentencing | Individual | Annual |
| Enhancement application ratios | CA DOJ Sentencing | Individual | Annual |
| Diversion rate gaps | CA DOJ Dispositions | County-year | Annual |
| Incarceration rate ratios | Vera Institute | County-quarter | 1970-2023 |
| Pretrial detention disparities | CA DOJ / Vera | County-year | Annual |

### 5.5 Addressing Threats to Validity

- **Selection into reform**: Counties that elect progressive prosecutors differ from those that don't. The RDD design addresses this directly; the DiD design tests parallel pre-trends. We additionally control for county demographics, crime rates, and political composition.
- **COVID confounding**: The 2020 timing of both the RJA and many progressive DA elections coincides with COVID-19. Our pilot identified this challenge explicitly — COVID-controlled DiD estimates for aggregate jail outcomes differed substantially from naive estimates. Race-disaggregated data partially addresses this because COVID affected racial groups differentially in ways that can be modeled.
- **Measurement error**: LLM coding introduces noise. The validation study quantifies this: measurement error in the treatment variable attenuates causal estimates toward zero, making our estimates conservative.
- **SUTVA violations**: Prosecutorial policy in one county may affect neighboring counties through defendant migration or policy diffusion. We test for spatial spillovers using contiguous-county controls.

## 6. Preliminary Results

Our pilot analysis provides strong evidence that the proposed measurement infrastructure captures meaningful variation in prosecutorial policy and that this variation correlates with criminal justice outcomes.

**Policy measurement**: The LLM coding system identified six major empirical patterns in California prosecutorial policy: (1) a sustained progressive trend of +0.062 ideology points per year (p = 0.003); (2) a 30-percentage-point surge in racial justice content in 2020; (3) significant geographic clustering with Bay Area offices ranging from strongly progressive (Santa Clara, +0.84) to traditional (Alameda, -0.15); (4) a large Gascón effect in LA County (d = 0.75); (5) emerging emphasis on extensive-margin leniency (who enters the system) over intensive-margin leniency (+11.3pp difference); and (6) racial justice emphasis as the strongest single predictor of progressive ideology (4.6x more likely progressive when high RJ emphasis).

**Outcome linkage**: Cross-sectional analysis merging policy data with Vera Institute jail data for 34 counties (137 county-years) found that ideology correlates with jail population rate at r = -0.222 (p = 0.009), robust to year controls. Progressive-coded counties jail 68.5 fewer people per 100,000 residents (d = -0.81, p < 0.001). However — and this is the critical gap the proposed research addresses — we cannot determine from aggregate jail data whether these differences reflect genuine racial equity gains or simply across-the-board reductions that leave disparities intact. The race-disaggregated DOJ data and complete county panel are necessary to answer this question.

**Election effects**: Close DA elections (≤15pp margin) produce 31.2 percentage points more progressive policies (p = 0.010) and 13 times more emphasis on racial justice than non-close elections, suggesting that electoral competition drives policy adoption. The continuous margin-ideology correlation (r = -0.50, p = 0.009) supports an RDD approach with the expanded sample.

## 7. Project Timeline

| Period | Activity |
|--------|----------|
| **Months 1-2** | File public records requests for 17 missing counties and supplemental requests to fill temporal gaps in 41 existing counties; begin human validation study (200 dual-coded documents); negotiate CA DOJ data access |
| **Months 3-4** | Merge policy panel with race-disaggregated DOJ data; construct racial disparity measures; descriptive analysis of full 58-county panel |
| **Months 5-7** | Implement causal designs: DiD around policy shocks, RDD around close elections, RJA event study; pre-trend tests and robustness checks |
| **Months 8-9** | Heterogeneity analysis: which policy dimensions drive disparity reduction? Which racial groups benefit most? |
| **Months 10-11** | Write and circulate working paper; present preliminary findings |
| **Month 12** | Submit to peer-reviewed journal; present at RSF conference; release replication data |

## 8. Budget Estimates

| Category | Amount |
|----------|--------|
| Co-PI salary — Yogev (2 months summer) | $28,000 |
| Co-PI salary — Goldstein (1 month summer) | $12,000 |
| Graduate research assistant (12 months, 10 hrs/week) | $26,000 |
| Human validation coding (200 docs × 2 coders) | $6,000 |
| Public records request fees (17 new counties + supplemental) | $3,000 |
| LLM API costs (new documents + validation runs) | $1,000 |
| CA DOJ data access fees | $2,000 |
| Travel (RSF conference + 1 academic conference) | $5,500 |
| Computing and software | $3,450 |
| **Subtotal (Direct Costs)** | **$86,950** |
| Indirect costs (15%) | $13,050 |
| **Total** | **$100,000** |

## 9. Significance

This project makes three contributions. First, it produces the first complete panel of coded prosecutorial policies for an entire state, creating a public-use dataset that enables rigorous causal inference about prosecutorial decision-making and racial disparities. Second, it provides the first causal estimates of whether progressive prosecutorial reform reduces racial disparities — rather than aggregate case volumes — addressing a question of immediate policy relevance as reform prosecutors face electoral backlash. Third, by situating these estimates within the California Racial Justice Act's institutional framework, the project provides empirical evidence on whether the RJA's unprecedented legal infrastructure — allowing statistical evidence of disparities to challenge convictions — has been accompanied by substantive policy changes that actually reduce the disparities the Act was designed to expose.

## References

Agan, A., Doleac, J. L., & Harvey, A. (2023). Misdemeanor prosecution. *Quarterly Journal of Economics*, 138(3), 1453-1505.

Ash, E., & Chen, D. L. (2024). Machine learning and law: A survey. *Annual Review of Law and Social Science*, 20.

Bellin, J. (2019). Reassessing prosecutorial power through the lens of mass incarceration. *Michigan Law Review*, 116(5), 835-886.

Byrne, A., Kuang, A., & Steel, A. (2025). The power to be lenient and the power to discriminate. *Berkeley Journal of Criminal Law*, 30(1).

Callaway, B., & Sant'Anna, P. H. C. (2021). Difference-in-differences with multiple time periods. *Journal of Econometrics*, 225(2), 200-230.

Davis, A. J. (2007). *Arbitrary Justice: The Power of the American Prosecutor*. Oxford University Press.

Krumholz, S. (2022). Progressive prosecutors and racial disparities in charging. Working Paper.

Kutateladze, B. L., et al. (2014). Cumulative disadvantage: Examining racial and ethnic disparity in prosecution and sentencing. *Criminology*, 52(3), 514-551.

Pfaff, J. F. (2017). *Locked In: The True Causes of Mass Incarceration and How to Achieve Real Reform*. Basic Books.

Rehavi, M. M., & Starr, S. B. (2014). Racial disparity in federal criminal sentences. *Journal of Political Economy*, 122(6), 1320-1354.

Sklansky, D. A. (2018). The progressive prosecutor's handbook. *UC Davis Law Review Online*, 50, 25-42.
