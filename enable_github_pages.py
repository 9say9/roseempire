"""
Rose Empire — enable GitHub Pages (Playwright).

Turns on branch deploy (main / root) for 9say9/roseempire, then waits until
https://9say9.github.io/roseempire/ is live.
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


def wait_for_github_login(page) -> None:
    if "login" not in page.url:
        return
    print("\nLog in to GitHub in the browser window (complete 2FA if asked).")
    page.wait_for_function(
        "() => !window.location.href.includes('login')",
        timeout=300000,
    )
    time.sleep(2)


def pick_source_option(page, label: str) -> bool:
    for locator in (
        page.get_by_label("Source", exact=False),
        page.locator("#pages-source-select"),
        page.locator('select[name="source"]'),
    ):
        if locator.count():
            try:
                locator.first.select_option(label=label)
                time.sleep(1)
                return True
            except Exception:
                pass

    toggle = page.locator("summary").filter(has_text="Source")
    if toggle.count():
        toggle.first.click()
        time.sleep(0.5)

    item = page.get_by_role("menuitemradio", name=label)
    if item.count():
        item.first.click()
        time.sleep(1)
        return True

    text = page.get_by_text(label, exact=True)
    if text.count():
        text.first.click()
        time.sleep(1)
        return True
    return False


def pick_branch_and_folder(page) -> None:
    for locator in (
        page.get_by_label("Branch", exact=False),
        page.locator("#pages-source-branch"),
        page.locator('select[name="branch"]'),
    ):
        if locator.count():
            try:
                locator.first.select_option("main")
                break
            except Exception:
                pass

    for locator in (
        page.get_by_label("Folder", exact=False),
        page.locator("#pages-source-folder"),
        page.locator('select[name="path"]'),
    ):
        if locator.count():
            for value in ("/(root)", "/", "root"):
                try:
                    locator.first.select_option(value)
                    break
                except Exception:
                    continue
            break


def configure_pages(page) -> None:
    page.goto(PAGES_SETTINGS, wait_until="domcontentloaded", timeout=120000)
    time.sleep(2)
    wait_for_github_login(page)
    page.goto(PAGES_SETTINGS, wait_until="domcontentloaded", timeout=120000)
    time.sleep(2)

    body = page.inner_text("body")
    if "Your site is live at" in body:
        print("GitHub Pages already enabled.")
        return

    print("Configuring: Deploy from a branch → main → / (root)")
    if not pick_source_option(page, "Deploy from a branch"):
        print("Could not find Source dropdown — use the open browser window manually:")
        print(f"  1. Open {PAGES_SETTINGS}")
        print("  2. Source → Deploy from a branch")
        print("  3. Branch main, folder / (root), Save")
        return

    pick_branch_and_folder(page)

    save = page.get_by_role("button", name="Save")
    if save.count() and save.first.is_enabled():
        save.first.click()
        time.sleep(3)
        print("Saved GitHub Pages settings.")
    else:
        print("Save button not found — click Save manually in the browser if shown.")

    page.screenshot(path=str(ROOT / "github-pages-setup.png"), full_page=True)
    print(f"Screenshot saved: {ROOT / 'github-pages-setup.png'}")


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

        print("\nIf Pages is not saved yet, finish in the browser, then press Enter...")
        try:
            input()
        except EOFError:
            time.sleep(20)

        context.close()

    if wait_for_live():
        print("\nDONE — Rose Empire is live on GitHub Pages.")
        return 0

    print(
        "\nSite not live yet. Open Settings → Pages and confirm branch main / (root):\n"
        f"  {PAGES_SETTINGS}\n"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
