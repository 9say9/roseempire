"""Sarah — UK-wide hotel lead scrape (Google Maps + email enrichment)."""
from __future__ import annotations

import argparse
import asyncio
import csv
import re
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path

from email_utils import is_valid_business_email
from hotel_leads import is_hotel_lead
from lead_validation import is_real_business_lead
from outreach_leads import normalize_phone
from send_leads_emails import find_emails_on_website

ROOT = Path(__file__).resolve().parent
OUTREACH = ROOT / "linkedin-outreach"
UK_HOTEL_CSV = OUTREACH / "uk_hotel_leads.csv"
MAPS_ARCHIVE = OUTREACH / "uk_hotel_google_maps.csv"

UK_CITIES = (
    "London",
    "Manchester",
    "Birmingham",
    "Edinburgh",
    "Glasgow",
    "Liverpool",
    "Bristol",
    "Leeds",
    "Newcastle upon Tyne",
    "Sheffield",
    "Cardiff",
    "Belfast",
    "Nottingham",
    "Leicester",
    "Brighton",
    "Oxford",
    "Cambridge",
    "York",
    "Bath",
    "Aberdeen",
    "Southampton",
    "Portsmouth",
    "Plymouth",
    "Norwich",
    "Coventry",
    "Reading",
    "Derby",
    "Swansea",
    "Bournemouth",
    "Blackpool",
)

CSV_FIELDS = (
    "name",
    "company",
    "email",
    "phone",
    "website",
    "address",
    "city",
    "region",
    "facility_type",
    "source",
    "query",
    "email_status",
    "notes",
)


@dataclass
class HotelLead:
    name: str
    company: str = ""
    email: str = ""
    phone: str = ""
    website: str = ""
    address: str = ""
    city: str = ""
    region: str = "United Kingdom"
    facility_type: str = "Hotel"
    source: str = "google_maps"
    query: str = ""
    email_status: str = "pending"
    notes: str = ""

    def key(self) -> str:
        base = (self.website or self.name or self.address).lower().strip()
        return re.sub(r"[^a-z0-9]+", "", base)


def _parse_city_from_row(city: str, address: str, query: str) -> str:
    if city:
        return city
    for c in UK_CITIES:
        if c.lower() in address.lower() or c.lower() in query.lower():
            return c
    m = re.search(r",\s*([A-Za-z\s]+)\s*,?\s*(?:UK|United Kingdom)?$", address)
    if m:
        return m.group(1).strip()
    return ""


def _load_existing(path: Path) -> dict[str, HotelLead]:
    if not path.is_file():
        return {}
    out: dict[str, HotelLead] = {}
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            lead = HotelLead(
                name=(row.get("name") or "").strip(),
                company=(row.get("company") or row.get("name") or "").strip(),
                email=(row.get("email") or "").strip(),
                phone=normalize_phone((row.get("phone") or "").strip()),
                website=(row.get("website") or "").strip(),
                address=(row.get("address") or "").strip(),
                city=(row.get("city") or "").strip(),
                region=(row.get("region") or "United Kingdom").strip(),
                facility_type=(row.get("facility_type") or "Hotel").strip(),
                source=(row.get("source") or "google_maps").strip(),
                query=(row.get("query") or "").strip(),
                email_status=(row.get("email_status") or "pending").strip(),
                notes=(row.get("notes") or "").strip(),
            )
            if lead.name and lead.key():
                out[lead.key()] = lead
    return out


def save_hotel_leads(leads: list[HotelLead], path: Path = UK_HOTEL_CSV) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [asdict(l) for l in leads]
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def merge_leads(existing: dict[str, HotelLead], new: list[HotelLead]) -> list[HotelLead]:
    for lead in new:
        key = lead.key()
        if not key:
            continue
        prev = existing.get(key)
        if not prev:
            existing[key] = lead
            continue
        for fld in CSV_FIELDS:
            if not getattr(prev, fld, "") and getattr(lead, fld, ""):
                setattr(prev, fld, getattr(lead, fld))
        if prev.email_status == "pending" and lead.email:
            prev.email = lead.email
    return sorted(existing.values(), key=lambda x: (x.city.lower(), x.name.lower()))


