"""Discover emails on business websites and send outreach to qualified leads."""
from __future__ import annotations

import argparse
import csv
import re
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from email_agent import send_email
from email_utils import is_valid_business_email, pick_best_email
from fleet_ai import draft_email_pitch_with_ai, parse_email_pitch
from outreach_leads import DEFAULT_OUTREACH, OUTREACH_COLUMNS, update_outreach_row

ROOT = Path(__file__).resolve().parent
QUALIFIED_CSV = ROOT / "linkedin-outreach" / "qualified_manchester_leads.csv"
DEFAULT_CSV = DEFAULT_OUTREACH if DEFAULT_OUTREACH.is_file() else QUALIFIED_CSV
CATALOG_PDF = ROOT / "assets" / "Rose-Empire-Wholesale-Catalog.pdf"
LANDING_URL = "https://www.roseempire.co.uk/?utm_source=outreach&utm_medium=email&utm_campaign=manchester_b2b#catalog-section"
EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}")

CONTACT_PATHS = (
    "/contact",
    "/contact-us",
    "/contactus",
    "/enquiries",
    "/enquiry",
    "/get-in-touch",
    "/about/contact",
)


def find_emails_on_website(url: str) -> str | None:
    """Find a business email on homepage and common contact pages."""
    if not url:
        return None
    if not url.startswith("http"):
        url = "http://" + url

    emails: set[str] = set()
    headers = {"User-Agent": "Mozilla/5.0 (compatible; RoseEmpireFleet/1.0)"}

    def _collect(html: str, page_url: str) -> None:
        emails.update(EMAIL_RE.findall(html))
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if href.lower().startswith("mailto:"):
                addr = href.split(":", 1)[1].split("?")[0].strip()
                if is_valid_business_email(addr):
                    emails.add(addr.lower())

    try:
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()
        _collect(response.text, url)

        base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        for path in CONTACT_PATHS:
            try:
                contact_url = urljoin(base, path)
                res = requests.get(contact_url, timeout=12, headers=headers)
                if res.status_code == 200:
                    _collect(res.text, contact_url)
            except Exception:
                continue
    except Exception as exc:
        print(f"  Email scrape error ({url}): {exc}")
        return None

    valid = {e.lower().rstrip(".") for e in emails if is_valid_business_email(e)}
    return pick_best_email(valid)


def enrich_csv_emails(csv_path: Path, limit: int = 50) -> int:
    """Fill missing email column by scraping websites. Updates CSV in place."""
    if not csv_path.is_file():
        print(f"CSV not found: {csv_path}")
        return 0

    rows: list[dict[str, str]] = []
    found = 0
    with csv_path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        for i, row in enumerate(reader):
            if i >= limit:
                rows.append(row)
                continue
            email = (row.get("email") or "").strip()
            website = (row.get("website") or "").strip()
            name = row.get("name") or row.get("company") or "Lead"
            if not email and website:
                print(f"[Enrich] {name} <- {website}")
                discovered = find_emails_on_website(website)
                if discovered:
                    row["email"] = discovered
                    found += 1
                    print(f"  -> {discovered}")
            rows.append(row)

    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Enriched {found} email(s) in {csv_path}")
    return found


def _catalog_attachment_line() -> str:
    if CATALOG_PDF.is_file():
        return "I've attached our wholesale price catalog (PDF) — MOQ 20 per size, volume discounts available.\n"
    return "Browse our wholesale catalog and request a quote: " + LANDING_URL + "\n"


def _ensure_company_context(subject: str, body: str, company_name: str) -> tuple[str, str]:
    company = (company_name or "your team").strip() or "your team"
    subject = subject.strip()
    body = body.strip()
    if company.lower() not in subject.lower():
        subject = f"{subject} for {company}" if subject else f"Wholesale bedding for {company}"
    if company.lower() not in body.lower():
        body = f"Hello {company},\n\n{body}"
    if not body.lower().startswith("hello"):
        body = f"Hello {company},\n\n{body}"
    return subject, body


def _default_pitch(name: str, query: str, company: str | None = None) -> tuple[str, str]:
    company_name = (company or name or "your team").strip() or "your team"
    subject = f"Wholesale bedding for {company_name}"
    pitch = (
        f"Rose Empire supplies wholesale mattress protectors and pillows to UK {query} buyers.\n"
        f"We help hospitality and care businesses improve bedding quality while keeping procurement simple and cost-effective.\n"
        f"{_catalog_attachment_line()}"
        f"If useful, I can send a tailored quote for {company_name} and the relevant product range.\n\n"
        f"Best regards,\n"
        f"Rose Empire Wholesale\n"
        f"info@roseempire.co.uk | +44 7999 988450"
    )
    return _ensure_company_context(subject, pitch, company_name)


