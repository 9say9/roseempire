"""
Rose Empire — Playwright stealth check for live chat on roseempire.co.uk
Run: py -3 verify_live_chat.py
"""
from __future__ import annotations

import json
import sys
import time

import requests

LIVE_URL = "https://roseempire.co.uk/"
CHAT_API = "https://roseempire.co.uk/api/chat"


def check_http() -> dict:
    out = {"site": {}, "api": {}}
    try:
        r = requests.get(LIVE_URL, timeout=20)
        out["site"]["status"] = r.status_code
        out["site"]["has_chat_widget"] = "chat-widget.js" in r.text
        out["site"]["server"] = r.headers.get("Server", "")
    except Exception as err:
        out["site"]["error"] = str(err)

    try:
        r = requests.post(
            CHAT_API,
            json={"message": "What is wholesale MOQ?", "context": "sarah"},
            timeout=45,
        )
        out["api"]["status"] = r.status_code
        body = r.json()
        out["api"]["reply_preview"] = (body.get("reply") or body.get("error") or "")[:120]
    except Exception as err:
        out["api"]["error"] = str(err)
    return out


def check_browser() -> dict:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"skipped": "Install playwright: py -3 -m pip install playwright && py -3 -m playwright install chromium"}

    result = {"steps": []}

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
        )
        page = context.new_page()
        page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
        )

        page.goto(LIVE_URL, wait_until="networkidle", timeout=60000)
        result["steps"].append(f"Loaded {LIVE_URL}")

        toggle = page.locator("#chat-toggle, .chat-widget-toggle")
        if toggle.count() == 0:
            result["error"] = "Chat widget toggle not found on live page."
            browser.close()
            return result

        toggle.first.click()
        page.wait_for_selector("#chat-input, .chat-widget-input", timeout=10000)
        page.locator("#chat-input, .chat-widget-input").first.fill("Hello Sarah, what is MOQ?")
        page.locator("#chat-send, .chat-widget-send").first.click()

        page.wait_for_selector(".chat-message--bot:not(.chat-message--loading)", timeout=60000)
        messages = page.locator(".chat-message--bot").all_text_contents()
        result["bot_reply"] = messages[-1][:200] if messages else ""
        result["steps"].append("Chat reply received in browser")
        browser.close()

    return result


def main() -> int:
    print("\n=== Rose Empire live chat verification ===\n")
    http = check_http()
    print("HTTP checks:")
    print(json.dumps(http, indent=2))

    print("\nPlaywright stealth browser check:")
    browser = check_browser()
    print(json.dumps(browser, indent=2))

    ok_site = http.get("site", {}).get("has_chat_widget")
    ok_api = http.get("api", {}).get("status") == 200
    ok_browser = "bot_reply" in browser and len(browser.get("bot_reply", "")) > 10

    if ok_site and ok_api and ok_browser:
        print("\nPASS — Live chat is working on roseempire.co.uk\n")
        return 0

    print("\nFAIL — Live chat not fully working yet.")
    if not ok_site:
        print("- Deploy latest site files (chat-widget.js) to Netlify.")
    if not ok_api:
        print("- Set GEMINI_API_KEY in Netlify → Site configuration → Environment variables, then redeploy.")
    print()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
