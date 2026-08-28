#!/usr/bin/env python3
"""Comprehensive Ambient Listening metrics analysis for UMass data."""

import json
import re
import numpy as np
import pandas as pd

CSV_PATH = "/home/ubuntu/.cursor/projects/workspace/uploads/UMass_AL_8.28_8329.csv"
OUT_PATH = "/workspace/docs/umass-al-metrics.json"

# Script question fields (main, not Details)
SCRIPT_FIELDS = [
    "Greeting",
    "ED Waiting Room",
    "Choice",
    "Communication",
    "Cleanliness",
    "Comfort",
    "Safety",
    "Care Provider Communication",
    "Courtesy and Respect",
    "Staff Work Together",
    "Exceptional Service Recognition",
    "Overall Improvement",
    "Family or Friend Medical Care Suggestion",
    "Room Status [Observation]",
    "White Board [Observation]",
    "Intentional Rounding",
    "Timely Call Button",
    "Medication Communication",
    "New Medication – Side Effects",
    "New Medication - Questions",
    "Noise Disturbance",
    "Quiet - Items Causing Noise",
    "Food and Nutrition",
    "Additional Information",
    "Registration",
    "Pain Management",
    "Anesthesia",
    "Explanation of Anesthesia to understand side effects",
    "Discharge Plan Communication",
    "Discharge from PACU to Floor Unit",
    "PACU Service Recovery",
    "Respect and Courtesy",
    "Caregiver Empathy - Nurses",
    "Caregiver Empathy - PCA/Aids",
    "Caregiver Empathy - Doctors",
    "Quiet",
    "Call Light Responsiveness",
]

# Core patient-experience questions (most relevant for leadership rounding)
CORE_SCRIPT_FIELDS = [
    "Care Provider Communication",
    "Courtesy and Respect",
    "Staff Work Together",
    "Overall Improvement",
    "Family or Friend Medical Care Suggestion",
    "Greeting",
    "Communication",
    "Cleanliness",
    "Comfort",
    "Safety",
]

# Detail/free-text fields
DETAIL_FIELDS = [c for c in pd.read_csv(CSV_PATH, nrows=0).columns if "(Details)" in c or c.endswith("(Details)")]
# Also observation detail fields
DETAIL_FIELDS += [c for c in pd.read_csv(CSV_PATH, nrows=0).columns if "[Observation] (Details)" in c]

# Re-read to get all detail fields properly
all_cols = pd.read_csv(CSV_PATH, nrows=0).columns.tolist()
DETAIL_FIELDS = [c for c in all_cols if "(Details)" in c]
CARE_GRAM_FIELDS = ["Exceptional Service Recognition", "Exceptional Service Recognition (Email)"]
OBSERVATION_FIELDS = ["Room Status [Observation]", "White Board [Observation]"]


def parse_duration_seconds(val):
    """Parse duration like '0:01:33' (H:MM:SS) or '1m 33s' to seconds."""
    if pd.isna(val) or val == "":
        return np.nan
    s = str(val).strip()
    if not s:
        return np.nan
    # H:MM:SS or M:SS format
    if ":" in s:
        parts = s.split(":")
        try:
            parts = [int(p) for p in parts]
            if len(parts) == 3:
                return parts[0] * 3600 + parts[1] * 60 + parts[2]
            if len(parts) == 2:
                return parts[0] * 60 + parts[1]
        except ValueError:
            pass
    total = 0
    m = re.search(r"(\d+)\s*m", s)
    sec = re.search(r"(\d+)\s*s", s)
    if m:
        total += int(m.group(1)) * 60
    if sec:
        total += int(sec.group(1))
    if total == 0 and s.isdigit():
        return float(s)
    return total if total > 0 else np.nan


def parse_datetime(val):
    if pd.isna(val):
        return pd.NaT
    s = str(val).strip()
    s = re.sub(r"\s+EDT$|\s+EST$", "", s)
    return pd.to_datetime(s, format="%m/%d/%Y %I:%M %p", errors="coerce")


def is_populated(val):
    if pd.isna(val):
        return False
    s = str(val).strip()
    return s != "" and s.lower() not in ("nan", "none", "n/a")


def pct(n, d):
    return round(100 * n / d, 1) if d > 0 else 0.0


def compare_group(df, al_val, label):
    g = df[df["al_group"] == al_val]
    n = len(g)
    return {"label": label, "n": n}


