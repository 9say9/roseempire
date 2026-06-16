"""Rose Empire — merge, qualify, and dedupe Manchester B2B leads from multiple sources."""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

from email_utils import is_valid_business_email
from lead_validation import is_real_business_lead

ROOT = Path(__file__).resolve().parent
OUTREACH_DIRS = [
    ROOT / "linkedin-outreach",
    Path(r"d:/ai/antigravity/linkedin-outreach"),
]

MANCHESTER_RE = re.compile(
    r"\bmanchester\b|\bgreater manchester\b|\bcheetham\b|\bchorlton\b|\bdidsbury\b|\bsalford\b|\bstockport\b|\boldham\b|\bbury\b|\bbolton\b|\bwigan\b|\brochdale\b|\btrafford\b|\bwithington\b|\bfallowfield\b|\brusholme\b|\bgorton\b|\bmoston\b|\bhulme\b",
    re.I,
)

HIGH_VALUE_QUERIES = (
    "care home", "hotel", "guest house", "student", "accommodation", "nursing", "hospitality", "procurement", "facilities", "housekeeping",
)

LANDING_URL = "https://www.roseempire.co.uk/?utm_source=outreach&utm_medium=email&utm_campaign=manchester_b2b#catalog-section"


@dataclass
class Lead:
    name: str
    company: str = ""
    email: str = ""
    phone: str = ""
    website: str = ""
    linkedin: str = ""
    source: str = ""
    facility_type: str = ""
    query: str = ""
    score: int = 0
    city: str = "Manchester"
    notes: str = ""

    def key(self) -> str:
        base = (self.website or self.linkedin or self.email or self.name).lower().strip()
        return re.sub(r"[^a-z0-9]+", "", base)


def _outreach_file(name: str) -> Path | None:
    for d in OUTREACH_DIRS:
        p = d / name
        if p.is_file():
            return p
    return None


def _score_lead(lead: Lead) -> int:
    score = 0
    blob = " ".join([lead.name, lead.company, lead.query, lead.facility_type, lead.notes]).lower()
    if lead.website: score += 25
    if lead.email: score += 30
    if lead.linkedin: score += 15
    if lead.phone: score += 5
    if any(k in blob for k in HIGH_VALUE_QUERIES): score += 20
    if MANCHESTER_RE.search(blob): score += 15
    return score


def _facility_type(text: str) -> str:
    t = text.lower()
    if "care home" in t or "nursing" in t or "dementia" in t: return "Care Home"
    if "hotel" in t or "boutique" in t: return "Hotel"
    if "guest house" in t or "b&b" in t or "bnb" in t: return "Guest House"
    if "student" in t or "accommodation" in t: return "Student Accommodation"
    if "procurement" in t or "facilities" in t: return "Procurement / Facilities"
    return "Commercial Buyer"


def load_google_maps_leads() -> list[Lead]:
    path = _outreach_file("refined_google_maps_leads.csv")
    if not path: return []
    leads: list[Lead] = []
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            name = (row.get("name") or "").strip()
            query = (row.get("query") or "").strip()
            if not name or not is_real_business_lead(name, row.get("address") or "", row.get("website") or ""):
                continue
            email = (row.get("email") or "").strip()
            if email and not is_valid_business_email(email):
                email = ""
            lead = Lead(name=name, company=name, email=email, phone=(row.get("phone") or "").strip(), website=(row.get("website") or "").strip(), source="google_maps", query=query, facility_type=_facility_type(query + " " + name))
            lead.score = _score_lead(lead)
            leads.append(lead)
    return leads


def load_linkedin_leads() -> list[Lead]:
    path = _outreach_file("manchester_textile_leads.csv")
    if not path: return []
    leads: list[Lead] = []
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            name = (row.get("name") or "").strip()
            if not name: continue
            keyword = (row.get("search_keyword") or "").strip()
            company = (row.get("company_name") or "").strip()
            lead = Lead(name=name, company=company or name, linkedin=(row.get("profile_url") or "").strip(), source="linkedin", query=keyword, facility_type=_facility_type(keyword + " " + company), notes=(row.get("notes") or "").strip())
            lead.score = _score_lead(lead)
            leads.append(lead)
    return leads


def load_sarah_multi_leads() -> list[Lead]:
    path = _outreach_file("sarah_multi_source_leads.csv")
    if not path:
        return []
    leads: list[Lead] = []
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            name = (row.get("name") or "").strip()
            if not name or not is_real_business_lead(name, row.get("address") or "", row.get("website") or ""):
                continue
            source = (row.get("source") or "sarah").strip()
            query = (row.get("query") or "").strip()
            lead = Lead(
                name=name,
                company=name,
                phone=(row.get("phone") or "").strip(),
                website=(row.get("website") or "").strip(),
                linkedin=(row.get("linkedin") or row.get("profile_url") or "").strip(),
                source=source,
                query=query,
                facility_type=_facility_type(query + " " + name),
                notes=(row.get("notes") or "").strip(),
            )
            lead.score = _score_lead(lead)
            leads.append(lead)
    return leads


