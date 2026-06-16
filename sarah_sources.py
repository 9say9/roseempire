"""Sarah multi-source lead scraper — Google, LinkedIn, web, Reddit (+ Facebook/Instagram later)."""
from __future__ import annotations

import csv
import json
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from urllib.parse import quote_plus, urlparse

import requests

from lead_validation import is_real_business_lead

ROOT = Path(__file__).resolve().parent
OUTREACH = ROOT / "linkedin-outreach"
MULTI_CSV = OUTREACH / "sarah_multi_source_leads.csv"
ARCHIVE_CSVS = [
    OUTREACH / "google_maps_leads.csv",
    OUTREACH / "manchester_textile_leads.csv",
    OUTREACH / "refined_google_maps_leads.csv",
]

HEADERS = {
    "User-Agent": "RoseEmpireFleet/1.0 (info@roseempire.co.uk; B2B lead research)",
    "Accept-Language": "en-GB,en;q=0.9",
}

# Sources Sarah can use now vs planned
SOURCE_REGISTRY: dict[str, dict] = {
    "google_maps": {"label": "Google Maps", "enabled": True, "tier": "live"},
    "google_web": {"label": "Google / Web search", "enabled": True, "tier": "live"},
    "linkedin": {"label": "LinkedIn", "enabled": True, "tier": "live"},
    "reddit": {"label": "Reddit", "enabled": True, "tier": "live"},
    "facebook": {"label": "Facebook", "enabled": True, "tier": "beta"},
    "instagram": {"label": "Instagram", "enabled": True, "tier": "beta"},
}

CSV_FIELDS = [
    "name", "address", "phone", "website", "linkedin", "source", "profile_url", "query", "notes",
]


def _safe_text(text: str) -> str:
    return text.encode("ascii", errors="replace").decode("ascii")


@dataclass
class ScrapedLead:
    name: str
    address: str = ""
    phone: str = ""
    website: str = ""
    linkedin: str = ""
    source: str = ""
    profile_url: str = ""
    query: str = ""
    notes: str = ""

    def key(self) -> str:
        for val in (self.linkedin, self.website, self.profile_url, self.name):
            if val:
                return re.sub(r"[^a-z0-9]+", "", val.lower())
        return ""

    def to_line(self, index: int) -> str:
        parts = [f"Lead #{index}: {_safe_text(self.name)} [{self.source}]"]
        if self.address:
            parts.append(_safe_text(self.address))
        if self.website:
            parts.append(_safe_text(self.website))
        if self.linkedin or self.profile_url:
            parts.append(_safe_text(self.linkedin or self.profile_url))
        if self.phone:
            parts.append(_safe_text(self.phone))
        return " | ".join(parts)


def enabled_sources(requested: list[str] | None = None) -> list[str]:
    if not requested:
        return [k for k, v in SOURCE_REGISTRY.items() if v.get("enabled")]
    out = []
    for src in requested:
        key = src.strip().lower().replace(" ", "_")
        if key in SOURCE_REGISTRY and SOURCE_REGISTRY[key].get("enabled"):
            out.append(key)
    return out or enabled_sources(None)


def _clean_query(mission: str) -> str:
    q = re.sub(r"\b(find|leads?|from|scrape|get)\b", "", mission, flags=re.I).strip()
    if not q:
        q = "hotels UK"
    lower = q.lower()
    if "uk" in lower or "united kingdom" in lower or "hotel" in lower:
        return q
    if "manchester" not in lower:
        q += " Manchester UK"
    return q


def _keywords(mission: str) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9&]+", mission.lower())
    stop = {"find", "from", "google", "maps", "leads", "linkedin", "reddit", "the", "and", "for", "in", "uk"}
    return [w for w in words if w not in stop and len(w) > 2]


def _ddg_search(query: str, limit: int = 8) -> list[dict[str, str]]:
    """DuckDuckGo HTML search (no API key)."""
    from bs4 import BeautifulSoup

    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except Exception as exc:
        print(f"  Web search error: {exc}", file=sys.stderr)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    results: list[dict[str, str]] = []
    for a in soup.select("a.result__a")[: limit * 2]:
        title = a.get_text(" ", strip=True)
        href = a.get("href") or ""
        snippet_el = a.find_parent("div", class_="result")
        snippet = ""
        if snippet_el:
            sn = snippet_el.select_one(".result__snippet")
            snippet = sn.get_text(" ", strip=True) if sn else ""
        if title and href:
            results.append({"title": title, "url": href, "snippet": snippet})
        if len(results) >= limit:
            break
    time.sleep(1.2)
    return results


def _title_to_name(title: str) -> str:
    name = re.split(r"\s[-|–]\s", title)[0].strip()
    name = re.sub(r"\s+(LinkedIn|Facebook|Instagram|Reddit).*$", "", name, flags=re.I)
    return name[:80]


