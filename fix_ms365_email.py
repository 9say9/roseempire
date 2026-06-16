"""Rose Empire ? fix Microsoft 365 email (Playwright + Graph API)."""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROFILE_DIR = ROOT / "m365_browser_profile"


def ensure_playwright():
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError:
        print("Install: py -3 -m pip install playwright msal && py -3 -m playwright install chromium")
        sys.exit(1)


def open_outlook_session(page) -> None:
    page.goto("https://outlook.office.com/mail/", wait_until="domcontentloaded", timeout=120000)
    time.sleep(4)
    body = page.inner_text("body")[:2000].lower()
    if "sign in" in body and "outlook" in body:
        print("Sign in as info@roseempire.co.uk in the browser window.")
    else:
        print("Outlook loaded ? if you see info@roseempire.co.uk mail, you are signed in.")
    page.screenshot(path=str(ROOT / "m365-outlook-check.png"), full_page=True)
    print(f"Screenshot: {ROOT / 'm365-outlook-check.png'}")


def graph_login() -> bool:
    sys.path.insert(0, str(ROOT))
    from email_agent import TOKEN_CACHE, get_graph_access_token

    print("\n=== Microsoft Graph login (browser consent) ===\n")
    token = get_graph_access_token(interactive=True)
    if not token:
        print("Graph login failed.")
        return False
    print(f"Success ? token saved: {TOKEN_CACHE}")
    return True


def test_send() -> bool:
    from email_agent import send_email

    print("\nSending test email to info@roseempire.co.uk ...")
    ok = send_email(
        "info@roseempire.co.uk",
        "Rose Empire ? email bots test",
        "Microsoft 365 Graph mail is working. Outreach bots can send now.",
    )
    print("Test email:", "SENT" if ok else "FAILED")
    return ok


def main() -> int:
    ensure_playwright()
    from playwright.sync_api import sync_playwright

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    print("\n=== Rose Empire ? Microsoft 365 email fix ===\n")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            args=["--start-maximized"],
            viewport=None,
            no_viewport=True,
        )
        page = context.pages[0] if context.pages else context.new_page()
        open_outlook_session(page)
        print("Waiting 15 seconds for Outlook to load, then continuing to Graph login...")
        time.sleep(15)
        context.close()

    if not graph_login():
        return 1
    test_send()
    print("\nDone. Run: py -3 manchester_sales_pipeline.py --limit 5 --send")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
