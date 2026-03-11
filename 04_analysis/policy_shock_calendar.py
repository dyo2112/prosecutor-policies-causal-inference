"""
Policy Shock Calendar: Precisely-Dated Enforcement Relaxation Events
====================================================================
Curated catalog of California criminal justice policies that significantly
shifted enforcement toward a more relaxed environment --- the kind of changes
that could, in theory, alter public behavior (e.g., avoidance of places
perceived as less safe).

Each entry carries the most precise implementation date available, enabling
event-study and difference-in-differences designs at daily resolution.

Usage:
    python policy_shock_calendar.py [--output-dir DIR] [--link-documents]

Output:
    policy_shock_calendar.csv --- precisely-dated policy shocks
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict


# ---------------------------------------------------------------------------
# Core shock catalog
# ---------------------------------------------------------------------------

POLICY_SHOCKS: List[Dict] = [

    # ===== STATEWIDE LEGISLATION / PROPOSITIONS =====

    {
        "shock_id": "ab_109_realignment",
        "date": "2011-10-01",
        "level": "statewide",
        "county": "All",
        "policy_name": "AB 109 (Public Safety Realignment)",
        "policy_type": "legislation",
        "description": (
            "Transferred incarceration and supervision of non-violent, "
            "non-serious, non-sex-offense felons from state prison to "
            "county jails and probation; reduced state prison population "
            "by ~28,000 in first year"
        ),
        "enforcement_channel": "incarceration",
        "behavioral_channel": "public_safety_perception",
        "severity": "major",
        "source": "Cal. Penal Code § 1170(h); AB 109 (2011)",
    },
    {
        "shock_id": "prop_36_three_strikes_reform",
        "date": "2012-11-07",
        "level": "statewide",
        "county": "All",
        "policy_name": "Proposition 36 (Three Strikes Reform)",
        "policy_type": "proposition",
        "description": (
            "Required third strike to be serious or violent felony; allowed "
            "~2,800 inmates serving life for non-serious third strikes to "
            "petition for resentencing"
        ),
        "enforcement_channel": "sentencing",
        "behavioral_channel": "public_safety_perception",
        "severity": "significant",
        "source": "Cal. Penal Code § 1170.126; Prop 36 (2012)",
    },
    {
        "shock_id": "prop_47",
        "date": "2014-11-05",
        "level": "statewide",
        "county": "All",
        "policy_name": "Proposition 47 (Safe Neighborhoods and Schools Act)",
        "policy_type": "proposition",
        "description": (
            "Reclassified drug possession and property crimes under $950 "
            "(shoplifting, theft, forgery, bad checks, receiving stolen "
            "property) from felonies to misdemeanors; ~1M eligible for "
            "reclassification"
        ),
        "enforcement_channel": "charging",
        "behavioral_channel": "retail_crime_perception",
        "severity": "major",
        "source": "Cal. Penal Code §§ 459.5, 473, 476a, 490.2, 496; Prop 47 (2014)",
    },
    {
        "shock_id": "prop_57",
        "date": "2016-11-09",
        "level": "statewide",
        "county": "All",
        "policy_name": "Proposition 57 (Public Safety and Rehabilitation Act)",
        "policy_type": "proposition",
        "description": (
            "Authorized parole consideration for nonviolent felons; "
            "required judges (not prosecutors) to decide juvenile transfer "
            "to adult court; expanded good-conduct and rehabilitative credits"
        ),
        "enforcement_channel": "sentencing",
        "behavioral_channel": "public_safety_perception",
        "severity": "significant",
        "source": "Cal. Const. Art. I, § 32; Prop 57 (2016)",
        "notes": (
            "Phased implementation: parole consideration began July 2017; "
            "credit changes May-Aug 2017; juvenile provisions Feb 2018"
        ),
    },
    {
        "shock_id": "sb_180_drug_enhancement_repeal",
        "date": "2018-01-01",
        "level": "statewide",
        "county": "All",
        "policy_name": "SB 180 (Drug Prior Enhancement Elimination)",
        "policy_type": "legislation",
        "description": (
            "Eliminated the 3-year sentence enhancement for prior drug "
            "convictions (HS 11370.2), except involving minors; removed "
            "a key sentence multiplier for repeat drug offenders"
        ),
        "enforcement_channel": "enhancements",
        "behavioral_channel": "public_safety_perception",
        "severity": "moderate",
        "source": "Cal. Health & Safety Code § 11370.2; SB 180 (2017)",
    },
    {
        "shock_id": "sb_620_firearm_enhancement_discretion",
        "date": "2018-01-01",
        "level": "statewide",
        "county": "All",
        "policy_name": "SB 620 (Firearm Enhancement Discretion)",
        "policy_type": "legislation",
        "description": (
            "Gave judges discretion to strike previously mandatory firearm "
            "enhancements under PC 12022.5 and 12022.53, which added 3-25 "
            "years to sentences"
        ),
        "enforcement_channel": "enhancements",
        "behavioral_channel": "public_safety_perception",
        "severity": "significant",
        "source": "Cal. Penal Code §§ 12022.5, 12022.53; SB 620 (2017)",
    },
    {
        "shock_id": "sb_1391_juvenile_transfer_ban",
        "date": "2019-01-01",
        "level": "statewide",
        "county": "All",
        "policy_name": "SB 1391 (Juvenile Transfer Ban for 14-15 Year Olds)",
        "policy_type": "legislation",
        "description": (
            "Prohibited transfer of juveniles aged 14-15 to adult court "
            "except in narrow federal prosecution circumstances"
        ),
        "enforcement_channel": "charging",
        "behavioral_channel": "public_safety_perception",
        "severity": "moderate",
        "source": "Cal. Welf. & Inst. Code § 707; SB 1391 (2018)",
    },
    {
        "shock_id": "sb_1393_enhancement_discretion",
        "date": "2019-01-01",
        "level": "statewide",
        "county": "All",
        "policy_name": "SB 1393 (Prior Serious Felony Enhancement Discretion)",
        "policy_type": "legislation",
        "description": (
            "Gave judges discretion to strike the mandatory 5-year prior "
            "serious felony enhancement under PC 667(a); previously this "
            "enhancement was mandatory"
        ),
        "enforcement_channel": "enhancements",
        "behavioral_channel": "public_safety_perception",
        "severity": "moderate",
        "source": "Cal. Penal Code §§ 667, 1385; SB 1393 (2018)",
    },
    {
        "shock_id": "sb_1437_felony_murder",
        "date": "2019-01-01",
        "level": "statewide",
        "county": "All",
        "policy_name": "SB 1437 (Felony Murder Reform)",
        "policy_type": "legislation",
        "description": (
            "Limited felony murder liability to actual killers, those with "
            "intent to kill, or major participants acting with reckless "
            "indifference; created resentencing petition process (PC 1172.6)"
        ),
        "enforcement_channel": "charging",
        "behavioral_channel": "public_safety_perception",
        "severity": "significant",
        "source": "Cal. Penal Code §§ 188, 189, 1172.6; SB 1437 (2018)",
    },
    {
        "shock_id": "zero_bail_statewide",
        "date": "2020-04-13",
        "level": "statewide",
        "county": "All",
        "policy_name": "CA Judicial Council Statewide Zero-Bail Emergency Order",
        "policy_type": "judicial_order",
        "description": (
            "Set bail at $0 for most misdemeanors and lower-level felonies "
            "statewide to reduce jail populations during COVID-19; reduced "
            "jail population by 20,000+"
        ),
        "enforcement_channel": "bail",
        "behavioral_channel": "public_safety_perception",
        "severity": "major",
        "source": "CA Judicial Council Emergency Rule (adopted Apr 6, effective Apr 13, 2020)",
        "end_date": "2020-06-20",
        "notes": (
            "Seven counties (44% of CA population) adopted county-level "
            "zero-bail ~1-3 weeks before statewide order. Statewide order "
            "rescinded June 20, 2020, but many counties continued locally."
        ),
    },
    {
        "shock_id": "ab_3234_misdemeanor_diversion",
        "date": "2021-01-01",
        "level": "statewide",
        "county": "All",
        "policy_name": "AB 3234 (Misdemeanor Diversion)",
        "policy_type": "legislation",
        "description": (
            "Authorized judges to offer misdemeanor diversion (up to 24 "
            "months) for nearly all misdemeanors, even over prosecutor "
            "objection; successful completion results in dismissal"
        ),
        "enforcement_channel": "diversion",
        "behavioral_channel": "quality_of_life_enforcement",
        "severity": "significant",
        "source": "Cal. Penal Code §§ 1001.95-1001.97; AB 3234 (2020)",
    },
    {
        "shock_id": "ab_1950_probation_reform",
        "date": "2021-01-01",
        "level": "statewide",
        "county": "All",
        "policy_name": "AB 1950 (Probation Term Limits)",
        "policy_type": "legislation",
        "description": (
            "Capped felony probation at 2 years (from 3-5) and misdemeanor "
            "probation at 1 year (from 3); applied retroactively to those "
            "currently on probation"
        ),
        "enforcement_channel": "supervision",
        "behavioral_channel": "public_safety_perception",
        "severity": "moderate",
        "source": "Cal. Penal Code § 1203.1; AB 1950 (2020)",
    },
    {
        "shock_id": "sb_81_enhancement_presumption",
        "date": "2022-01-01",
        "level": "statewide",
        "county": "All",
        "policy_name": "SB 81 (Sentencing Enhancement Presumption of Dismissal)",
        "policy_type": "legislation",
        "description": (
            "Created presumption that courts should dismiss sentencing "
            "enhancements unless doing so would endanger public safety; "
            "mandatory dismissal if sentence would exceed 20 years"
        ),
        "enforcement_channel": "enhancements",
        "behavioral_channel": "public_safety_perception",
        "severity": "significant",
        "source": "Cal. Penal Code § 1385(c); SB 81 (2021)",
    },

    # ===== COUNTY-LEVEL DA POLICY SHOCKS =====

    # --- San Francisco ---
    {
        "shock_id": "gascon_sf_takes_office",
        "date": "2011-01-09",
        "level": "county",
        "county": "San Francisco County",
        "policy_name": "George Gascón Appointed SF DA",
        "policy_type": "da_directive",
        "description": (
            "Appointed by Mayor Newsom after Kamala Harris became AG; "
            "first police chief to become DA; implemented cash bail reform, "
            "quality-of-life crime declination, marijuana conviction expungement"
        ),
        "enforcement_channel": "charging",
        "behavioral_channel": "quality_of_life_enforcement",
        "severity": "significant",
        "source": "SF Mayor appointment, Jan 9, 2011",
    },
    {
        "shock_id": "boudin_sf_takes_office",
        "date": "2020-01-08",
        "level": "county",
        "county": "San Francisco County",
        "policy_name": "Chesa Boudin Sworn In as SF DA",
        "policy_type": "da_directive",
        "description": (
            "Day-one directives: ended cash bail requests, banned gang "
            "enhancements, stopped prosecuting quality-of-life crimes, "
            "launched caregiver parent diversion program, ended pretextual "
            "stop prosecutions"
        ),
        "enforcement_channel": "charging",
        "behavioral_channel": "quality_of_life_enforcement",
        "severity": "major",
        "source": "SF DA inauguration, Jan 8, 2020; SFDA press releases",
        "end_date": "2022-07-08",
        "notes": "Recalled June 7, 2022; left office July 8, 2022",
    },

    # --- Los Angeles ---
    {
        "shock_id": "gascon_la_takes_office",
        "date": "2020-12-07",
        "level": "county",
        "county": "Los Angeles County",
        "policy_name": "George Gascón Sworn In as LA DA — Day-One Directives",
        "policy_type": "da_directive",
        "description": (
            "Issued sweeping Special Directives 20-06 through 20-14 on "
            "day one: eliminated cash bail presumption, banned sentencing "
            "enhancements and three-strikes allegations, ended death penalty, "
            "reformed juvenile transfer, launched resentencing review"
        ),
        "enforcement_channel": "charging",
        "behavioral_channel": "public_safety_perception",
        "severity": "major",
        "source": "LA DA Special Directives 20-06 to 20-14 (Dec 7-8, 2020)",
        "end_date": "2024-12-03",
        "notes": "Nathan Hochman took office Dec 3, 2024, reversing most directives",
    },
    {
        "shock_id": "gascon_la_sd_20_07_bail",
        "date": "2020-12-07",
        "level": "county",
        "county": "Los Angeles County",
        "policy_name": "Gascón SD 20-07: Pretrial Release",
        "policy_type": "da_directive",
        "description": (
            "Presumption of pretrial release for all defendants; "
            "prosecutors directed never to request cash bail"
        ),
        "enforcement_channel": "bail",
        "behavioral_channel": "public_safety_perception",
        "severity": "major",
        "source": "LA DA Special Directive 20-07 (Dec 7, 2020)",
    },
    {
        "shock_id": "gascon_la_sd_20_08_enhancements",
        "date": "2020-12-08",
        "level": "county",
        "county": "Los Angeles County",
        "policy_name": "Gascón SD 20-08: Sentencing Enhancements Ban",
        "policy_type": "da_directive",
        "description": (
            "Directed prosecutors not to file sentencing enhancements "
            "or three-strikes allegations in most cases; superseded "
            "existing Legal Policies Manual"
        ),
        "enforcement_channel": "enhancements",
        "behavioral_channel": "public_safety_perception",
        "severity": "major",
        "source": "LA DA Special Directive 20-08 (Dec 8, 2020)",
    },
    {
        "shock_id": "gascon_la_amended_enhancements",
        "date": "2020-12-18",
        "level": "county",
        "county": "Los Angeles County",
        "policy_name": "Gascón Amended Directive on Sentencing Enhancements",
        "policy_type": "da_directive",
        "description": (
            "Amended SD 20-08 after legal challenges; retained core ban "
            "on enhancements with limited exceptions for certain violent "
            "offenses"
        ),
        "enforcement_channel": "enhancements",
        "behavioral_channel": "public_safety_perception",
        "severity": "significant",
        "source": "LA DA press release, Dec 18, 2020",
    },
    {
        "shock_id": "la_zero_bail_extension",
        "date": "2020-06-20",
        "level": "county",
        "county": "Los Angeles County",
        "policy_name": "LA County Zero-Bail Extension Beyond Statewide Order",
        "policy_type": "judicial_order",
        "description": (
            "LA County continued emergency zero-bail schedule after statewide "
            "order rescinded June 20, 2020; pandemic-era zero bail remained "
            "until July 1, 2022"
        ),
        "enforcement_channel": "bail",
        "behavioral_channel": "public_safety_perception",
        "severity": "significant",
        "source": "LA Superior Court emergency bail orders (2020-2022)",
        "end_date": "2022-07-01",
        "notes": (
            "Reinstated May 24, 2023 by Judge Riff ruling; new bail schedule "
            "effective Oct 1, 2023"
        ),
    },
    {
        "shock_id": "la_zero_bail_reinstatement",
        "date": "2023-05-24",
        "level": "county",
        "county": "Los Angeles County",
        "policy_name": "LA County Zero-Bail Reinstated (Court Order)",
        "policy_type": "judicial_order",
        "description": (
            "Judge Riff ruled enforcing bail against indigent defendants "
            "unconstitutional; reinstated zero-bail for misdemeanors and "
            "non-violent felonies via preliminary injunction"
        ),
        "enforcement_channel": "bail",
        "behavioral_channel": "public_safety_perception",
        "severity": "significant",
        "source": "LA Superior Court ruling, Judge Lawrence Riff, May 16/24, 2023",
    },

    # --- Contra Costa ---
    {
        "shock_id": "becton_contra_costa_takes_office",
        "date": "2017-09-18",
        "level": "county",
        "county": "Contra Costa County",
        "policy_name": "Diana Becton Sworn In as Contra Costa DA",
        "policy_type": "da_directive",
        "description": (
            "First woman and first Black DA in county history; stopped "
            "prosecuting low-level drug crimes, established drug diversion, "
            "abolished juvenile justice fees, partnered with Vera Institute "
            "on racial bias evaluation"
        ),
        "enforcement_channel": "charging",
        "behavioral_channel": "quality_of_life_enforcement",
        "severity": "significant",
        "source": "Contra Costa Board of Supervisors appointment, Sep 12/18, 2017",
    },

    # --- Alameda ---
    {
        "shock_id": "price_alameda_takes_office",
        "date": "2023-01-10",
        "level": "county",
        "county": "Alameda County",
        "policy_name": "Pamela Price Sworn In as Alameda DA",
        "policy_type": "da_directive",
        "description": (
            "First Black woman DA in county; pursued alternatives to prison, "
            "addressed racial disparities, restricted sentencing enhancement "
            "requests, issued racial-impact sentencing directive (Apr 14)"
        ),
        "enforcement_channel": "charging",
        "behavioral_channel": "public_safety_perception",
        "severity": "significant",
        "source": "Alameda County DA inauguration, Jan 2023",
        "end_date": "2024-12-05",
        "notes": "Recalled Nov 5, 2024 (62.9%-37.1%); left office Dec 5, 2024",
    },
    {
        "shock_id": "price_alameda_racial_impact_directive",
        "date": "2023-04-14",
        "level": "county",
        "county": "Alameda County",
        "policy_name": "Price Racial-Impact Sentencing Directive",
        "policy_type": "da_directive",
        "description": (
            "Special directive instructing prosecutors to refrain from "
            "seeking elevated sentences where doing so would produce "
            "disproportionate racial impact"
        ),
        "enforcement_channel": "enhancements",
        "behavioral_channel": "public_safety_perception",
        "severity": "significant",
        "source": "Alameda DA special directive, Apr 14, 2023",
    },
]


# ---------------------------------------------------------------------------
# Build DataFrame
# ---------------------------------------------------------------------------

def build_shock_calendar() -> pd.DataFrame:
    """Convert the curated shock list to a clean DataFrame."""
    df = pd.DataFrame(POLICY_SHOCKS)

    df["date"] = pd.to_datetime(df["date"])

    if "end_date" in df.columns:
        df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce")

    if "notes" not in df.columns:
        df["notes"] = np.nan

    # Standardize column order
    cols = [
        "shock_id", "date", "end_date", "level", "county",
        "policy_name", "policy_type", "description",
        "enforcement_channel", "behavioral_channel",
        "severity", "source", "notes",
    ]
    for c in cols:
        if c not in df.columns:
            df[c] = np.nan
    df = df[cols]

    return df.sort_values("date").reset_index(drop=True)


# ---------------------------------------------------------------------------
# Document-level shock detection
# ---------------------------------------------------------------------------

# Map primary_topic_clean → enforcement_channel
TOPIC_TO_CHANNEL = {
    "bail": "bail",
    "sentencing": "sentencing",
    "enhancements": "enhancements",
    "charging_decisions": "charging",
    "diversion": "diversion",
    "juvenile": "charging",
    "death_penalty": "sentencing",
    "racial_justice": "charging",
    "parole_opposition": "sentencing",
    "victim_services": "charging",
    "case_law_update": "sentencing",
    "training_material": "charging",
    "administrative": "charging",
}

# Map primary_topic_clean → behavioral_channel
TOPIC_TO_BEHAVIORAL = {
    "bail": "public_safety_perception",
    "sentencing": "public_safety_perception",
    "enhancements": "public_safety_perception",
    "charging_decisions": "quality_of_life_enforcement",
    "diversion": "quality_of_life_enforcement",
    "juvenile": "public_safety_perception",
    "death_penalty": "public_safety_perception",
    "racial_justice": "public_safety_perception",
}


def _sanitize_id(filename: str) -> str:
    """Turn a filename into a usable shock_id."""
    import re
    name = Path(filename).stem
    name = re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()
    # Truncate to reasonable length
    return name[:80]


def _clean_policy_name(filename: str) -> str:
    """Extract a human-readable policy name from filename."""
    import re
    name = Path(filename).stem
    # Remove date prefix like "2020.12.07_" or "2020_"
    name = re.sub(r"^\d{4}(\.\d{2}\.\d{2})?_", "", name)
    # Remove county prefix like "Los Angeles County_"
    name = re.sub(r"^[A-Za-z ]+County_", "", name)
    # Remove "LA County_" style
    name = re.sub(r"^[A-Z]{2,} County_", "", name)
    return name.replace("_", " ").strip()


def detect_document_shocks(
    cleaned_csv_path: str,
    ideology_threshold: float = 1.5,
) -> pd.DataFrame:
    """
    Identify individual documents that represent clear policy breaks.

    Filters to documents that are: clearly new policy, office-wide,
    mandatory/strong guidance, with strong ideology score, and have a date.

    Args:
        cleaned_csv_path: Path to prosecutor_policies_CLEANED.csv.
        ideology_threshold: Minimum |ideology_score| to qualify (default 1.5).

    Returns:
        DataFrame of document-level shocks.
    """
    df = pd.read_csv(cleaned_csv_path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Apply filters
    mask = (
        (df["policy_change_clean"] == "clearly_new_policy")
        & (df["office_wide_policy_clean"] == "yes")
        & (df["mandates_vs_guidance_clean"].isin(["mandatory", "strong_guidance"]))
        & (df["ideology_score"].abs() >= ideology_threshold)
        & (df["date"].notna())
    )
    shocks = df[mask].copy()

    if shocks.empty:
        return pd.DataFrame()

    # Build output columns
    shocks["shock_id"] = shocks["filename"].apply(_sanitize_id)
    shocks["policy_name"] = shocks["filename"].apply(_clean_policy_name)
    shocks["policy_type"] = "internal_directive"

    shocks["direction"] = np.where(
        shocks["ideology_score"] > 0, "progressive", "traditional"
    )

    shocks["enforcement_channel"] = shocks["primary_topic_clean"].map(
        TOPIC_TO_CHANNEL
    ).fillna("charging")

    shocks["behavioral_channel"] = shocks["primary_topic_clean"].map(
        TOPIC_TO_BEHAVIORAL
    ).fillna("public_safety_perception")

    # Severity assignment
    shocks["severity"] = "moderate"
    shocks.loc[
        (shocks["ideology_score"].abs() == 2.0)
        & (shocks["mandates_vs_guidance_clean"] == "mandatory"),
        "severity",
    ] = "significant"

    # Select and rename columns
    out = shocks[[
        "shock_id", "date", "county", "policy_name", "policy_type",
        "primary_topic_clean", "ideology_score", "direction",
        "enforcement_channel", "behavioral_channel", "severity",
        "mandates_vs_guidance_clean",
        "extensive_margin_direction_clean", "intensive_margin_direction_clean",
        "summary", "filename",
    ]].rename(columns={
        "primary_topic_clean": "primary_topic",
        "mandates_vs_guidance_clean": "mandates_vs_guidance",
        "extensive_margin_direction_clean": "extensive_margin_direction",
        "intensive_margin_direction_clean": "intensive_margin_direction",
    })

    return out.sort_values("date").reset_index(drop=True)


def cross_reference_external_shocks(
    doc_shocks: pd.DataFrame,
    external_shocks: pd.DataFrame,
    window_days: int = 365,
) -> pd.DataFrame:
    """
    For each document shock, find the nearest matching external shock.

    Matching requires:
    - County overlap (statewide external shocks match any county)
    - Date within ±window_days
    - Enforcement channel overlap

    Args:
        doc_shocks: Output of detect_document_shocks().
        external_shocks: Output of build_shock_calendar().
        window_days: Maximum days between document and external shock.

    Returns:
        doc_shocks with added cross-reference columns.
    """
    result = doc_shocks.copy()
    result["nearest_external_shock_id"] = pd.Series(dtype="object")
    result["nearest_external_shock_name"] = pd.Series(dtype="object")
    result["nearest_external_shock_date"] = pd.NaT
    result["days_from_external_shock"] = np.nan
    result["external_shock_match_type"] = pd.Series(dtype="object")

    for idx, doc in result.iterrows():
        doc_date = doc["date"]
        doc_county = doc["county"]
        doc_channel = doc["enforcement_channel"]

        best_dist = float("inf")
        best_shock = None

        for _, ext in external_shocks.iterrows():
            # County filter
            if ext["county"] != "All":
                ext_county = ext["county"].replace(" County", "")
                doc_county_clean = doc_county.replace(" County", "")
                if ext_county != doc_county_clean:
                    continue

            # Date proximity
            days_diff = (doc_date - ext["date"]).days
            if abs(days_diff) > window_days:
                continue

            # Channel overlap (loose: any match counts)
            channel_match = (ext["enforcement_channel"] == doc_channel)
            # Also accept if both deal with same broad area
            if not channel_match:
                # Enhancements and sentencing are related
                related = {
                    ("enhancements", "sentencing"),
                    ("sentencing", "enhancements"),
                    ("charging", "diversion"),
                    ("diversion", "charging"),
                }
                channel_match = (
                    ext["enforcement_channel"], doc_channel
                ) in related

            if not channel_match:
                continue

            # Pick closest by date
            if abs(days_diff) < best_dist:
                best_dist = abs(days_diff)
                best_shock = ext
                best_days = days_diff

        if best_shock is not None:
            result.at[idx, "nearest_external_shock_id"] = best_shock["shock_id"]
            result.at[idx, "nearest_external_shock_name"] = best_shock["policy_name"]
            result.at[idx, "nearest_external_shock_date"] = best_shock["date"]
            result.at[idx, "days_from_external_shock"] = best_days
            match_type = (
                "statewide_legislation"
                if best_shock["level"] == "statewide"
                else "county_da_directive"
            )
            result.at[idx, "external_shock_match_type"] = match_type

    return result


# ---------------------------------------------------------------------------
# Link shocks to internal documents
# ---------------------------------------------------------------------------

def link_shocks_to_documents(
    shock_df: pd.DataFrame,
    metadata_path: str,
    window_days: int = 365,
) -> pd.DataFrame:
    """
    Match policy shocks to internal DA documents from the ACLU dataset.

    For each shock, find documents from the same county (or any county for
    statewide shocks) that mention related keywords within ±window_days
    of the shock date.

    Args:
        shock_df: Policy shock calendar DataFrame.
        metadata_path: Path to prosecutor_policies_metadata.csv.
        window_days: Days before/after shock to search for related docs.

    Returns:
        DataFrame with shock_id and matched document info.
    """
    meta = pd.read_csv(metadata_path)

    # Parse the document date (column index 3 = relevant_date)
    date_col = meta.columns[3]  # 'relevant_date' or similar
    meta["doc_date"] = pd.to_datetime(meta[date_col], errors="coerce")
    meta["filename"] = meta.iloc[:, 0]
    meta["doc_county"] = meta.iloc[:, 1]

    # Keywords per enforcement channel
    channel_keywords = {
        "bail": ["bail", "pretrial", "release"],
        "charging": ["charging", "decline", "prosecut", "filing"],
        "sentencing": ["sentenc", "strike", "three strike", "prison"],
        "enhancements": ["enhancement", "allegation", "strike", "sb 81"],
        "diversion": ["diversion", "divert", "alternative"],
        "incarceration": ["realignment", "ab 109", "jail", "prison"],
        "supervision": ["probation", "supervision", "parole"],
        "quality_of_life_enforcement": [
            "quality of life", "misdemeanor", "drug", "theft", "shoplifting"
        ],
    }

    # Shock-specific keywords
    shock_keywords = {
        "prop_47": ["prop 47", "proposition 47", "safe neighborhoods"],
        "prop_57": ["prop 57", "proposition 57", "early release", "juvenile transfer"],
        "sb_1437_felony_murder": ["sb 1437", "felony murder", "accomplice liability"],
        "ab_109_realignment": ["ab 109", "realignment"],
        "zero_bail_statewide": ["zero bail", "zero-bail", "$0 bail", "emergency bail"],
        "gascon_la_takes_office": ["gascon", "special directive"],
        "gascon_la_sd_20_07_bail": ["bail", "pretrial release", "gascon"],
        "gascon_la_sd_20_08_enhancements": [
            "enhancement", "three strikes", "gascon", "special directive"
        ],
        "boudin_sf_takes_office": ["boudin"],
        "gascon_sf_takes_office": ["gascon"],
        "becton_contra_costa_takes_office": ["becton"],
        "price_alameda_takes_office": ["price"],
        "ab_3234_misdemeanor_diversion": ["ab 3234", "misdemeanor diversion"],
        "ab_1950_probation_reform": ["ab 1950", "probation"],
        "sb_81_enhancement_presumption": ["sb 81", "enhancement"],
        "sb_1393_enhancement_discretion": ["sb 1393", "five-year", "nickel prior"],
    }

    matches = []
    for _, shock in shock_df.iterrows():
        sid = shock["shock_id"]
        shock_date = shock["date"]
        shock_county = shock["county"]

        # Get keywords for this shock
        kw_list = shock_keywords.get(sid, [])
        channel = shock.get("enforcement_channel", "")
        if channel in channel_keywords:
            kw_list = kw_list + channel_keywords[channel]

        if not kw_list:
            continue

        # Filter by county (statewide shocks match all counties)
        if shock_county == "All":
            county_mask = pd.Series([True] * len(meta))
        else:
            county_name = shock_county.replace(" County", "")
            county_mask = meta["doc_county"].str.contains(county_name, case=False, na=False)

        # Filter by date window
        date_mask = (
            meta["doc_date"].notna()
            & (meta["doc_date"] >= shock_date - pd.Timedelta(days=window_days))
            & (meta["doc_date"] <= shock_date + pd.Timedelta(days=window_days))
        )

        # Filter by keyword in filename
        kw_pattern = "|".join(kw_list)
        kw_mask = meta["filename"].str.contains(kw_pattern, case=False, na=False)

        matched = meta[county_mask & date_mask & kw_mask]

        for _, doc in matched.iterrows():
            matches.append({
                "shock_id": sid,
                "shock_date": shock_date,
                "document_filename": doc["filename"],
                "document_date": doc["doc_date"],
                "document_county": doc["doc_county"],
                "days_from_shock": (doc["doc_date"] - shock_date).days,
            })

    return pd.DataFrame(matches).sort_values(
        ["shock_id", "days_from_shock"]
    ).reset_index(drop=True) if matches else pd.DataFrame()


# ---------------------------------------------------------------------------
# Merge shocks with existing disruption scores
# ---------------------------------------------------------------------------

def merge_shocks_with_disruptions(
    shock_df: pd.DataFrame,
    disruptions_path: str,
) -> pd.DataFrame:
    """
    Link policy shocks to existing county-year disruption scores.

    Each shock is matched to the disruption score for the same county-year.
    Statewide shocks are expanded to all counties present in that year.

    Args:
        shock_df: Policy shock calendar DataFrame.
        disruptions_path: Path to policy_disruptions.csv.

    Returns:
        Merged DataFrame with shock info + disruption scores.
    """
    disruptions = pd.read_csv(disruptions_path)

    shock_years = shock_df.copy()
    shock_years["shock_year"] = shock_years["date"].dt.year

    merged_rows = []
    for _, shock in shock_years.iterrows():
        year = shock["shock_year"]
        county = shock["county"]

        if county == "All":
            # Statewide: match to all counties in that year
            year_matches = disruptions[disruptions["year"] == year]
        else:
            year_matches = disruptions[
                (disruptions["county"] == county)
                & (disruptions["year"] == year)
            ]

        for _, d_row in year_matches.iterrows():
            row = shock.to_dict()
            row["disruption_county"] = d_row["county"]
            row["disruption_year"] = d_row["year"]
            row["disruption_score"] = d_row["disruption_score"]
            row["disruption_classification"] = d_row["disruption_classification"]
            row["disruption_direction"] = d_row["direction"]
            merged_rows.append(row)

        # If no disruption data for this county-year, still keep the shock
        if len(year_matches) == 0:
            row = shock.to_dict()
            row["disruption_county"] = county
            row["disruption_year"] = year
            row["disruption_score"] = np.nan
            row["disruption_classification"] = "no_data"
            row["disruption_direction"] = np.nan
            merged_rows.append(row)

    return pd.DataFrame(merged_rows)


# ---------------------------------------------------------------------------
# Event-study helper
# ---------------------------------------------------------------------------

def get_shocks_for_event_study(
    shock_df: pd.DataFrame,
    county: Optional[str] = None,
    min_severity: str = "moderate",
    channels: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Filter shocks suitable for a specific event-study design.

    Args:
        shock_df: Policy shock calendar DataFrame.
        county: If given, include statewide + this county's shocks.
        min_severity: Minimum severity threshold ('moderate', 'significant', 'major').
        channels: If given, filter to these enforcement channels.

    Returns:
        Filtered DataFrame of shocks.
    """
    severity_order = {"moderate": 0, "significant": 1, "major": 2}
    min_level = severity_order.get(min_severity, 0)

    mask = shock_df["severity"].map(
        lambda s: severity_order.get(s, -1) >= min_level
    )

    if county is not None:
        mask = mask & (
            (shock_df["county"] == "All") | (shock_df["county"] == county)
        )

    if channels is not None:
        mask = mask & shock_df["enforcement_channel"].isin(channels)

    return shock_df[mask].copy()