async def _scrape_city(city: str, per_city: int, *, headed: bool) -> list[HotelLead]:
    from directory_scraper import scrape_target_leads

    query = f"hotels {city} UK"
    print(f"\n[Maps] {query} (up to {per_city})")
    rows = await scrape_target_leads(
        query=query,
        limit=per_city,
        output=MAPS_ARCHIVE,
        headless=not headed,
        enrich_details=True,
    )
    leads: list[HotelLead] = []
    for row in rows:
        name = (row.get("name") or "").strip()
        address = (row.get("address") or "").strip()
        website = (row.get("website") or "").strip()
        if not is_real_business_lead(name, address, website):
            continue
        if not is_hotel_lead(name, query=query, address=address, website=website):
            continue
        leads.append(
            HotelLead(
                name=name,
                company=name,
                phone=normalize_phone((row.get("phone") or "").strip()),
                website=website,
                address=address,
                city=_parse_city_from_row(city, address, query),
                query=query,
                source="google_maps",
            )
        )
    print(f"  -> {len(leads)} hotel(s) kept")
    return leads


def enrich_hotel_emails(leads: list[HotelLead], *, limit: int = 999) -> int:
    found = 0
    for i, lead in enumerate(leads):
        if i >= limit:
            break
        if lead.email and is_valid_business_email(lead.email):
            lead.email_status = "pending"
            continue
        if not lead.website:
            if not lead.email:
                lead.email_status = "no_email"
            continue
        print(f"[Email] {lead.name} <- {lead.website}")
        email = find_emails_on_website(lead.website) or ""
        if email and is_valid_business_email(email):
            lead.email = email
            lead.email_status = "pending"
            found += 1
            print(f"  -> {email}")
        else:
            lead.email_status = "no_email"
        time.sleep(0.8)
    return found


def scrape_uk_hotels(
    *,
    cities: list[str] | None = None,
    per_city: int = 6,
    max_cities: int = 12,
    headed: bool = False,
    enrich_emails: bool = True,
) -> list[HotelLead]:
    city_list = (cities or list(UK_CITIES))[:max_cities]
    existing = _load_existing(UK_HOTEL_CSV)
    collected: list[HotelLead] = []

    async def _run() -> None:
        for city in city_list:
            batch = await _scrape_city(city, per_city, headed=headed)
            collected.extend(batch)
            await asyncio.sleep(2)

    asyncio.run(_run())

    merged = merge_leads(existing, collected)
    if enrich_emails:
        new_emails = enrich_hotel_emails(merged)
        print(f"\n[Adeel] Found {new_emails} new email(s) on hotel websites")

    save_hotel_leads(merged)
    with_email = sum(1 for l in merged if is_valid_business_email(l.email))
    with_phone = sum(1 for l in merged if l.phone)
    print(f"\nSaved {len(merged)} UK hotel leads -> {UK_HOTEL_CSV}")
    print(f"  With email: {with_email} | With phone: {with_phone}")
    return merged


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Scrape UK hotel leads (Sarah) with emails and phones")
    parser.add_argument("--per-city", type=int, default=6, help="Max hotels per city from Google Maps")
    parser.add_argument("--max-cities", type=int, default=12, help="Number of UK cities to scrape")
    parser.add_argument("--city", action="append", help="Scrape specific city (repeatable)")
    parser.add_argument("--headed", action="store_true", help="Visible browser (Google consent)")
    parser.add_argument("--no-enrich", action="store_true", help="Skip website email discovery")
    parser.add_argument("--enrich-only", action="store_true", help="Only enrich emails on existing CSV")
    args = parser.parse_args()

    if args.enrich_only:
        leads = list(_load_existing(UK_HOTEL_CSV).values())
        if not leads:
            print(f"No leads in {UK_HOTEL_CSV}. Run scrape first.", file=sys.stderr)
            return 1
        enrich_hotel_emails(leads)
        save_hotel_leads(leads)
        return 0

    scrape_uk_hotels(
        cities=args.city,
        per_city=args.per_city,
        max_cities=args.max_cities,
        headed=args.headed,
        enrich_emails=not args.no_enrich,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
