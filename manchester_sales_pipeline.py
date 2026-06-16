"""Rose Empire — Manchester B2B sales pipeline: scrape sources -> qualify -> email -> landing page (Sarah)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from lead_pipeline import (
    LANDING_URL,
    Lead,
    append_send_log,
    load_send_log,
    merge_and_qualify,
    save_leads,
)
from email_utils import is_valid_business_email
from fleet_ai import ai_available, draft_email_pitch_with_ai, parse_email_pitch
from send_leads_emails import find_emails_on_website

ROOT = Path(__file__).resolve().parent
QUALIFIED_CSV = ROOT / "linkedin-outreach" / "qualified_manchester_leads.csv"
SEND_LOG = ROOT / "linkedin-outreach" / "email_send_log.csv"


def enrich_emails(leads: list[Lead], limit: int = 20) -> None:
    done = 0
    for lead in leads:
        if done >= limit:
            break
        if lead.email or not lead.website:
            continue
        print(f"Finding email for {lead.name} ({lead.website})...")
        email = find_emails_on_website(lead.website)
        if email and is_valid_business_email(email):
            lead.email = email
            lead.score += 30
            print(f"  -> {email}")
        done += 1


def build_pitch(lead: Lead) -> tuple[str, str]:
    if ai_available():
        customer_data = (
            f"Business: {lead.name}; Company: {lead.company}; Facility: {lead.facility_type}; "
            f"Website: {lead.website}; City: {lead.city}; Query: {lead.query}"
        )
        try:
            return parse_email_pitch(draft_email_pitch_with_ai(customer_data))
        except Exception:
            pass
    subject = f"Wholesale mattress protectors & pillows for {lead.company or lead.name}"
    body = f"""Hello,

Rose Empire is a Manchester wholesale supplier of mattress protectors and goose/duck down pillows for {lead.facility_type.lower()} buyers.

We work with care homes, hotels, guest houses, and student accommodation across Greater Manchester with:
- MOQ 20 pieces per size (one trade box)
- Volume discounts from 50+ and 200+ pieces
- UK-wide delivery and fast quote turnaround

Browse products and build a quote online (Sarah, our wholesale assistant, can help with MOQ and trade pricing):
{LANDING_URL}

If useful, reply with your typical order volume and product sizes and we will confirm trade pricing within 24 hours.

Best regards,
Rose Empire Wholesale
info@roseempire.co.uk
+44 7999 988450
https://www.roseempire.co.uk
"""
    return subject, body


def run_pipeline(limit: int = 10, send: bool = False, enrich: bool = True) -> int:
    print("\n=== Rose Empire Manchester Sales Pipeline ===\n")
    leads = merge_and_qualify(manchester_only=True, min_score=35)
    print(f"Qualified leads after merge: {len(leads)}")
    if not leads:
        print("No leads found. Run LinkedIn/Google scrapers first (see linkedin-outreach/*.bat).")
        return 1

    if enrich:
        enrich_emails(leads, limit=min(limit * 2, 30))

    save_leads(leads, QUALIFIED_CSV)
    print(f"Saved qualified list: {QUALIFIED_CSV}")

    sent_keys = load_send_log(SEND_LOG)
    processed = 0
    for lead in leads:
        if processed >= limit:
            break
        if lead.key() in sent_keys:
            continue
        subject, body = build_pitch(lead)
        print(f"\n--- Lead: {lead.name} | {lead.facility_type} | score {lead.score} ---")
        print(f"Source: {lead.source} | Website: {lead.website or '-'} | LinkedIn: {lead.linkedin or '-'}")
        if lead.email:
            print(f"Email: {lead.email}")
            if send:
                from email_agent import send_email
                ok = send_email(lead.email, subject, body)
                status = "sent" if ok else "failed"
                append_send_log(SEND_LOG, lead, status, subject)
                print(f"Email status: {status}")
            else:
                print("[DRY RUN] Email not sent. Re-run with --send after reviewing.")
                append_send_log(SEND_LOG, lead, "drafted", subject)
        else:
            print("No email found — use LinkedIn outreach for this lead.")
            if lead.linkedin:
                print(f"LinkedIn: {lead.linkedin}")
            append_send_log(SEND_LOG, lead, "no_email", subject)
        processed += 1

    print(f"\nProcessed {processed} leads.")
    print(f"Landing page for all outreach: {LANDING_URL}")
    print("Website Sarah chat qualifies inbound replies on roseempire.co.uk.\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Manchester B2B sales pipeline")
    parser.add_argument("--limit", type=int, default=10, help="Max leads per run")
    parser.add_argument("--send", action="store_true", help="Actually send emails (default is dry-run)")
    parser.add_argument("--no-enrich", action="store_true", help="Skip website email discovery")
    args = parser.parse_args()
    return run_pipeline(limit=args.limit, send=args.send, enrich=not args.no_enrich)


if __name__ == "__main__":
    raise SystemExit(main())
