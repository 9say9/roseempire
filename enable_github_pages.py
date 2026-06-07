"""
Rose Empire — enable GitHub Pages (Playwright).

Opens GitHub in a saved browser profile, turns on Pages for 9say9/roseempire,
then waits until https://9say9.github.io/roseempire/ responds.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
PROFILE_DIR = ROOT / "github_browser_profile"
REPO = "9say9/roseempire"
PAGES_SETTINGS = f"https://github.com/{REPO}/settings/pages"
ACTIONS_URL = f"https://github.com/{REPO}/actions/workflows/github-pages.yml"
LIVE_URL = "https://9say9.github.io/roseempire/"


def ensure_playwright():
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError:
        print("\nInstall Playwright first:")
        print("  py -3 -m pip install playwright requests")
        print("  py -3 -m playwright install chromium")
        sys.exit(1)


def wait_for_live(timeout_sec: int = 600) -> bool:
    print(f"\nWaiting for {LIVE_URL} (up to {timeout_sec // 60} min)...")
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            r = requests.get(LIVE_URL, timeout=20, allow_redirects=True)
            if r.status_code == 200 and "Rose Empire" in r.text:
                print(f"Live: {LIVE_URL} (HTTP {r.status_code})")
                return True
            print(f"  HTTP {r.status_code} — retrying in 20s...")
        except requests.RequestException as err:
            print(f"  {err} — retrying in 20s...")
        time.sleep(20)
    return False


def configure_pages(page) -> None:
    page.goto(PAGES_SETTINGS, wait_until="domcontentloaded", timeout=120000)
    time.sleep(2)

    if "login" in page.url:
        print("\nLog in to GitHub in the browser window.")
        page.wait_for_url("**/github.com/**", timeout=300000)
        page.goto(PAGES_SETTINGS, wait_until="domcontentloaded", timeout=120000)
        time.sleep(2)

    body = page.inner_text("body")

    if "Your site is live at" in body or "gihub.io" in body.lower():
        print("GitHub Pages already appears enabled.")
        return

    # Prefer GitHub Actions source (matches .github/workflows/github-pages.yml).
    actions_tab = page.get_by_role("link", name="GitHub Actions")
    if actions_tab.count():
        actions_tab.first.click()
        time.sleep(1)

    for label in ("GitHub Actions", "Deploy from a branch"):
        option = page.get_by_text(label, exact=True)
        if option.count():
            option.first.click()
            time.sleep(1)
            break

    branch_combo = page.locator('select[id*="source"], select[name*="branch"], #pages-source-branch')
    if branch_combo.count():
        branch_combo.first.select_option("main")
        time.sleep(0.5)

    folder_combo = page.locator('select[id*="path"], select[name*="path"]')
    if folder_combo.count():
        try:
            folder_combo.first.select_option("/(root)")
        except Exception:
            try:
                folder_combo.first.select_option("/")
            except Exception:
                pass

    save = page.get_by_role("button", name="Save")
    if save.count() and save.first.is_enabled():
        save.first.click()
        time.sleep(2)
        print("Saved GitHub Pages settings.")

    if "Configure" in page.inner_text("body"):
        print(
            "\nIf you see a suggested workflow in the browser, click "
            "'Configure' only if our workflow is not listed under Actions."
        )


def trigger_workflow(page) -> None:
    page.goto(ACTIONS_URL, wait_until="domcontentloaded", timeout=120000)
    time.sleep(2)

    run_btn = page.get_by_role("button", name="Run workflow")
    if run_btn.count():
        run_btn.first.click()
        time.sleep(0.5)
        confirm = page.get_by_role("button", name="Run workflow")
        if confirm.count() > 1:
            confirm.last.click()
        print("Triggered GitHub Pages workflow.")
        time.sleep(3)


def main() -> int:
    ensure_playwright()
    from playwright.sync_api import sync_playwright

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 64)
    print("  ROSE EMPIRE — GitHub Pages setup")
    print("=" * 64)
    print(f"\nRepo:  https://github.com/{REPO}")
    print(f"Live:  {LIVE_URL}\n")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            args=["--start-maximized"],
            viewport=None,
            no_viewport=True,
        )
        page = context.pages[0] if context.pages else context.new_page()

        configure_pages(page)
        trigger_workflow(page)

        print("\nComplete any remaining clicks in the browser, then press Enter here...")
        try:
            input()
        except EOFError:
            page.wait_for_timeout(15000)

        context.close()

    if wait_for_live():
        print("\nDONE — Rose Empire is live on GitHub Pages.")
        return 0

    print(
        "\nSite not responding yet. Check:\n"
        f"  {PAGES_SETTINGS}\n"
        f"  {ACTIONS_URL}\n"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
