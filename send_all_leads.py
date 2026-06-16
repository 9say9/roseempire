"""Merge all lead CSVs and send outreach to every lead with a valid email."""
from __future__ import annotations

import csv
import re
from datetime import date
from pathlib import Path

from email_utils import is_valid_business_email
from outreach_leads import OUTREACH_COLUMNS, normalize_phone
from send_leads_emails import enrich_csv_emails, process_leads_and_send_emails

ROOT = Path(__file__).resolve().parent
OUTREACH = ROOT / "linkedin-outreach"
MERGED = OUTREACH / "all_leads_outreach.csv"

SOURCES = (
    OUTREACH / "outreach_master.csv",
    OUTREACH / "uk_hotel_leads.csv",
)


def _key(row: dict) -> str:
    base = (row.get("website") or row.get("email") or row.get("name") or "").lower().strip()
    return re.sub(r"[^a-z0-9]+", "", base)


def merge_all_leads() -> Path:
    merged: dict[str, dict] = {}
    for path in SOURCES:
        if not path.is_file():
            continue
        with path.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                name = (row.get("name") or "").strip()
                if not name:
                    continue
                email = (row.get("email") or "").strip()
                if email and not is_valid_business_email(email):
                    email = ""
                out = {
                    "name": name,
                    "company": (row.get("company") or name).strip(),
                    "email": email,
                    "phone": normalize_phone((row.get("phone") or "").strip()),
                    "website": (row.get("website") or "").strip(),
                    "linkedin": (row.get("linkedin") or "").strip(),
                    "facility_type": (row.get("facility_type") or "Commercial Buyer").strip(),
                    "city": (row.get("city") or "").strip(),
                    "source": (row.get("source") or path.stem).strip(),
                    "score": str(row.get("score") or ""),
                    "email_status": (row.get("email_status") or ("pending" if email else "no_email")).strip(),
                    "call_status": (row.get("call_status") or "pending").strip(),
                    "last_email_date": (row.get("last_email_date") or "").strip(),
                    "notes": (row.get("address") or row.get("notes") or "").strip()[:300],
                }
                k = _key(out)
                if not k:
                    continue
                prev = merged.get(k)
                if not prev:
                    merged[k] = out
                    continue
                for fld in OUTREACH_COLUMNS:
                    if not prev.get(fld) and out.get(fld):
                        prev[fld] = out[fld]
                if prev.get("email_status") != "sent" and out.get("email_status") == "sent":
                    prev["email_status"] = "sent"
                    prev["last_email_date"] = out.get("last_email_date") or prev.get("last_email_date")

    rows = sorted(merged.values(), key=lambda r: (r.get("email_status") == "sent", r.get("name", "").lower()))
    OUTREACH.mkdir(parents=True, exist_ok=True)
    with MERGED.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTREACH_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    with_email = sum(1 for r in rows if is_valid_business_email(r.get("email", "")))
    pending = sum(1 for r in rows if r.get("email_status") != "sent" and is_valid_business_email(r.get("email", "")))
    print(f"Merged {len(rows)} leads -> {MERGED}")
    print(f"  Valid emails: {with_email} | Ready to send: {pending}")
    return MERGED


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Merge and email all Rose Empire leads")
    parser.add_argument("--merge-only", action="store_true")
    parser.add_argument("--enrich-only", action="store_true")
    parser.add_argument("--send", action="store_true")
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()

    path = merge_all_leads()
    if args.merge_only:
        return 0

    if args.enrich_only or args.send:
        enrich_csv_emails(path, limit=args.limit)

    if args.send:
        process_leads_and_send_emails(
            path,
            limit=args.limit,
            dry_run=False,
            attach_catalog=True,
            email_only=True,
            use_ai=False,
        )
    elif not args.enrich_only and not args.merge_only:
        print("Use --enrich-only, --send, or --merge-only")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