def scrape_google_maps(mission: str, limit: int, *, headed: bool = False) -> list[ScrapedLead]:
    import asyncio

    from directory_scraper import scrape_target_leads

    query = _clean_query(mission)
    print(f"  [google_maps] Live scrape: {query}")
    try:
        rows = asyncio.run(
            scrape_target_leads(
                query=query,
                limit=limit,
                headless=False,
                enrich_details=True,
            )
        )
    except Exception as exc:
        print(f"  [google_maps] Error: {exc}", file=sys.stderr)
        return []

    leads: list[ScrapedLead] = []
    for row in rows:
        name = (row.get("name") or "").strip()
        if not is_real_business_lead(name, row.get("address", ""), row.get("website", "")):
            continue
        leads.append(
            ScrapedLead(
                name=name,
                address=(row.get("address") or "").strip(),
                phone=(row.get("phone") or "").strip(),
                website=(row.get("website") or "").strip(),
                source="google_maps",
                query=query,
            )
        )
    return leads[:limit]


def scrape_google_web(mission: str, limit: int) -> list[ScrapedLead]:
    query = _clean_query(mission) + " hospitality business contact"
    print(f"  [google_web] Searching: {query}")
    results = _ddg_search(query, limit=limit)
    leads: list[ScrapedLead] = []
    for item in results:
        name = _title_to_name(item["title"])
        url = item["url"]
        if not is_real_business_lead(name, website=url):
            continue
        if "linkedin.com" in url or "facebook.com" in url or "instagram.com" in url:
            continue
        leads.append(
            ScrapedLead(
                name=name,
                website=url,
                source="google_web",
                profile_url=url,
                query=query,
                notes=item.get("snippet", "")[:200],
            )
        )
        if len(leads) >= limit:
            break
    return leads


def scrape_linkedin(mission: str, limit: int) -> list[ScrapedLead]:
    """Public LinkedIn company pages via web search + local CSV archive."""
    query = _clean_query(mission)
    leads: list[ScrapedLead] = []
    seen: set[str] = set()

    # Local LinkedIn CSV archive
    linkedin_csvs = [OUTREACH / "manchester_textile_leads.csv"]
    keys = _keywords(mission)
    for csv_path in linkedin_csvs:
        if not csv_path.is_file():
            continue
        with csv_path.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                name = (row.get("name") or row.get("company_name") or "").strip()
                linkedin = (row.get("profile_url") or row.get("linkedin") or "").strip()
                if not name or not is_real_business_lead(name, website=linkedin):
                    continue
                blob = " ".join(row.values()).lower()
                if keys and not any(k in blob for k in keys):
                    continue
                key = linkedin.lower() or name.lower()
                if key in seen:
                    continue
                seen.add(key)
                leads.append(
                    ScrapedLead(
                        name=name,
                        linkedin=linkedin,
                        source="linkedin",
                        profile_url=linkedin,
                        query=query,
                        notes=(row.get("notes") or row.get("search_keyword") or "")[:200],
                    )
                )
                if len(leads) >= limit:
                    return leads

    # Live: site search for public LinkedIn company pages (no login)
    search_q = f'site:linkedin.com/company "{query}"'
    print(f"  [linkedin] Public search: {search_q}")
    for item in _ddg_search(search_q, limit=limit * 2):
        url = item["url"]
        if "linkedin.com/company/" not in url.lower():
            continue
        name = _title_to_name(item["title"])
        if not is_real_business_lead(name, website=url):
            continue
        key = url.lower()
        if key in seen:
            continue
        seen.add(key)
        leads.append(
            ScrapedLead(
                name=name,
                linkedin=url,
                source="linkedin",
                profile_url=url,
                query=query,
                notes=item.get("snippet", "")[:200],
            )
        )
        if len(leads) >= limit:
            break
    return leads


