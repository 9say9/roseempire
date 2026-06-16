"""Print / export phone call follow-up list after email outreach."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_CSV = ROOT / "linkedin-outreach" / "outreach_master.csv"
CALL_QUEUE = ROOT / "linkedin-outreach" / "call_queue.csv"

CALL_COLUMNS = ("name", "company", "phone", "email", "facility_type", "email_status", "call_status", "website", "notes")


def build_call_queue(csv_path: Path = DEFAULT_CSV, *, include_no_email: bool = True) -> list[dict[str, str]]:
    if not csv_path.is_file():
        return []
    queue: list[dict[str, str]] = []
    with csv_path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            phone = (row.get("phone") or "").strip()
            if not phone:
                continue
            call_status = (row.get("call_status") or "").strip()
            if call_status not in ("", "pending", "callback"):
                continue
            email_status = (row.get("email_status") or "").strip()
            if not include_no_email and email_status == "no_email":
                continue
            queue.append({k: (row.get(k) or "").strip() for k in CALL_COLUMNS})
    queue.sort(key=lambda r: (r["email_status"] != "sent", r["name"].lower()))
    return queue


def save_call_queue(rows: list[dict[str, str]], path: Path = CALL_QUEUE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CALL_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Call follow-up queue from outreach_master.csv")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--export", action="store_true", help="Write call_queue.csv")
    parser.add_argument("--sent-only", action="store_true", help="Only leads where email was sent")
    args = parser.parse_args()

    rows = build_call_queue(args.csv, include_no_email=not args.sent_only)
    if not rows:
        print(f"No call targets in {args.csv}")
        print("Run: py -3 outreach_leads.py  (after Sarah + Adeel qualify)")
        return 1

    if args.export:
        save_call_queue(rows)
        print(f"Exported {len(rows)} leads to {CALL_QUEUE}")

    print(f"\nCall queue ({len(rows)} leads):\n")
    print("name | phone | email_status | facility_type")
    print("-" * 70)
    for r in rows[:50]:
        print(f"{r['name'][:35]:35} | {r['phone']:18} | {r['email_status']:10} | {r['facility_type']}")
    if len(rows) > 50:
        print(f"... and {len(rows) - 50} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
