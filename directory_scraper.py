"""Async Playwright directory scraper with human-like behavior for Rose Empire leads."""
from __future__ import annotations

import argparse
import asyncio
import csv
import random
import re
from pathlib import Path
from urllib.parse import quote_plus

from playwright.async_api import BrowserContext, Page, async_playwright

ROOT = Path(__file__).resolve().parent
DEFAULT_OUT = ROOT / "linkedin-outreach" / "refined_google_maps_leads.csv"
PROFILE = ROOT / "linkedin-outreach" / "browser_profile"

from lead_validation import is_real_business_lead, is_valid_lead_name

STEALTH_INIT = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
"""

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


async def _try_dismiss_consent(page: Page) -> bool:
    """Click common Google consent buttons if present."""
    selectors = [
        'button:has-text("Accept all")',
        'button:has-text("Reject all")',
        'button:has-text("Accept")',
        'button:has-text("I agree")',
        '[aria-label="Accept all"]',
        '#L2AGLb',
        'form button[type="submit"]',
    ]
    for sel in selectors:
        try:
            btn = page.locator(sel).first
            if await btn.count() and await btn.is_visible():
                await btn.click(timeout=3000)
                await asyncio.sleep(2)
                return True
        except Exception:
            continue
    return False


async def _wait_for_maps_results(page: Page, timeout_sec: int = 25) -> bool:
    selectors = ['div[role="feed"]', 'a[href*="/maps/place/"]', ".Nv2PK", '[data-result-index]']
    for _ in range(timeout_sec):
        for sel in selectors:
            try:
                if await page.locator(sel).count() > 0:
                    return True
            except Exception:
                pass
        await asyncio.sleep(1)
    return False


async def human_like_behavior(page: Page, feed=None) -> None:
    scroll_amount = random.randint(300, 700)
    if feed is not None:
        await feed.evaluate(f"el => el.scrollBy(0, {scroll_amount})")
    else:
        await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
    await asyncio.sleep(random.uniform(0.5, 2.0))
    if random.choice([True, False]):
        if feed is not None:
            await feed.evaluate("el => el.scrollBy(0, -150)")
        else:
            await page.evaluate("window.scrollBy(0, -150)")
        await asyncio.sleep(random.uniform(0.3, 1.0))


async def _scroll_results_feed(page: Page, rounds: int = 8) -> None:
    feed = page.locator('div[role="feed"]')
    if not await feed.count():
        return
    for _ in range(rounds):
        await human_like_behavior(page, feed.first)
        await asyncio.sleep(random.uniform(0.8, 1.6))


async def _extract_place_details(page: Page) -> tuple[str, str]:
    phone = ""
    website = ""
    phone_btn = page.locator('button[data-item-id*="phone"], button[aria-label*="Phone"]')
    if await phone_btn.count():
        phone = re.sub(r"[\ue000-\uf8ff]", "", (await phone_btn.first.inner_text() or "")).strip()
    site_link = page.locator('a[data-item-id="authority"], a[aria-label*="Website"]')
    if await site_link.count():
        website = (await site_link.first.get_attribute("href") or "").strip()
    return phone, website


async def scrape_google_maps_directory(page: Page, query: str, limit: int = 20, enrich_details: bool = False, *, headed: bool = False) -> list[dict[str, str]]:
    search_url = f"https://www.google.com/maps/search/{quote_plus(query)}"
    print(f"Navigating to directory: {query}")
    await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
    await asyncio.sleep(random.uniform(3, 5))
    title = (await page.title()).lower()
    body_text = (await page.inner_text("body") if await page.locator("body").count() else "").lower()
    if "continue to google" in title or "consent" in body_text[:800] or "before you continue" in body_text[:800]:
        if await _try_dismiss_consent(page):
            await asyncio.sleep(2)
            await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(random.uniform(2, 4))
        elif headed:
            print(">>> Accept Google consent in the browser window (60 seconds)...")
            await asyncio.sleep(60)
            await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)
        else:
            print("Google consent screen — run: py -3 fleet_scraper.py --headed --sources google_maps")
            return []

    if not await _wait_for_maps_results(page):
        print("Maps results not loaded — try --headed or check internet.")
        return []

    await _scroll_results_feed(page)
    leads: list[dict[str, str]] = []
    seen: set[str] = set()

    nodes = await page.locator('a[href*="/maps/place/"]').all()
    if not nodes:
        nodes = await page.locator(".Nv2PK").all()

    for node in nodes:
        full_text = (await node.inner_text() or "").strip()
        if not full_text:
            aria = await node.get_attribute("aria-label")
            full_text = (aria or "").strip()
        if not full_text:
            continue
        name = full_text.split("\n")[0].strip()
        address = full_text.split("\n")[1].strip() if "\n" in full_text else ""
        key = name.lower()
        if not is_real_business_lead(name, address) or key in seen:
            continue
        phone = ""
        website = ""
        if enrich_details:
            try:
                await node.click(timeout=5000)
                await asyncio.sleep(random.uniform(1.2, 2.5))
                await human_like_behavior(page)
                phone, website = await _extract_place_details(page)
            except Exception:
                pass
        seen.add(key)
        leads.append({"name": name, "phone": phone, "website": website, "address": address, "query": query})
        print(f"  Lead #{len(leads)}: {name}")
        if len(leads) >= limit:
            break
    return leads


async def _launch_context(p, headless: bool) -> tuple[BrowserContext, object | None]:
    if PROFILE.is_dir():
        context = await p.chromium.launch_persistent_context(
            str(PROFILE), headless=headless, user_agent=USER_AGENT,
            viewport={"width": 1920, "height": 1080},
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
        )
        return context, None
    browser = await p.chromium.launch(headless=headless, args=["--disable-blink-features=AutomationControlled", "--start-maximized"])
    context = await browser.new_context(user_agent=USER_AGENT, viewport={"width": 1920, "height": 1080})
    return context, browser


def save_leads_csv(leads: list[dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["name", "phone", "website", "address", "query"]
    write_header = not output.is_file() or output.stat().st_size == 0
    with output.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(leads)


async def scrape_target_leads(query: str, limit: int = 20, output: Path = DEFAULT_OUT, headless: bool = False, enrich_details: bool = False) -> list[dict[str, str]]:
    """Scrape Google Maps. Retries with visible browser if headless hits consent."""
    attempts = [(headless, enrich_details)]
    if headless:
        attempts.append((False, enrich_details))

    leads: list[dict[str, str]] = []
    for attempt_headless, attempt_enrich in attempts:
        async with async_playwright() as p:
            context, browser = await _launch_context(p, headless=attempt_headless)
            page = context.pages[0] if context.pages else await context.new_page()
            await page.add_init_script(STEALTH_INIT)
            try:
                leads = await scrape_google_maps_directory(
                    page, query=query, limit=limit, enrich_details=attempt_enrich, headed=not attempt_headless
                )
                if leads:
                    save_leads_csv(leads, output)
                    print(f"Saved {len(leads)} leads to {output}")
                    return leads
                if not attempt_headless:
                    print("No leads extracted.")
            finally:
                await context.close()
                if browser is not None:
                    await browser.close()

        if not headless:
            break
        if attempt_headless:
            print("Retrying with visible browser for Google consent...")

    return leads


def main() -> int:
    parser = argparse.ArgumentParser(description="Scrape Google Maps directory leads for Rose Empire.")
    parser.add_argument("--query", default="care homes hotels guest houses Manchester UK")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--details", action="store_true")
    args = parser.parse_args()
    asyncio.run(scrape_target_leads(query=args.query, limit=args.limit, output=args.output, headless=args.headless, enrich_details=args.details))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
