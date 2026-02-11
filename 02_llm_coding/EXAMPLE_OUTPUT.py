"""
Example Output: What Your Coded Data Will Look Like

This shows the structure and format of the CSV file that will be generated
by the coding pipeline. Each row represents one coded document.
"""

# Example row from coded_prosecutor_policies.csv:

{
  "filename": "2020.01.15_San Francisco County_Declination Policy Memo.pdf",
  "county": "San Francisco County",
  "relevant_date": "2020-01-15",
  "coded_at": "2025-10-09T14:23:45",
  
  # DOCUMENT CLASSIFICATION
  "document_type": "policy_memo",
  "primary_topic": "charging_decisions",
  "secondary_topics": ["declination", "diversion", "racial_justice"],
  
  # EXTENSIVE MARGIN (who enters the system)
  "extensive_margin_impact": "high_impact",
  "extensive_margin_direction": "more_lenient",
  "extensive_margin_explanation": "Policy establishes broad declination guidelines for low-level offenses and quality-of-life crimes. Creates presumption against charging for certain categories. Significantly reduces the number of cases entering the system.",
  
  # INTENSIVE MARGIN (how severely people are treated)
  "intensive_margin_impact": "low_impact",
  "intensive_margin_direction": "not_applicable",
  "intensive_margin_explanation": "Document focuses primarily on charging decisions rather than sentencing for those charged. Does not address plea negotiations or sentencing recommendations.",
  
  # IDEOLOGICAL ORIENTATION
  "ideological_orientation": "clearly_progressive",
  "confidence_level": "high",
  "progressive_indicators": [
    "presumption against charging quality-of-life offenses",
    "explicit consideration of racial disparities in enforcement",
    "emphasis on alternatives to prosecution",
    "recognition of collateral consequences",
    "focus on community harm vs technical violations"
  ],
  "traditional_indicators": [
    "maintains mandatory charging for violent felonies",
    "preserves victim notification requirements"
  ],
  "ideological_explanation": "This memo represents a clearly progressive approach to prosecutorial discretion. The policy creates a strong presumption against charging for a wide range of low-level offenses, explicitly considers racial justice implications, and prioritizes community harm over technical legal violations. While it maintains some traditional elements (mandatory violent felony charging), the overall thrust is toward reducing system involvement for low-level offenses.",
  
  # SPECIFIC POLICY POSITIONS
  "supports_diversion": "yes",
  "supports_alternatives_to_incarceration": "yes",
  "position_on_enhancements": "minimize",
  "position_on_three_strikes": "not_addressed",
  "position_on_bail": "not_addressed",
  "position_on_juvenile_transfer": "not_addressed",
  "racial_justice_emphasis": "high",
  
  # ADMINISTRATIVE CONTEXT
  "da_administration_mentioned": "Chesa Boudin",
  "reflects_office_wide_policy": "yes",
  "policy_change_indicator": "clearly_new_policy",
  "mandates_vs_guidance": "mandatory",
  
  # KEY QUOTES
  "key_quotes": [
    {
      "text": "Prosecutors shall decline to file charges in cases where the defendant's conduct, while potentially meeting the technical elements of a crime, does not result in identifiable harm to persons or property.",
      "relevance": "Extensive margin - establishes clear declination standard",
      "page": 2
    },
    {
      "text": "In evaluating whether to file charges, prosecutors must consider the documented racial disparities in enforcement patterns for quality-of-life offenses.",
      "relevance": "Racial justice emphasis in charging decisions",
      "page": 3
    },
    {
      "text": "This policy reflects the office's commitment to reducing unnecessary criminal justice system involvement while maintaining public safety.",
      "relevance": "Progressive framing of prosecutorial mission",
      "page": 1
    }
  ],
  
  # SUMMARY
  "summary": "Office-wide policy memo establishing new declination standards for low-level offenses. Creates presumption against charging for quality-of-life crimes that lack identifiable victim harm. Requires explicit consideration of racial disparities in enforcement. Emphasizes alternatives to prosecution and reduction of system involvement. Represents major shift toward progressive prosecutorial approach under new DA administration."
}


# ===================================================================
# COMPARISON EXAMPLES: Progressive vs Traditional
# ===================================================================

# EXAMPLE 1: Traditional Enhancement Policy (Orange County)
{
  "filename": "2018.09.12_Orange County_Gang Enhancement Guidelines.pdf",
  "county": "Orange County",
  "extensive_margin_impact": "low_impact",
  "extensive_margin_direction": "neutral",
  "intensive_margin_impact": "high_impact",
  "intensive_margin_direction": "more_punitive",
  "intensive_margin_explanation": "Policy provides detailed guidance on charging gang enhancements, emphasizing thorough investigation and documentation. Enhancements significantly increase sentencing exposure for those charged.",
  "ideological_orientation": "clearly_traditional",
  "progressive_indicators": ["requires documented gang membership evidence"],
  "traditional_indicators": [
    "presumption in favor of charging when evidence supports",
    "emphasis on maximum sentences for gang-related crimes",
    "victim impact prioritized over collateral consequences",
    "cooperation with specialized gang units"
  ],
  "position_on_enhancements": "maximize",
  "summary": "Comprehensive guidance on charging gang enhancements with emphasis on thorough documentation and aggressive prosecution of gang-related activity."
}

