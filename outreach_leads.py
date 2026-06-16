"""Clean outreach CSV — emails + phones for email first, call follow-up second."""
from __future__ import annotations

import csv
import re
from pathlib import Path

from email_utils import is_valid_business_email

ROOT = Path(__file__).resolve().parent
DEFAULT_QUALIFIED = ROOT / "linkedin-outreach" / "qualified_manchester_leads.csv"
DEFAULT_OUTREACH = ROOT / "linkedin-outreach" / "outreach_master.csv"

OUTREACH_COLUMNS = (
    "name",
    "company",
    "email",
    "phone",
    "website",
    "linkedin",
    "facility_type",
    "city",
    "source",
    "score",
    "email_status",
    "call_status",
    "last_email_date",
    "notes",
)

# Strip Google Maps / UI junk from phone strings
_PHONE_JUNK = re.compile(r"[\ue000-\uf8ff\u200b-\u200f\ufeff]")


def normalize_phone(raw: str) -> str:
    """Strip Maps UI junk; keep human-readable UK formatting."""
    if not raw:
        return ""
    s = _PHONE_JUNK.sub("", raw.strip())
    s = re.sub(r"\s+", " ", s)
    # Drop trailing extension junk from scrape artifacts
    s = re.split(r"\s*(?:ext|x\.)\s*", s, maxsplit=1, flags=re.I)[0].strip()
    return s


def _load_existing_status(path: Path) -> dict[str, dict[str, str]]:
    if not path.is_file():
        return {}
    out: dict[str, dict[str, str]] = {}
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            key = _row_key(row)
            if key:
                out[key] = {
                    "email_status": (row.get("email_status") or "pending").strip(),
                    "call_status": (row.get("call_status") or "pending").strip(),
                    "last_email_date": (row.get("last_email_date") or "").strip(),
                    "notes": (row.get("notes") or "").strip(),
                }
    return out


def _row_key(row: dict) -> str:
    base = (
        (row.get("website") or row.get("linkedin") or row.get("email") or row.get("name") or "")
        .lower()
        .strip()
    )
    return re.sub(r"[^a-z0-9]+", "", base)


def _initial_email_status(email: str) -> str:
    return "pending" if is_valid_business_email(email) else "no_email"


def _initial_call_status(phone: str) -> str:
    return "pending" if phone else "no_phone"


def export_outreach_csv(
    qualified_path: Path = DEFAULT_QUALIFIED,
    out_path: Path = DEFAULT_OUTREACH,
) -> dict[str, int]:
    if not qualified_path.is_file():
        raise FileNotFoundError(f"Qualified leads not found: {qualified_path}")

    existing = _load_existing_status(out_path)
    rows: list[dict[str, str]] = []

    with qualified_path.open(encoding="utf-8", newline="") as fh:
        for src in csv.DictReader(fh):
            email = (src.get("email") or "").strip()
            if email and not is_valid_business_email(email):
                email = ""
            phone = normalize_phone((src.get("phone") or "").strip())
            row = {
                "name": (src.get("name") or "").strip(),
                "company": (src.get("company") or src.get("name") or "").strip(),
                "email": email,
                "phone": phone,
                "website": (src.get("website") or "").strip(),
                "linkedin": (src.get("linkedin") or "").strip(),
                "facility_type": (src.get("facility_type") or "").strip(),
                "city": (src.get("city") or "Manchester").strip(),
                "source": (src.get("source") or "").strip(),
                "score": str(src.get("score") or ""),
                "email_status": "",
                "call_status": "",
                "last_email_date": "",
                "notes": (src.get("notes") or "").strip(),
            }
            prev = existing.get(_row_key(row), {})
            row["email_status"] = prev.get("email_status") or _initial_email_status(email)
            row["call_status"] = prev.get("call_status") or _initial_call_status(phone)
            row["last_email_date"] = prev.get("last_email_date") or ""
            if prev.get("notes") and not row["notes"]:
                row["notes"] = prev["notes"]
            rows.append(row)

    rows.sort(key=lambda r: (-int(r["score"] or 0), r["name"].lower()))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTREACH_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    stats = {
        "total": len(rows),
        "with_email": sum(1 for r in rows if is_valid_business_email(r["email"])),
        "with_phone": sum(1 for r in rows if r["phone"]),
        "email_pending": sum(1 for r in rows if r["email_status"] == "pending"),
        "call_pending": sum(1 for r in rows if r["call_status"] == "pending" and r["phone"]),
    }
    return stats


def update_outreach_row(
    out_path: Path,
    *,
    lead_key: str | None = None,
    email: str | None = None,
    email_status: str | None = None,
    call_status: str | None = None,
    last_email_date: str | None = None,
    notes: str | None = None,
) -> bool:
    if not out_path.is_file():
        return False
    with out_path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    updated = False
    for row in rows:
        match = False
        if lead_key and _row_key(row) == lead_key:
            match = True
        elif email and (row.get("email") or "").strip().lower() == email.strip().lower():
            match = True
        if not match:
            continue
        if email_status is not None:
            row["email_status"] = email_status
        if call_status is not None:
            row["call_status"] = call_status
        if last_email_date is not None:
            row["last_email_date"] = last_email_date
        if notes is not None:
            row["notes"] = notes
        updated = True
        break
    if not updated:
        return False
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTREACH_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return True


def _cli() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Export clean outreach CSV for email + call follow-up")
    parser.add_argument("--qualified", type=Path, default=DEFAULT_QUALIFIED)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTREACH)
    args = parser.parse_args()
    try:
        stats = export_outreach_csv(args.qualified, args.out)
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        print("Run: py -3 lead_pipeline.py --qualify")
        return 1
    print(f"Outreach CSV: {args.out}")
    print(f"  Total leads:     {stats['total']}")
    print(f"  With email:      {stats['with_email']}")
    print(f"  With phone:      {stats['with_phone']}")
    print(f"  Email pending:   {stats['email_pending']}")
    print(f"  Call pending:    {stats['call_pending']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