def scrape_reddit(mission: str, limit: int) -> list[ScrapedLead]:
    """Public Reddit JSON search — finds posts mentioning businesses (research signals)."""
    query = _clean_query(mission)
    print(f"  [reddit] Searching posts: {query}")
    url = f"https://www.reddit.com/search.json?q={quote_plus(query)}&limit={min(limit * 3, 25)}&sort=relevance"
    headers = {**HEADERS, "User-Agent": "RoseEmpireFleet/1.0 by info@roseempire.co.uk"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        print(f"  [reddit] Error: {exc}", file=sys.stderr)
        return []

    leads: list[ScrapedLead] = []
    for child in data.get("data", {}).get("children", []):
        post = child.get("data", {})
        title = (post.get("title") or "").strip()
        subreddit = post.get("subreddit", "")
        permalink = post.get("permalink", "")
        if not title or len(title) < 8:
            continue
        name = _title_to_name(title)
        if not is_real_business_lead(name):
            continue
        profile = f"https://www.reddit.com{permalink}" if permalink else ""
        leads.append(
            ScrapedLead(
                name=name,
                source="reddit",
                profile_url=profile,
                query=query,
                notes=f"r/{subreddit}: {(post.get('selftext') or '')[:150]}",
            )
        )
        if len(leads) >= limit:
            break
    time.sleep(1.0)
    return leads


def _scrape_social_site(mission: str, limit: int, site: str, domain: str) -> list[ScrapedLead]:
    """Beta: public Facebook/Instagram business pages via web search."""
    query = _clean_query(mission)
    search_q = f"site:{domain} {query} UK business"
    print(f"  [{site}] Public search: {search_q}")
    leads: list[ScrapedLead] = []
    for item in _ddg_search(search_q, limit=limit * 2):
        url = item["url"]
        if domain not in urlparse(url).netloc:
            continue
        name = _title_to_name(item["title"])
        if not is_real_business_lead(name, website=url):
            continue
        leads.append(
            ScrapedLead(
                name=name,
                website=url,
                source=site,
                profile_url=url,
                query=query,
                notes=item.get("snippet", "")[:200],
            )
        )
        if len(leads) >= limit:
            break
    return leads


def scrape_facebook(mission: str, limit: int) -> list[ScrapedLead]:
    return _scrape_social_site(mission, limit, "facebook", "facebook.com")


def scrape_instagram(mission: str, limit: int) -> list[ScrapedLead]:
    return _scrape_social_site(mission, limit, "instagram", "instagram.com")


SOURCE_FUNCS = {
    "google_maps": scrape_google_maps,
    "google_web": scrape_google_web,
    "linkedin": scrape_linkedin,
    "reddit": scrape_reddit,
    "facebook": scrape_facebook,
    "instagram": scrape_instagram,
}


def save_leads_csv(leads: list[ScrapedLead], path: Path = MULTI_CSV) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for lead in leads:
            writer.writerow({k: getattr(lead, k, "") for k in CSV_FIELDS})


def merge_dedupe(all_leads: list[ScrapedLead]) -> list[ScrapedLead]:
    merged: dict[str, ScrapedLead] = {}
    for lead in all_leads:
        key = lead.key()
        if not key:
            continue
        if key not in merged:
            merged[key] = lead
        else:
            existing = merged[key]
            for fld in CSV_FIELDS:
                if not getattr(existing, fld, "") and getattr(lead, fld, ""):
                    setattr(existing, fld, getattr(lead, fld))
    return list(merged.values())


def scrape_multi_source(
    mission: str,
    limit: int = 10,
    *,
    sources: list[str] | None = None,
    headed: bool = False,
    per_source: int | None = None,
) -> list[ScrapedLead]:
    """Run Sarah across multiple internet sources."""
    active = enabled_sources(sources)
    if not active:
        print("No valid sources selected.", file=sys.stderr)
        return []

    budget = per_source or max(3, (limit + len(active) - 1) // len(active))
    print(f"Sarah multi-source scrape: {mission!r}")
    print(f"Sources: {', '.join(active)} (up to {budget} each, target {limit} total)")

    collected: list[ScrapedLead] = []
    for src in active:
        if len(collected) >= limit:
            break
        need = min(budget, limit - len(collected))
        fn = SOURCE_FUNCS.get(src)
        if not fn:
            continue
        try:
            if src == "google_maps":
                batch = fn(mission, need, headed=headed)
            else:
                batch = fn(mission, need)
            print(f"  [{src}] -> {len(batch)} lead(s)")
            collected.extend(batch)
        except Exception as exc:
            print(f"  [{src}] failed: {exc}", file=sys.stderr)

    final = merge_dedupe(collected)[:limit]
    if final:
        save_leads_csv(final)
        print(f"Saved {len(final)} leads -> {MULTI_CSV}")
    return final


def scrape_fresh_leads(
    mission: str,
    limit: int = 5,
    *,
    headed: bool = False,
    sources: list[str] | None = None,
) -> list[str]:
    """Dashboard/orchestrator entry — returns formatted lines."""
    leads = scrape_multi_source(mission, limit=limit, headed=headed, sources=sources)
    return [lead.to_line(i + 1) for i, lead in enumerate(leads)]


def list_sources() -> str:
    lines = ["Sarah lead sources:"]
    for key, meta in SOURCE_REGISTRY.items():
        flag = "ON" if meta.get("enabled") else "OFF"
        tier = meta.get("tier", "live")
        lines.append(f"  {key:14} {meta['label']:22} [{flag}] ({tier})")
    return "\n".join(lines)
