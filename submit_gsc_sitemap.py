"""Submit sitemap in Google Search Console after DNS verification."""
from __future__ import annotations

import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROFILE = ROOT / "gsc_browser_profile"
SITE = "https://www.roseempire.co.uk/"
SITEMAP = "sitemap.xml"
VERIFY_TXT = "google-site-verification=TrV3N6fDujWtDZJxzNnoykShZ5D73mM4f6N53ub4xAc"


def main() -> None:
    from playwright.sync_api import sync_playwright

    PROFILE.mkdir(parents=True, exist_ok=True)
    resource = SITE.replace(":", "%3A").replace("/", "%2F")

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            str(PROFILE),
            headless=False,
            args=["--start-maximized"],
            viewport=None,
            no_viewport=True,
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        # Domain property verification page
        page.goto(
            "https://search.google.com/search-console/welcome?resource_id=sc-domain%3Aroseempire.co.uk",
            wait_until="domcontentloaded",
            timeout=120000,
        )
        time.sleep(3)

        if "accounts.google.com" in page.url:
            print("Sign in to Google in the browser, then wait...")
            page.wait_for_url(re.compile(r"search\.google\.com"), timeout=300000)

        verify = page.locator('button:has-text("Verify"), material-button:has-text("Verify")')
        if verify.count():
            verify.first.click()
            time.sleep(5)
            print("Clicked Verify for domain property.")

        # URL-prefix property fallback
        page.goto(
            f"https://search.google.com/search-console/welcome?resource_id={resource}",
            wait_until="domcontentloaded",
            timeout=120000,
        )
        time.sleep(2)
        if verify.count():
            verify.first.click()
            time.sleep(5)

        # Submit sitemap
        page.goto(
            f"https://search.google.com/search-console/sitemaps?resource_id={resource}",
            wait_until="domcontentloaded",
            timeout=120000,
        )
        time.sleep(2)

        for selector in [
            'input[aria-label*="sitemap"]',
            'input[placeholder*="sitemap"]',
            'input[type="url"]',
            'input[type="text"]',
        ]:
            field = page.locator(selector)
            if field.count():
                field.first.fill(SITEMAP)
                break

        submit = page.locator('button:has-text("Submit"), material-button:has-text("Submit")')
        if submit.count():
            submit.first.click()
            print(f"Submitted sitemap: {SITEMAP}")
        else:
            print(f"Submit manually in Sitemaps: {SITEMAP}")

        print(f"\nDNS TXT should be live: {VERIFY_TXT}")
        print("Close the browser when done.\n")
        while ctx.pages:
            time.sleep(1)
        ctx.close()


if __name__ == "__main__":
    main()
