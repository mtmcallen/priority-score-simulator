"""Shared Prisma Health ambient listening metrics logic."""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path

DATE_START = datetime(2026, 5, 5)
DATE_END = datetime(2026, 7, 22, 23, 59, 59)
BAPTIST_CUTOFF = datetime(2026, 7, 1)
BAPTIST_FACILITY = "BAPTIST COLUMBIA HOSPITAL"
REPORT_META_KEY = "_report"
ROUNDER_COLUMN = "Interaction Created By"
UNIT_COLUMN = "Unit"

CARE_PROVIDER_OPTIONS = [
    "Prisma",
    "HHC",
    "UMass",
    "Johns Hopkins",
    "Evergreen",
    "Kaiser",
    "University of Michigan",
    "Lee Health",
    "University of Oklahoma",
    "Intermountain",
    "Duke",
    "Norton",
    "St. Luke's",
    "Penn",
    "Baystate",
]

HOSPITALS = [
    ("GREENVILLE MEMORIAL HOSPITAL", "Greenville Memorial Hospital", "GMH "),
    ("PATEWOOD MEMORIAL HOSPITAL", "Patewood Memorial Hospital", "PWH "),
    ("BAPTIST COLUMBIA HOSPITAL", "Baptist Columbia Hospital", "BCH "),
]

DECLINED_CONSENT_COLUMNS = ("Declined Consent", "Declined to Record")


def norm(value: str) -> str:
    return (value or "").strip().lower()


def parse_date(value: str) -> datetime | None:
    value = (value or "").strip()
    if not value:
        return None
    for fmt in ("%m/%d/%Y %I:%M %p", "%m/%d/%Y %I:%M %p %Z"):
        try:
            cleaned = value.replace(" EDT", "").replace(" EST", "").strip()
            return datetime.strptime(cleaned[:22], fmt)
        except ValueError:
            continue
    try:
        return datetime.strptime(value[:19], "%m/%d/%Y %I:%M %p")
    except ValueError:
        return None


def resolve_declined_consent_column(fieldnames: list[str] | None) -> str:
    if not fieldnames:
        return DECLINED_CONSENT_COLUMNS[-1]
    normalized = {name.strip().lower(): name for name in fieldnames}
    for candidate in DECLINED_CONSENT_COLUMNS:
        if candidate.lower() in normalized:
            return normalized[candidate.lower()]
    raise ValueError(
        f"CSV must include one of {DECLINED_CONSENT_COLUMNS!r}; found columns: {', '.join(fieldnames or [])}"
    )


def classify_round_type(ambient: str, declined: str) -> str:
    if ambient == "yes" and declined == "no":
        return "al_used"
    if ambient == "no" and declined == "yes":
        return "patient_said_no"
    if ambient == "no" and declined == "no":
        return "manual_round"
    if ambient == "yes" and declined == "yes":
        return "declined_during_al"
    return "other"


def pct(count: int, total: int) -> float:
    return round(100 * count / total, 1) if total else 0.0


def format_date_label(dt: datetime) -> str:
    return f"{dt.strftime('%B')} {dt.day}, {dt.year}"


def format_date_range(start: datetime, end: datetime) -> str:
    if start.year == end.year:
        return f"{start.strftime('%B')} {start.day} – {end.strftime('%B')} {end.day}, {end.year}"
    return f"{format_date_label(start)} – {format_date_label(end)}"


def summarize_rows(rows: list[dict]) -> dict:
    total = len(rows)
    counts = {key: 0 for key in ("al_used", "patient_said_no", "manual_round", "declined_during_al")}
    for row in rows:
        outcome = classify_round_type(row["ambient"], row["declined"])
        if outcome in counts:
            counts[outcome] += 1

    unit_stats: dict[str, dict[str, int]] = defaultdict(
        lambda: {key: 0 for key in ("total", "al_used", "patient_said_no", "manual_round", "declined_during_al")}
    )
    for row in rows:
        unit = row["unit"]
        outcome = classify_round_type(row["ambient"], row["declined"])
        unit_stats[unit]["total"] += 1
        if outcome in unit_stats[unit]:
            unit_stats[unit][outcome] += 1

    al_attempted = counts["al_used"] + counts["declined_during_al"]
    declined_or_no = counts["patient_said_no"] + counts["declined_during_al"]

    units = []
    for unit, stats in sorted(unit_stats.items(), key=lambda item: (-item[1]["total"], item[0])):
        unit_declined_or_no = stats["patient_said_no"] + stats["declined_during_al"]
        units.append(
            {
                "unit": unit,
                "total": stats["total"],
                "al_used": stats["al_used"],
                "patient_said_no": stats["patient_said_no"],
                "manual_round": stats["manual_round"],
                "declined_during_al": stats["declined_during_al"],
                "declined_or_no": unit_declined_or_no,
                "al_used_pct": pct(stats["al_used"], stats["total"]),
                "patient_said_no_pct": pct(stats["patient_said_no"], stats["total"]),
                "manual_round_pct": pct(stats["manual_round"], stats["total"]),
                "declined_during_al_pct": pct(stats["declined_during_al"], stats["total"]),
                "declined_or_no_pct": pct(unit_declined_or_no, stats["total"]),
            }
        )

    return {
        "total_rounds": total,
        "al_used": counts["al_used"],
        "al_used_pct": pct(counts["al_used"], total),
        "patient_said_no": counts["patient_said_no"],
        "patient_said_no_pct": pct(counts["patient_said_no"], total),
        "manual_round": counts["manual_round"],
        "manual_round_pct": pct(counts["manual_round"], total),
        "declined_during_al": counts["declined_during_al"],
        "declined_during_al_pct": pct(counts["declined_during_al"], total),
        "declined_or_no": declined_or_no,
        "declined_or_no_pct": pct(declined_or_no, total),
        "al_attempted": al_attempted,
        "units": units,
    }


