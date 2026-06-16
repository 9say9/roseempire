"""Rose Empire ? verify/fix GoDaddy DNS for GitHub Pages + TLS (Playwright)."""
from __future__ import annotations

import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
PROFILE_DIR = ROOT / "godaddy_browser_profile"
DOMAIN = "roseempire.co.uk"
DNS_URL = f"https://dcc.godaddy.com/control/portfolio/{DOMAIN}/settings?tab=dns"
LIVE_URL = "https://www.roseempire.co.uk/"
GITHUB_A = ["185.199.108.153", "185.199.109.153", "185.199.110.153", "185.199.111.153"]
WWW_CNAME = "9say9.github.io"
NETLIFY_A = "75.2.60.5"
NETLIFY_CNAME = "say9.netlify.app"


def ensure_playwright():
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError:
        print("Install: py -3 -m pip install playwright requests && py -3 -m playwright install chromium")
        sys.exit(1)


def check_live() -> tuple[bool, str]:
    try:
        r = requests.get(LIVE_URL, timeout=20, allow_redirects=True)
        body = r.text[:5000]
        ok = r.status_code == 200 and ("Rose Empire" in body or "roseempire" in body.lower())
        return ok, f"HTTP {r.status_code}"
    except requests.RequestException as err:
        return False, str(err)


def wait_login(page, timeout_sec: int = 150) -> None:
    for _ in range(timeout_sec // 2):
        if "godaddy.com" in page.url and "login" not in page.url.lower():
            return
        time.sleep(2)
    print("Complete GoDaddy login in the browser, then press Enter...")
    try:
        input()
    except EOFError:
        time.sleep(30)


def configure_dns(page) -> None:
    page.goto(DNS_URL, wait_until="domcontentloaded", timeout=120000)
    time.sleep(3)
    wait_login(page)
    page.goto(DNS_URL, wait_until="domcontentloaded", timeout=120000)
    time.sleep(4)
    body = page.inner_text("body")
    shot = ROOT / "godaddy-dns-before.png"
    page.screenshot(path=str(shot), full_page=True)
    print(f"Screenshot: {shot}")
    issues = []
    if NETLIFY_A in body or NETLIFY_CNAME in body:
        issues.append("Still points to Netlify ? update DNS to GitHub Pages")
    if not any(ip in body for ip in GITHUB_A):
        issues.append("Missing GitHub Pages A records")
    if WWW_CNAME not in body:
        issues.append(f"www CNAME should be {WWW_CNAME}")
    if "mail.protection.outlook.com" not in body:
        issues.append("WARNING: Microsoft 365 MX may be missing")
    if issues:
        print("\nDNS issues found:")
        for i in issues:
            print(f"  - {i}")
        print("\nRequired: 4x A @ GitHub IPs, CNAME www -> 9say9.github.io")
        print("Remove Netlify records. Keep MX + TXT for email.")
    else:
        print("DNS looks correct for GitHub Pages.")
    print("Edit records in the browser if needed, then press Enter...")
    try:
        input()
    except EOFError:
        time.sleep(20)
    page.screenshot(path=str(ROOT / "godaddy-dns-after.png"), full_page=True)


def main() -> int:
    ensure_playwright()
    from playwright.sync_api import sync_playwright
    live, detail = check_live()
    print(f"Live check {LIVE_URL}: {'OK' if live else 'NOT OK'} ({detail})")
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR), headless=False,
            args=["--start-maximized"], viewport=None, no_viewport=True,
        )
        page = context.pages[0] if context.pages else context.new_page()
        configure_dns(page)
        context.close()
    live2, detail2 = check_live()
    if live2:
        print(f"\nDONE ? {LIVE_URL} live ({detail2})")
        return 0
    print(f"\nRetest in 30-90 min: {LIVE_URL}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