def load_uk_hotel_leads() -> list[Lead]:
    path = _outreach_file("uk_hotel_leads.csv")
    if not path:
        return []
    leads: list[Lead] = []
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            name = (row.get("name") or "").strip()
            if not name or not is_real_business_lead(name, row.get("address") or "", row.get("website") or ""):
                continue
            email = (row.get("email") or "").strip()
            if email and not is_valid_business_email(email):
                email = ""
            lead = Lead(
                name=name,
                company=(row.get("company") or name).strip(),
                email=email,
                phone=(row.get("phone") or "").strip(),
                website=(row.get("website") or "").strip(),
                source="uk_hotel",
                query=(row.get("query") or "").strip(),
                facility_type="Hotel",
                city=(row.get("city") or "").strip() or "UK",
                notes=(row.get("address") or "") + (" | " + row.get("notes") if row.get("notes") else ""),
            )
            lead.score = _score_lead(lead) + (15 if email else 0)
            leads.append(lead)
    return leads


def merge_and_qualify(manchester_only: bool = True, min_score: int = 35) -> list[Lead]:
    merged: dict[str, Lead] = {}
    for lead in load_uk_hotel_leads() + load_sarah_multi_leads() + load_google_maps_leads() + load_linkedin_leads():
        blob = " ".join([lead.name, lead.company, lead.query, lead.website, lead.linkedin])
        if (
            manchester_only
            and lead.source not in ("uk_hotel",)
            and lead.source == "google_maps"
            and "manchester" not in blob.lower()
            and not MANCHESTER_RE.search(blob)
        ):
            continue
        if lead.score < min_score and lead.source == "linkedin":
            continue
        existing = merged.get(lead.key())
        if not existing or lead.score > existing.score:
            merged[lead.key()] = lead
        else:
            for field in ("email", "phone", "website", "linkedin", "company", "query"):
                if not getattr(existing, field) and getattr(lead, field):
                    setattr(existing, field, getattr(lead, field))
            existing.score = _score_lead(existing)
    return sorted(merged.values(), key=lambda x: x.score, reverse=True)


def save_leads(leads: Iterable[Lead], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [asdict(l) for l in leads]
    if not rows:
        path.write_text("name,company,email,phone,website,linkedin,source,facility_type,query,score,city,notes\n", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def load_send_log(path: Path) -> set[str]:
    if not path.is_file(): return set()
    sent = set()
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            key = (row.get("lead_key") or row.get("email") or "").strip().lower()
            if key: sent.add(key)
    return sent


def append_send_log(path: Path, lead: Lead, status: str, subject: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not path.is_file()
    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["lead_key", "name", "email", "source", "status", "subject"])
        if new_file: writer.writeheader()
        writer.writerow({"lead_key": lead.key(), "name": lead.name, "email": lead.email, "source": lead.source, "status": status, "subject": subject})


def _cli() -> int:
    import argparse
    import sys

    from email_utils import is_valid_business_email

    parser = argparse.ArgumentParser(description="Adeel — qualify and merge Manchester B2B leads (free, no API)")
    parser.add_argument("--qualify", action="store_true", help="Merge CSVs, score, and save qualified leads")
    parser.add_argument("--enrich-emails", action="store_true", help="Scrape websites for missing emails (updates CSV)")
    parser.add_argument("--export-outreach", action="store_true", help="Build clean outreach_master.csv for email + calls")
    parser.add_argument("--min-score", type=int, default=35)
    parser.add_argument("--limit", type=int, default=10, help="Max rows to print")
    parser.add_argument("--manchester-only", action="store_true", default=True)
    args = parser.parse_args()

    out_path = ROOT / "linkedin-outreach" / "qualified_manchester_leads.csv"
    leads = merge_and_qualify(manchester_only=args.manchester_only, min_score=args.min_score)
    with_email = sum(1 for l in leads if l.email and is_valid_business_email(l.email))

    print(f"[Adeel] Qualified leads: {len(leads)} ({with_email} with valid email)")

    if args.qualify:
        save_leads(leads, out_path)
        print(f"[Adeel] Saved: {out_path}")

    if args.export_outreach:
        from outreach_leads import export_outreach_csv

        if not out_path.is_file():
            save_leads(leads, out_path)
        stats = export_outreach_csv(out_path)
        outreach_path = ROOT / "linkedin-outreach" / "outreach_master.csv"
        print(f"[Adeel] Outreach CSV: {outreach_path}")
        print(f"  {stats['with_email']} emails | {stats['with_phone']} phones | {stats['call_pending']} ready for calls")

    if args.enrich_emails:
        from send_leads_emails import enrich_csv_emails

        if not out_path.is_file():
            save_leads(leads, out_path)
        found = enrich_csv_emails(out_path, limit=50)
        with out_path.open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        with_email = sum(1 for r in rows if is_valid_business_email((r.get("email") or "").strip()))
        print(f"[Adeel] After enrich: {with_email}/{len(rows)} leads with valid email (+{found} new)")

        from outreach_leads import export_outreach_csv

        stats = export_outreach_csv(out_path)
        outreach_path = ROOT / "linkedin-outreach" / "outreach_master.csv"
        print(f"[Adeel] Outreach CSV: {outreach_path}")
        print(f"  {stats['with_email']} emails | {stats['with_phone']} phones | {stats['call_pending']} ready for calls")

    print("\nname,email,phone,website,facility_type,score")
    for lead in leads[: args.limit]:
        email = lead.email if lead.email and is_valid_business_email(lead.email) else ""
        print(f"{lead.name},{email},{lead.phone},{lead.website},{lead.facility_type},{lead.score}")

    if not leads:
        print("No leads yet. Run Sarah first: py -3 fleet_scraper.py --mission \"care homes Manchester UK\"", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
