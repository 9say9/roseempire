"""Rose Empire — unified sales engine: scrape -> qualify -> enrich -> pitch -> send."""
from __future__ import annotations

import argparse
from pathlib import Path

from email_utils import is_valid_business_email
from fleet_ai import ai_available, draft_email_pitch_with_ai, parse_email_pitch
from lead_pipeline import LANDING_URL, Lead, append_send_log, load_send_log, merge_and_qualify, save_leads
from send_leads_emails import find_emails_on_website

ROOT = Path(__file__).resolve().parent
QUALIFIED_CSV = ROOT / "linkedin-outreach" / "qualified_manchester_leads.csv"
MAPS_CSV = ROOT / "linkedin-outreach" / "refined_google_maps_leads.csv"
SEND_LOG = ROOT / "linkedin-outreach" / "email_send_log.csv"

DEFAULT_MISSION = "care homes hotels guest houses Manchester UK"


def sanitize_lead_emails(leads: list[Lead]) -> int:
    fixed = 0
    for lead in leads:
        if lead.email and not is_valid_business_email(lead.email):
            lead.email = ""
            lead.score = max(0, lead.score - 30)
            fixed += 1
    return fixed


def scrape_fresh_leads(mission: str, limit: int = 15) -> int:
    import asyncio
    from directory_scraper import scrape_target_leads

    rows = asyncio.run(
        scrape_target_leads(
            query=mission,
            limit=limit,
            output=MAPS_CSV,
            headless=True,
            enrich_details=True,
        )
    )
    return len(rows)


def enrich_emails(leads: list[Lead], limit: int = 20) -> int:
    found = 0
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
            found += 1
            print(f"  -> {email}")
        done += 1
    return found


def build_pitch(lead: Lead) -> tuple[str, str]:
    if ai_available():
        customer_data = (
            f"Business: {lead.name}; Company: {lead.company}; Facility: {lead.facility_type}; "
            f"Website: {lead.website}; City: {lead.city}; Query: {lead.query}"
        )
        try:
            raw = draft_email_pitch_with_ai(customer_data)
            return parse_email_pitch(raw)
        except Exception as exc:
            print(f"James AI fallback ({exc}) — using template pitch.")
    subject = f"Wholesale mattress protectors for {lead.company or lead.name}"
    body = f"""Hello,

Rose Empire supplies wholesale mattress protectors and pillows to {lead.facility_type.lower()} buyers across Greater Manchester.

- MOQ 20 pieces per size (one trade box)
- Volume discounts from 50+ and 200+ pieces
- UK-wide delivery and fast quote turnaround

Browse products and build a quote online:
{LANDING_URL}

Reply with typical order volume and sizes and we will confirm trade pricing within 24 hours.

Best regards,
Rose Empire Wholesale
info@roseempire.co.uk
+44 7999 988450
"""
    return subject, body


def run_sales_cycle(
    mission: str = DEFAULT_MISSION,
    limit: int = 10,
    send: bool = False,
    scrape_first: bool = False,
    scrape_limit: int = 15,
) -> dict:
    stats = {
        "scraped": 0,
        "qualified": 0,
        "emails_sanitized": 0,
        "emails_found": 0,
        "processed": 0,
        "sent": 0,
        "drafted": 0,
        "skipped_no_email": 0,
        "failed": 0,
    }

    print("\n=== Rose Empire Sales Engine ===\n")
    print(f"Mission: {mission}")
    print(f"Mode: {'LIVE SEND' if send else 'DRY RUN'}\n")

    if scrape_first:
        print("[Sarah] Scraping Google Maps directory...")
        stats["scraped"] = scrape_fresh_leads(mission, limit=scrape_limit)
        print(f"[Sarah] Scraped {stats['scraped']} new rows -> {MAPS_CSV}\n")

    leads = merge_and_qualify(manchester_only=True, min_score=35)
    stats["emails_sanitized"] = sanitize_lead_emails(leads)
    stats["qualified"] = len(leads)
    print(f"[Adeel] Qualified leads: {stats['qualified']} (sanitized {stats['emails_sanitized']} junk emails)")

    if not leads:
        print("No qualified leads. Run with --scrape or add CSV data in linkedin-outreach/.")
        return stats

    stats["emails_found"] = enrich_emails(leads, limit=min(limit * 2, 30))
    save_leads(leads, QUALIFIED_CSV)
    print(f"[Adeel] Saved: {QUALIFIED_CSV}\n")

    sent_keys = load_send_log(SEND_LOG)
    from email_agent import send_email

    for lead in leads:
        if stats["processed"] >= limit:
            break
        if lead.key() in sent_keys:
            continue

        subject, body = build_pitch(lead)
        stats["processed"] += 1
        print(f"\n--- {lead.name} | {lead.facility_type} | score {lead.score} ---")

        if not lead.email:
            stats["skipped_no_email"] += 1
            append_send_log(SEND_LOG, lead, "no_email", subject)
            if lead.linkedin:
                print(f"No email — LinkedIn: {lead.linkedin}")
            continue

        print(f"Email: {lead.email}")
        if send:
            ok = send_email(lead.email, subject, body)
            status = "sent" if ok else "failed"
            append_send_log(SEND_LOG, lead, status, subject)
            if ok:
                stats["sent"] += 1
            else:
                stats["failed"] += 1
            print(f"Status: {status}")
        else:
            stats["drafted"] += 1
            append_send_log(SEND_LOG, lead, "drafted", subject)
            print("[DRY RUN] Pitch ready — re-run with --send")

    print("\n=== Summary ===")
    for key, val in stats.items():
        print(f"  {key}: {val}")
    print(f"\nLanding page: {LANDING_URL}\n")
    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Rose Empire full sales cycle")
    parser.add_argument("--mission", default=DEFAULT_MISSION)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--scrape", action="store_true", help="Scrape Google Maps first")
    parser.add_argument("--scrape-limit", type=int, default=15)
    parser.add_argument("--send", action="store_true")
    args = parser.parse_args()
    stats = run_sales_cycle(
        mission=args.mission,
        limit=args.limit,
        send=args.send,
        scrape_first=args.scrape,
        scrape_limit=args.scrape_limit,
    )
    return 0 if stats["qualified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