def main():
    df = pd.read_csv(CSV_PATH)
    df["interaction_time"] = df["Interaction Time"].apply(parse_datetime)
    df["duration_sec"] = df["Interaction Duration"].apply(parse_duration_seconds)

    # Completed rounds = patient was rounded on
    completed_mask = df["Ability to Round"].astype(str).str.contains("Yes", na=False)
    df_completed = df[completed_mask].copy()

    df_completed["al_group"] = df_completed["Ambient Listening"].map({"Yes": "AL Yes", "No": "AL No"})

    # Exclude duration outliers > 30 min (1800s)
    df_completed = df_completed[
        df_completed["duration_sec"].isna() | (df_completed["duration_sec"] <= 1800)
    ]

    al_yes = df_completed[df_completed["al_group"] == "AL Yes"]
    al_no = df_completed[df_completed["al_group"] == "AL No"]

    results = {
        "source": "UMass Community Patient Experience / Leadership Rounding",
        "date_range": {
            "min": str(df["interaction_time"].min().date()) if df["interaction_time"].notna().any() else None,
            "max": str(df["interaction_time"].max().date()) if df["interaction_time"].notna().any() else None,
        },
        "total_interactions": len(df),
        "completed_rounds": {
            "total": len(df_completed),
            "al_yes": len(al_yes),
            "al_no": len(al_no),
        },
        "adoption": {
            "all_interactions_al_yes": int((df["Ambient Listening"] == "Yes").sum()),
            "all_interactions_al_no": int((df["Ambient Listening"] == "No").sum()),
            "al_adoption_rate_pct": pct((df["Ambient Listening"] == "Yes").sum(), len(df)),
            "declined_to_record_yes": int((df["Declined to Record"] == "Yes").sum()),
            "declined_to_record_no": int((df["Declined to Record"] == "No").sum()),
            "declined_rate_pct": pct((df["Declined to Record"] == "Yes").sum(), len(df)),
            "declined_among_al_yes": int(
                ((df["Ambient Listening"] == "Yes") & (df["Declined to Record"] == "Yes")).sum()
            ),
            "declined_among_al_no": int(
                ((df["Ambient Listening"] == "No") & (df["Declined to Record"] == "Yes")).sum()
            ),
        },
    }

    # Documentation time
    def duration_stats(group):
        d = group["duration_sec"].dropna()
        if len(d) == 0:
            return {}
        return {
            "n_with_duration": int(len(d)),
            "median_sec": round(float(d.median()), 1),
            "mean_sec": round(float(d.mean()), 1),
            "median_fmt": f"{int(d.median() // 60)}m {int(d.median() % 60)}s" if len(d) else None,
        }

    dur_yes = duration_stats(al_yes)
    dur_no = duration_stats(al_no)
    if dur_yes.get("median_sec") and dur_no.get("median_sec"):
        reduction = (dur_no["median_sec"] - dur_yes["median_sec"]) / dur_no["median_sec"] * 100
        dur_yes["reduction_vs_no_pct"] = round(reduction, 1)
        dur_yes["seconds_saved"] = round(dur_no["median_sec"] - dur_yes["median_sec"], 1)

    results["documentation_time"] = {
        "al_yes": dur_yes,
        "al_no": dur_no,
        "outlier_exclusion": ">30 min excluded",
    }

    # Script completion - all script fields
    def script_completion(group, fields):
        applicable = []
        for _, row in group.iterrows():
            answered = sum(1 for f in fields if f in group.columns and is_populated(row.get(f)))
            applicable.append(answered)
        if not applicable:
            return {}
        arr = np.array(applicable)
        total_fields = len(fields)
        return {
            "avg_fields_answered": round(float(arr.mean()), 1),
            "median_fields_answered": int(np.median(arr)),
            "pct_all_fields_answered": round(100 * (arr == total_fields).mean(), 1),
            "avg_completion_pct": round(100 * arr.mean() / total_fields, 1),
            "total_script_fields": total_fields,
        }

    # Script completion - core fields only
    core_yes = script_completion(al_yes, CORE_SCRIPT_FIELDS)
    core_no = script_completion(al_no, CORE_SCRIPT_FIELDS)
    if core_yes and core_no:
        core_yes["completion_pts_higher_than_no"] = round(
            core_yes["avg_completion_pct"] - core_no["avg_completion_pct"], 1
        )

    all_yes = script_completion(al_yes, SCRIPT_FIELDS)
    all_no = script_completion(al_no, SCRIPT_FIELDS)

    results["script_completion"] = {
        "core_fields": {"fields": CORE_SCRIPT_FIELDS, "al_yes": core_yes, "al_no": core_no},
        "all_script_fields": {"al_yes": all_yes, "al_no": all_no},
    }

    # Per-question completion rates
    per_q = {}
    for field in CORE_SCRIPT_FIELDS + OBSERVATION_FIELDS:
        if field not in df_completed.columns:
            continue
        yes_rate = pct(al_yes[field].apply(is_populated).sum(), len(al_yes))
        no_rate = pct(al_no[field].apply(is_populated).sum(), len(al_no))
        per_q[field] = {
            "al_yes_pct": yes_rate,
            "al_no_pct": no_rate,
            "diff_pts": round(yes_rate - no_rate, 1),
            "al_yes_n": int(al_yes[field].apply(is_populated).sum()),
            "al_no_n": int(al_no[field].apply(is_populated).sum()),
        }
    results["per_question_completion"] = per_q

    # Free text capture
    def free_text_stats(group):
        counts = []
        has_any = []
        for _, row in group.iterrows():
            n = sum(1 for f in DETAIL_FIELDS if f in group.columns and is_populated(row.get(f)))
            counts.append(n)
            has_any.append(n > 0)
        arr = np.array(counts)
        return {
            "pct_rounds_with_any_free_text": round(100 * np.mean(has_any), 1),
            "avg_detail_fields_populated": round(float(arr.mean()), 1),
            "median_detail_fields": int(np.median(arr)),
            "rounds_with_free_text_n": int(sum(has_any)),
        }

    ft_yes = free_text_stats(al_yes)
    ft_no = free_text_stats(al_no)
    if ft_yes and ft_no:
        ft_yes["multiplier_vs_no"] = round(
            ft_yes["avg_detail_fields_populated"] / max(ft_no["avg_detail_fields_populated"], 0.01), 1
        )
        ft_yes["pts_higher_any_free_text"] = round(
            ft_yes["pct_rounds_with_any_free_text"] - ft_no["pct_rounds_with_any_free_text"], 1
        )

    results["free_text"] = {"al_yes": ft_yes, "al_no": ft_no, "detail_field_count": len(DETAIL_FIELDS)}

    # Care grams
    def care_gram_stats(group):
        esr = group["Exceptional Service Recognition"].apply(is_populated).sum() if "Exceptional Service Recognition" in group.columns else 0
        email = (
            group["Exceptional Service Recognition (Email)"].apply(is_populated).sum()
            if "Exceptional Service Recognition (Email)" in group.columns
            else 0
        )
        either = (
            (group["Exceptional Service Recognition"].apply(is_populated))
            | (group["Exceptional Service Recognition (Email)"].apply(is_populated))
        ).sum()
        return {
            "exceptional_service_recognition_n": int(esr),
            "exceptional_service_recognition_pct": pct(esr, len(group)),
            "email_n": int(email),
            "email_pct": pct(email, len(group)),
            "either_n": int(either),
            "either_pct": pct(either, len(group)),
        }

    cg_yes = care_gram_stats(al_yes)
    cg_no = care_gram_stats(al_no)
    results["care_grams"] = {"al_yes": cg_yes, "al_no": cg_no}

    # Whiteboard observations
    wb_yes = pct(al_yes["White Board [Observation]"].apply(is_populated).sum(), len(al_yes)) if len(al_yes) else 0
    wb_no = pct(al_no["White Board [Observation]"].apply(is_populated).sum(), len(al_no)) if len(al_no) else 0
    results["whiteboard_observation"] = {
        "al_yes_pct": wb_yes,
        "al_no_pct": wb_no,
        "diff_pts": round(wb_yes - wb_no, 1),
    }

    # Overall improvement details
    oi_yes = pct(al_yes["Overall Improvement (Details)"].apply(is_populated).sum(), len(al_yes)) if len(al_yes) else 0
    oi_no = pct(al_no["Overall Improvement (Details)"].apply(is_populated).sum(), len(al_no)) if len(al_no) else 0
    results["overall_improvement_details"] = {
        "al_yes_pct": oi_yes,
        "al_no_pct": oi_no,
        "diff_pts": round(oi_yes - oi_no, 1),
    }

    # Per-rounder breakdown
    rounders = {}
    for name, grp in df_completed.groupby("Interaction Created By"):
        al_sub = grp[grp["Ambient Listening"] == "Yes"]
        no_sub = grp[grp["Ambient Listening"] == "No"]
        rounders[name] = {
            "total_completed": len(grp),
            "al_yes_n": len(al_sub),
            "al_no_n": len(no_sub),
            "al_adoption_pct": pct(len(al_sub), len(grp)),
        }
        if len(al_sub) >= 3:
            rounders[name]["al_yes_median_duration_sec"] = round(float(al_sub["duration_sec"].median()), 1) if al_sub["duration_sec"].notna().any() else None
            rounders[name]["al_yes_free_text_pct"] = free_text_stats(al_sub).get("pct_rounds_with_any_free_text")
        if len(no_sub) >= 3:
            rounders[name]["al_no_median_duration_sec"] = round(float(no_sub["duration_sec"].median()), 1) if no_sub["duration_sec"].notna().any() else None
            rounders[name]["al_no_free_text_pct"] = free_text_stats(no_sub).get("pct_rounds_with_any_free_text")

    results["per_rounder"] = rounders

    # Print summary
    print(json.dumps(results, indent=2))

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {OUT_PATH}")


if __name__ == "__main__":
    main()
