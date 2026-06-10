"""Sarah — lead scraping for AI Fleet dashboard."""
from __future__ import annotations

import csv
import re
from pathlib import Path
from urllib.parse import quote_plus

import requests

ROOT = Path(__file__).resolve().parent
CSV_SOURCES = [
    ROOT / "linkedin-outreach" / "google_maps_leads.csv",
    ROOT / "linkedin-outreach" / "manchester_textile_leads.csv",
    ROOT / "linkedin-outreach" / "refined_google_maps_leads.csv",
]
SEARCH_HEADERS = {
    "User-Agent": "RoseEmpireFleet/1.0 (info@roseempire.co.uk)",
    "Accept-Language": "en-GB,en;q=0.9",
}


def _is_valid_lead_name(name: str) -> bool:
    # Expanded list of bad keywords to filter out ads and non-business links
    bad = {
        "unknown", "?", "website", "visit site", "directions", "share",
        "sponsored", "ad", "advertisement", "learn more", "book now",
        "clearing halls", "uni halls", "student apartments"
    }
    cleaned = name.strip().lower()
    # Filter out entries that are purely promotional or contain common ad keywords
    if any(b in cleaned for b in bad):
        return False
    return len(cleaned) >= 4 and not cleaned.startswith("http")


def _keywords(mission: str) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9&]+", mission.lower())
    stop = {"find", "from", "google", "maps", "leads", "the", "and", "for", "in", "uk"}
    return [w for w in words if w not in stop and len(w) > 2]


def scrape_local_csv(mission: str, limit: int = 5) -> list[str]:
    keys = _keywords(mission)
    leads: list[str] = []
    seen: set[str] = set()

    for csv_path in CSV_SOURCES:
        if not csv_path.is_file():
            continue
        with csv_path.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                blob = " ".join(row.values()).lower()
                if keys and not any(k in blob for k in keys):
                    continue
                name = (
                    row.get("name")
                    or row.get("business_name")
                    or row.get("company")
                    or row.get("title")
                    or ""
                ).strip()
                if not name or not _is_valid_lead_name(name) or name.lower() in seen:
                    continue
                seen.add(name.lower())
                extra = row.get("address") or row.get("location") or row.get("city") or ""
                leads.append(f"Lead #{len(leads) + 1}: {name}" + (f" — {extra}" if extra else ""))
                if len(leads) >= limit:
                    return leads
    return leads


def scrape_openstreetmap(mission: str, limit: int = 5) -> list[str]:
    query = re.sub(r"\b(find|leads?|from|google|maps)\b", "", mission, flags=re.I).strip()
    if not query:
        query = "boutique hotels Manchester"
    if "uk" not in query.lower():
        query += " UK"
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": str(limit), "countrycodes": "gb"}
    response = requests.get(url, params=params, headers=SEARCH_HEADERS, timeout=15)
    response.raise_for_status()
    leads: list[str] = []
    for item in response.json():
        name = item.get("name") or item.get("display_name", "").split(",")[0]
        address = item.get("display_name", "")
        if name and _is_valid_lead_name(name):
            leads.append(f"Lead #{len(leads) + 1}: {name} — {address}")
        if len(leads) >= limit:
            break
    return leads


def scrape_google_maps_leads(mission: str, limit: int = 5) -> list[str]:
    """Try OpenStreetMap first, then local CSV archive, and finally Playwright Maps if needed."""
    leads = scrape_openstreetmap(mission, limit=limit)
    if len(leads) >= limit:
        return leads

    leads_csv = scrape_local_csv(mission, limit=limit - len(leads))
    leads.extend(leads_csv)
    if len(leads) >= limit:
        return leads[:limit]

    # Fallback to heavy-duty browser scraping if we still haven't hit the limit
    browser_leads = _scrape_google_maps_browser(mission, limit=limit - len(leads))
    leads.extend(browser_leads)
    
    return leads[:limit]


def scrape_duckduckgo(mission: str, limit: int = 5) -> list[str]:
    """Optional web index scrape (may be blocked by DuckDuckGo)."""
    from bs4 import BeautifulSoup

    query = quote_plus(mission)
    url = f"https://html.duckduckgo.com/html/?q={query}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    leads: list[str] = []
    links = soup.find_all("a", class_="result__url")
    snippets = soup.find_all("a", class_="result__snippet")
    for i in range(min(limit, len(links))):
        source = links[i].get_text(strip=True)
        desc = snippets[i].get_text(strip=True) if i < len(snippets) else "N/A"
        if _is_valid_lead_name(source):
            leads.append(f"Source: {source}\nDescription: {desc}")
    return leads


def scrape_all_leads(mission: str, limit: int = 5) -> list[str]:
    """Combine OSM, CSV, browser, and DuckDuckGo sources."""
    leads = scrape_google_maps_leads(mission, limit=limit)
    if len(leads) >= limit:
        return leads[:limit]
    try:
        extra = scrape_duckduckgo(mission, limit=limit - len(leads))
        leads.extend(extra)
    except Exception:
        pass
    return leads[:limit]


def _scrape_google_maps_browser(mission: str, limit: int = 5) -> list[str]:
    from playwright.sync_api import sync_playwright

    query = mission.strip()
    if not re.search(r"\b(uk|manchester|london|hotel|b&b|care home)\b", query, re.I):
        query = f"{query} UK hotels B&Bs"

    profile = ROOT / "linkedin-outreach" / "browser_profile"
    search_url = f"https://www.google.com/maps/search/{quote_plus(query)}"
    leads: list[str] = []
    seen: set[str] = set()

    with sync_playwright() as p:
        launch_kwargs = {"headless": True}
        if profile.is_dir():
            context = p.chromium.launch_persistent_context(str(profile), headless=True)
            page = context.pages[0] if context.pages else context.new_page()
        else:
            browser = p.chromium.launch(**launch_kwargs)
            page = browser.new_page()

        try:
            page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(6000)
            if "continue to Google" in page.title():
                return []

            # Improved scrolling logic to load more results
            feed = page.locator('div[role="feed"]')
            if feed.count():
                # Scroll more times and use a larger scroll distance for better depth
                for _ in range(8):
                    feed.first.evaluate("el => el.scrollBy(0, 2000)")
                    page.wait_for_timeout(1000)

            # Use a more specific selector to target the business name in Google Maps results
            # Usually the title of the link in the feed
            for node in page.locator('a[href*="/maps/place/"]').all():
                # Extract text and clean up
                full_text = (node.inner_text() or "").strip()
                if not full_text:
                    continue
                
                # The first line is usually the business name
                name = full_text.split("\n")[0].strip()
                
                if not _is_valid_lead_name(name) or name.lower() in seen:
                    continue
                
                seen.add(name.lower())
                leads.append(f"Lead #{len(leads) + 1}: {name}")
                if len(leads) >= limit:
                    break
        finally:
            if profile.is_dir():
                context.close()
            else:
                browser.close()

    return leads