# EXAMPLE 2: Progressive Diversion Program (Alameda County)
{
  "filename": "2019.05.20_Alameda County_Mental Health Diversion Protocol.pdf",
  "county": "Alameda County",
  "extensive_margin_impact": "high_impact",
  "extensive_margin_direction": "more_lenient",
  "extensive_margin_explanation": "Establishes broad eligibility for mental health diversion, diverting significant numbers of defendants out of traditional prosecution track. Focus on treatment rather than punishment for defendants with mental health conditions.",
  "intensive_margin_impact": "moderate_impact",
  "intensive_margin_direction": "more_lenient",
  "intensive_margin_explanation": "For those who complete diversion, charges are dismissed. For those in traditional track, mental health status considered in sentencing recommendations.",
  "ideological_orientation": "clearly_progressive",
  "progressive_indicators": [
    "broad eligibility criteria for diversion",
    "emphasis on treatment over punishment",
    "recognition that incarceration worsens mental health",
    "partnerships with community treatment providers",
    "trauma-informed approach"
  ],
  "supports_diversion": "yes",
  "supports_alternatives_to_incarceration": "yes",
  "summary": "Comprehensive mental health diversion protocol establishing broad eligibility and treatment-focused approach for defendants with mental health conditions."
}

# EXAMPLE 3: Mixed/Technical Document (Training on Legal Standard)
{
  "filename": "2017.08.10_San Diego County_Brady Disclosure Training.pdf",
  "county": "San Diego County",
  "extensive_margin_impact": "low_impact",
  "extensive_margin_direction": "neutral",
  "intensive_margin_impact": "low_impact", 
  "intensive_margin_direction": "neutral",
  "ideological_orientation": "neutral",
  "confidence_level": "high",
  "progressive_indicators": [],
  "traditional_indicators": [],
  "ideological_explanation": "This training document covers constitutional requirements for Brady disclosure. While proper Brady compliance can be seen as progressive (ensuring fair trials), this is a legal requirement not a discretionary policy choice. Document is instructional rather than ideological.",
  "summary": "Legal training on Brady v. Maryland disclosure obligations. Covers Supreme Court precedent and office procedures for identifying and disclosing exculpatory evidence."
}


# ===================================================================
# DATA STRUCTURE NOTES
# ===================================================================

"""
CSV COLUMNS (in order):
1. filename                                 [string]
2. county                                   [string]
3. relevant_date                            [date]
4. coded_at                                 [datetime]
5. document_type                            [categorical]
6. primary_topic                            [categorical]
7. secondary_topics                         [list/json]
8. extensive_margin_impact                  [categorical: high/moderate/low/not_applicable]
9. extensive_margin_direction               [categorical: more_lenient/more_punitive/neutral/mixed/not_applicable]
10. extensive_margin_explanation            [text]
11. intensive_margin_impact                 [categorical: high/moderate/low/not_applicable]
12. intensive_margin_direction              [categorical: more_lenient/more_punitive/neutral/mixed/not_applicable]
13. intensive_margin_explanation            [text]
14. ideological_orientation                 [categorical: clearly_progressive/leans_progressive/neutral/leans_traditional/clearly_traditional/mixed/unclear]
15. confidence_level                        [categorical: high/medium/low]
16. progressive_indicators                  [list/json]
17. traditional_indicators                  [list/json]
18. ideological_explanation                 [text]
19. supports_diversion                      [categorical: yes/no/unclear/not_addressed]
20. supports_alternatives_to_incarceration  [categorical: yes/no/unclear/not_addressed]
21. position_on_enhancements                [categorical: maximize/selective/minimize/not_addressed]
22. position_on_three_strikes               [categorical: strict_enforcement/flexible/reform_oriented/not_addressed]
23. position_on_bail                        [categorical: high_bail/moderate/reform_oriented/not_addressed]
24. position_on_juvenile_transfer           [categorical: supports_transfer/case_by_case/opposes_transfer/not_addressed]
25. racial_justice_emphasis                 [categorical: high/moderate/low/not_addressed]
26. da_administration_mentioned             [string or "not_mentioned"]
27. reflects_office_wide_policy             [categorical: yes/no/unclear]
28. policy_change_indicator                 [categorical: clearly_new_policy/modification/continuation/unclear]
29. mandates_vs_guidance                    [categorical: mandatory/strong_guidance/suggestion/informational]
30. key_quotes                              [list/json of quote objects]
31. summary                                 [text]

Total: 31 columns
"""

# ===================================================================
# USAGE IN ANALYSIS
# ===================================================================

"""
import pandas as pd

# Load data
df = pd.read_csv('coded_prosecutor_policies.csv')

# Create binary variables
df['is_progressive'] = df['ideological_orientation'].str.contains('progressive').astype(int)
df['extensive_lenient'] = df['extensive_margin_direction'].str.contains('lenient').astype(int)

# Time series of progressive orientation
df['year'] = pd.to_datetime(df['relevant_date']).dt.year
progressive_trend = df.groupby('year')['is_progressive'].mean()

# County comparison
county_ideology = df.groupby('county')['is_progressive'].agg(['mean', 'count'])
county_ideology = county_ideology[county_ideology['count'] >= 20]  # Filter for sufficient n

# Extensive vs intensive focus
extensive_docs = df[df['extensive_margin_impact'].isin(['high_impact', 'moderate_impact'])]
intensive_docs = df[df['intensive_margin_impact'].isin(['high_impact', 'moderate_impact'])]

print(f"Progressive orientation:")
print(f"  Extensive-focused docs: {extensive_docs['is_progressive'].mean():.2%}")
print(f"  Intensive-focused docs: {intensive_docs['is_progressive'].mean():.2%}")
"""