def _save_outreach_rows(csv_path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def process_leads_and_send_emails(
    csv_path: Path,
    limit: int = 20,
    *,
    dry_run: bool = False,
    attach_catalog: bool = True,
    email_only: bool = False,
    use_ai: bool = True,
) -> None:
    if not csv_path.is_file():
        print(f"Error: CSV not found at {csv_path}")
        return

    attachments: list[Path] = []
    if attach_catalog and CATALOG_PDF.is_file():
        attachments.append(CATALOG_PDF)
        print(f"Attaching catalog: {CATALOG_PDF.name}")
    elif attach_catalog:
        print("Tip: run py -3 generate_catalog_pdf.py to attach the price catalog PDF")

    sent = 0
    skipped = 0
    failed = 0

    with csv_path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or [])
        all_rows = list(reader)

    is_outreach = "email_status" in fieldnames
    rows_to_write = all_rows if is_outreach else None

    targets = []
    for row in all_rows:
        if (row.get("email_status") or "").strip() == "sent":
            continue
        email = (row.get("email") or "").strip()
        website = (row.get("website") or "").strip()
        if email_only and not email and not website:
            continue
        targets.append(row)

    print(f"Processing {min(limit, len(targets))} of {len(targets)} lead(s) with email or website...")

    for row in targets:
        if sent + failed >= limit:
            break

        name = row.get("name") or row.get("company") or "Business Owner"
        website = (row.get("website") or "").strip()
        query = row.get("query") or row.get("facility_type") or "hotel and hospitality"
        recipient_email = (row.get("email") or "").strip()

        if not recipient_email and website:
            print(f"Discovering email for {name}...")
            recipient_email = find_emails_on_website(website) or ""
            if recipient_email:
                print(f"  Found: {recipient_email}")
                row["email"] = recipient_email
                if is_outreach:
                    row["email_status"] = "pending"

        if not recipient_email or not is_valid_business_email(recipient_email):
            if email_only:
                continue
            skipped += 1
            if is_outreach:
                row["email_status"] = "no_email"
            continue

        facility = row.get("facility_type") or query
        company_name = (row.get("company") or row.get("name") or "your team").strip() or "your team"
        if use_ai:
            print(f"Drafting pitch for {company_name}...")
            customer_data = (
                f"Company: {company_name}, Contact: {name}, Website: {website}, Industry: {facility}"
            )
            try:
                raw_pitch = draft_email_pitch_with_ai(customer_data)
                subject, pitch = parse_email_pitch(raw_pitch)
                subject, pitch = _ensure_company_context(subject, pitch, company_name)
                if attachments and "attach" not in pitch.lower() and "catalog" not in pitch.lower():
                    pitch = pitch.rstrip() + "\n\n" + _catalog_attachment_line()
            except Exception as exc:
                print(f"  James AI unavailable ({exc}) — using template.")
                subject, pitch = _default_pitch(name, facility, company=company_name)
        else:
            subject, pitch = _default_pitch(name, facility, company=company_name)

        if dry_run:
            att = f" + {CATALOG_PDF.name}" if attachments else ""
            print(f"DRY-RUN would send to {recipient_email}: {subject}{att}")
            sent += 1
            continue

        success = send_email(
            recipient_email=recipient_email,
            subject=subject,
            body=pitch,
            attachments=attachments or None,
        )
        if success:
            print(f"SENT to {name} ({recipient_email})")
            sent += 1
            if is_outreach:
                row["email_status"] = "sent"
                row["last_email_date"] = date.today().isoformat()
        else:
            print(f"FAILED send to {name} ({recipient_email})")
            failed += 1

    if is_outreach and rows_to_write is not None:
        _save_outreach_rows(csv_path, rows_to_write, fieldnames or list(OUTREACH_COLUMNS))

    print(f"\nDone. Sent: {sent}, failed: {failed}, skipped (no email): {skipped}")
    if failed:
        print("Mail failed — run: py -3 scripts/ms365_graph_auth.py  then retry --send")
    elif sent and not dry_run:
        print("Next: py -3 call_followup.py --export  (phone follow-up list)")


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Enrich emails and send outreach to qualified leads")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Qualified leads CSV")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--enrich-only", action="store_true", help="Find emails from websites, update CSV")
    parser.add_argument("--dry-run", action="store_true", help="Draft pitches without sending")
    parser.add_argument("--send", action="store_true", help="Send emails (requires .env SMTP)")
    parser.add_argument("--no-attach", action="store_true", help="Do not attach wholesale catalog PDF")
    parser.add_argument("--email-only", action="store_true", help="Only leads that already have email or website")
    parser.add_argument("--no-ai", action="store_true", help="Use template pitch (faster, more reliable)")
    args = parser.parse_args()

    if args.enrich_only:
        enrich_csv_emails(args.csv, limit=args.limit)
        return 0

    if not args.send and not args.dry_run:
        print("Use --enrich-only, --dry-run, or --send")
        print(f"Default CSV: {args.csv}")
        return 1

    process_leads_and_send_emails(
        args.csv,
        limit=args.limit,
        dry_run=args.dry_run or not args.send,
        attach_catalog=not args.no_attach,
        email_only=args.email_only,
        use_ai=not args.no_ai,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