def hospital_metric_keys(metrics: dict) -> list[str]:
    return [key for key in metrics if key != REPORT_META_KEY]


def parse_csv_text(
    csv_text: str,
    date_start: datetime | None = None,
    date_end: datetime | None = None,
    rounder: str | None = None,
    unit: str | None = None,
) -> list[dict]:
    """Parse CSV text into normalized row dicts."""
    date_start = date_start or DATE_START
    date_end = date_end or DATE_END
    hospital_keys = {key for key, _, _ in HOSPITALS}
    rounder_filter = (rounder or "").strip() or None
    unit_filter = (unit or "").strip() or None
    rows: list[dict] = []

    reader = csv.DictReader(csv_text.splitlines())
    declined_col = resolve_declined_consent_column(reader.fieldnames)

    for row in reader:
        facility = (row.get("Unit Facility") or "").strip().upper()
        if facility not in hospital_keys:
            continue
        dt = parse_date(row.get("Interaction Time", ""))
        if dt is None or dt < date_start or dt > date_end:
            continue
        rounder_name = (row.get(ROUNDER_COLUMN) or "Unknown").strip()
        unit_name = (row.get(UNIT_COLUMN) or "Unknown").strip()
        if rounder_filter and rounder_name != rounder_filter:
            continue
        if unit_filter and unit_name != unit_filter:
            continue
        rows.append(
            {
                "facility": facility,
                "ambient": norm(row.get("Ambient Listening")),
                "declined": norm(row.get(declined_col)),
                "unit": unit_name,
                "rounder": rounder_name,
                "interaction_time": dt,
            }
        )

    return rows


def list_csv_filter_options(csv_text: str) -> dict[str, list[str]]:
    rows = parse_csv_text(csv_text)
    return {
        "rounders": sorted({row["rounder"] for row in rows}, key=str.casefold),
        "units": sorted({row["unit"] for row in rows}, key=str.casefold),
    }


def load_metrics_from_rows(
    rows: list[dict],
    care_provider: str | None = None,
    rounder: str | None = None,
    unit: str | None = None,
) -> dict:
    observed_dates = [row["interaction_time"] for row in rows]
    date_start = min(observed_dates) if observed_dates else DATE_START
    date_end = max(observed_dates) if observed_dates else DATE_END

    results: dict = {}
    for fac_key, fac_name, _ in HOSPITALS:
        hospital_rows = [row for row in rows if row["facility"] == fac_key]
        results[fac_name] = summarize_rows(hospital_rows)

    baptist_rows = [row for row in rows if row["facility"] == BAPTIST_FACILITY]
    baptist_before = [row for row in baptist_rows if row["interaction_time"] < BAPTIST_CUTOFF]
    baptist_after = [row for row in baptist_rows if row["interaction_time"] >= BAPTIST_CUTOFF]

    results[REPORT_META_KEY] = {
        "date_start": date_start.isoformat(),
        "date_end": date_end.isoformat(),
        "date_range_label": format_date_range(date_start, date_end),
        "care_provider": (care_provider or "").strip(),
        "rounder": (rounder or "").strip(),
        "unit": (unit or "").strip(),
        "row_count": len(rows),
        "baptist_before_after": {
            "before_label": "Before July 1",
            "after_label": "July 1 Onward",
            "before_period": format_date_range(date_start, datetime(2026, 6, 30, 23, 59, 59)),
            "after_period": format_date_range(BAPTIST_CUTOFF, date_end),
            "before": summarize_rows(baptist_before),
            "after": summarize_rows(baptist_after),
        },
    }
    return results


def load_metrics(
    csv_path: Path,
    care_provider: str | None = None,
    rounder: str | None = None,
    unit: str | None = None,
    date_start: datetime | None = None,
    date_end: datetime | None = None,
) -> dict:
    csv_text = csv_path.read_text(encoding="utf-8-sig")
    rows = parse_csv_text(csv_text, date_start=date_start, date_end=date_end, rounder=rounder, unit=unit)
    return load_metrics_from_rows(rows, care_provider=care_provider, rounder=rounder, unit=unit)


def load_metrics_from_csv_text(
    csv_text: str,
    care_provider: str | None = None,
    rounder: str | None = None,
    unit: str | None = None,
) -> dict:
    rows = parse_csv_text(csv_text, rounder=rounder, unit=unit)
    return load_metrics_from_rows(rows, care_provider=care_provider, rounder=rounder, unit=unit)