# ---------------------------------------------------------------------------
# Main: generate and export
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate policy shock calendar for event-study designs"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(Path(__file__).resolve().parent.parent / "05_data" / "results"),
        help="Output directory (default: 05_data/results/)",
    )
    parser.add_argument(
        "--link-documents",
        action="store_true",
        help="Also match shocks to internal ACLU documents",
    )
    parser.add_argument(
        "--detect-document-shocks",
        action="store_true",
        help="Detect document-level shocks from cleaned dataset",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build calendar
    print("Building policy shock calendar...")
    shock_df = build_shock_calendar()
    print(f"  {len(shock_df)} precisely-dated policy shocks cataloged")
    print(f"  Statewide: {(shock_df['level'] == 'statewide').sum()}")
    print(f"  County-level: {(shock_df['level'] == 'county').sum()}")

    # Export main calendar
    out_path = output_dir / "policy_shock_calendar.csv"
    shock_df.to_csv(out_path, index=False)
    print(f"  Saved: {out_path}")

    # Link to existing disruption scores if available
    disruptions_path = output_dir / "policy_disruptions.csv"
    if disruptions_path.exists():
        print("Linking to existing disruption scores...")
        merged = merge_shocks_with_disruptions(shock_df, str(disruptions_path))
        merged_path = output_dir / "shocks_with_disruptions.csv"
        merged.to_csv(merged_path, index=False)
        print(f"  Saved: {merged_path}")

    # Link to internal documents if requested
    if args.link_documents:
        metadata_path = (
            Path(__file__).resolve().parent.parent
            / "01_raw_data"
            / "prosecutor_policies_metadata.csv"
        )
        if metadata_path.exists():
            print("Matching shocks to internal ACLU documents...")
            doc_links = link_shocks_to_documents(shock_df, str(metadata_path))
            if len(doc_links) > 0:
                doc_path = output_dir / "shock_document_links.csv"
                doc_links.to_csv(doc_path, index=False)
                print(f"  {len(doc_links)} document matches found")
                print(f"  Saved: {doc_path}")
            else:
                print("  No document matches found")
        else:
            print(f"  Warning: metadata file not found at {metadata_path}")

    # Detect document-level shocks if requested
    if args.detect_document_shocks:
        cleaned_path = (
            Path(__file__).resolve().parent.parent
            / "05_data"
            / "clean"
            / "prosecutor_policies_CLEANED.csv"
        )
        if cleaned_path.exists():
            print("Detecting document-level shocks...")
            doc_shocks = detect_document_shocks(str(cleaned_path))
            if len(doc_shocks) > 0:
                print(f"  {len(doc_shocks)} document shocks detected")
                print(f"  Counties: {doc_shocks['county'].nunique()}")
                print(f"  Progressive: {(doc_shocks['direction'] == 'progressive').sum()}")
                print(f"  Traditional: {(doc_shocks['direction'] == 'traditional').sum()}")

                # Cross-reference with external shocks
                print("Cross-referencing with external shock calendar...")
                doc_shocks = cross_reference_external_shocks(doc_shocks, shock_df)
                n_matched = doc_shocks["nearest_external_shock_id"].notna().sum()
                n_novel = doc_shocks["nearest_external_shock_id"].isna().sum()
                print(f"  {n_matched} matched to external shocks")
                print(f"  {n_novel} novel (no external shock match)")

                doc_path = output_dir / "document_shocks.csv"
                doc_shocks.to_csv(doc_path, index=False)
                print(f"  Saved: {doc_path}")
            else:
                print("  No document shocks detected")
        else:
            print(f"  Warning: cleaned data not found at {cleaned_path}")

    # Print summary
    print("\n=== Policy Shock Calendar Summary ===")
    print(f"Date range: {shock_df['date'].min().date()} to {shock_df['date'].max().date()}")
    print(f"\nBy severity:")
    print(shock_df["severity"].value_counts().to_string())
    print(f"\nBy enforcement channel:")
    print(shock_df["enforcement_channel"].value_counts().to_string())
    print(f"\nBy level:")
    print(shock_df["level"].value_counts().to_string())

    print("\nDone!")


if __name__ == "__main__":
    main()
