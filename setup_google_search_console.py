"""
Rose Empire — Google Search Console setup (Playwright).

Opens Search Console in a saved browser profile, adds the property if needed,
installs the HTML verification tag on the site, redeploys to Netlify, verifies,
and submits the sitemap.
"""

from __future__ import annotations

import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROFILE_DIR = ROOT / "gsc_browser_profile"
INDEX_HTML = ROOT / "index.html"
SITE_URL = "https://www.roseempire.co.uk/"
SITEMAP_URL = "https://www.roseempire.co.uk/sitemap.xml"
GSC_HOME = "https://search.google.com/search-console"
GSC_SITEMAPS = (
    "https://search.google.com/search-console/sitemaps"
    f"?resource_id={SITE_URL.replace(':', '%3A').replace('/', '%2F')}"
)


def ensure_playwright():
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError:
        print("\nInstall Playwright first:")
        print("  py -3.12 -m pip install playwright")
        print("  py -3.12 -m playwright install chromium")
        sys.exit(1)


def netlify_deploy() -> bool:
    netlify = ROOT / "node_modules" / ".bin" / "netlify.cmd"
    if not netlify.exists():
        print("Netlify CLI missing. Run: npm install")
        return False
    print("\nDeploying verification tag to Netlify production...")
    result = subprocess.run(
        [str(netlify), "deploy", "--prod", "--dir", "."],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        return False
    print("Deploy complete.")
    return True


def upsert_verification_tag(content: str) -> bool:
    html = INDEX_HTML.read_text(encoding="utf-8")
    tag = f'<meta name="google-site-verification" content="{content}" />'
    pattern = r'<meta name="google-site-verification" content="[^"]*"\s*/?>'
    if re.search(pattern, html):
        html = re.sub(pattern, tag, html, count=1)
    else:
        html = html.replace(
            '<meta name="author" content="Rose Empire Wholesale Home Textiles">',
            '<meta name="author" content="Rose Empire Wholesale Home Textiles">\n    ' + tag,
        )
    INDEX_HTML.write_text(html, encoding="utf-8")
    print(f"Added google-site-verification tag to index.html")
    return True


def extract_meta_content(page) -> str | None:
    for selector in [
        'meta[name="google-site-verification"]',
        "code",
        "textarea",
    ]:
        loc = page.locator(selector)
        count = loc.count()
        for i in range(count):
            text = (loc.nth(i).get_attribute("content") or loc.nth(i).inner_text() or "").strip()
            match = re.search(r"google-site-verification[=:\s]+([A-Za-z0-9_\-]+)", text)
            if match:
                return match.group(1)
            if re.fullmatch(r"[A-Za-z0-9_\-]{20,}", text):
                return text
    body = page.inner_text("body")
    match = re.search(r"content=\"([A-Za-z0-9_\-]{20,})\"", body)
    if match:
        return match.group(1)
    return None


def wait_for_manual_step(page, message: str, timeout_ms: int = 300000) -> None:
    print(message)
    print("Complete the step in the browser window, then press Enter here...")
    try:
        input()
    except EOFError:
        page.wait_for_timeout(timeout_ms)


def main() -> None:
    ensure_playwright()
    from playwright.sync_api import sync_playwright

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 64)
    print("  ROSE EMPIRE — Google Search Console setup")
    print("=" * 64)
    print(f"\nSite:    {SITE_URL}")
    print(f"Sitemap: {SITEMAP_URL}\n")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            args=["--start-maximized"],
            viewport=None,
            no_viewport=True,
        )
        page = context.pages[0] if context.pages else context.new_page()

        page.goto(GSC_HOME, wait_until="domcontentloaded", timeout=120000)
        time.sleep(3)

        if "accounts.google.com" in page.url:
            print("Sign in to Google in the browser window if prompted.")
            page.wait_for_url(re.compile(r"search\.google\.com/search-console"), timeout=300000)

        # Try opening property directly
        page.goto(GSC_SITEMAPS, wait_until="domcontentloaded", timeout=120000)
        time.sleep(2)

        if "welcome" in page.url or page.locator("text=Add property").count():
            print("Property not found yet — add it in Search Console:")
            print(f"  URL prefix: {SITE_URL}")
            wait_for_manual_step(page, "After adding the property, continue.")
            page.goto(GSC_SITEMAPS, wait_until="domcontentloaded", timeout=120000)

        # Verification via HTML tag if needed
        verify_url = (
            "https://search.google.com/search-console/welcome"
            f"?resource_id={SITE_URL.replace(':', '%3A').replace('/', '%2F')}"
        )
        page.goto(verify_url, wait_until="domcontentloaded", timeout=120000)
        time.sleep(2)

        if page.locator("text=Verify ownership").count() or page.locator("text=HTML tag").count():
            html_tag = page.locator("text=HTML tag").first
            if html_tag.count():
                html_tag.click()
                time.sleep(1)

            content = extract_meta_content(page)
            if not content:
                wait_for_manual_step(
                    page,
                    "Open the HTML tag verification method and copy the content value if needed.",
                )
                content = extract_meta_content(page)

            if content and 'google-site-verification' not in INDEX_HTML.read_text(encoding="utf-8"):
                upsert_verification_tag(content)
                if not netlify_deploy():
                    print("Deploy failed — verify tag manually, then click Verify in Search Console.")
                else:
                    print("Waiting 20s for Netlify to publish...")
                    time.sleep(20)
                    page.reload(wait_until="domcontentloaded")
                    verify_btn = page.locator("text=Verify").first
                    if verify_btn.count():
                        verify_btn.click()
                        time.sleep(5)

        # Submit sitemap
        page.goto(GSC_SITEMAPS, wait_until="domcontentloaded", timeout=120000)
        time.sleep(2)

        sitemap_input = page.locator('input[placeholder*="sitemap"], input[aria-label*="sitemap"]')
        if sitemap_input.count():
            sitemap_input.first.fill("sitemap.xml")
            submit = page.locator('button:has-text("Submit"), button:has-text("SUBMIT")')
            if submit.count():
                submit.first.click()
                print(f"Submitted sitemap: {SITEMAP_URL}")
        else:
            print(f"\nOpen Sitemaps and submit manually: sitemap.xml")
            print(f"Direct URL: {GSC_SITEMAPS}")

        print("\nDone. Keep this browser profile for future Search Console visits.")
        print("Close the browser window when finished.\n")

        try:
            while context.pages:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            context.close()


if __name__ == "__main__":
    main()
