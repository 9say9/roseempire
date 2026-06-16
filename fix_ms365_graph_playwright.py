"""Microsoft 365 Graph login via Playwright (uses saved browser session)."""
from __future__ import annotations

import json
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
PROFILE_DIR = ROOT / "m365_browser_profile"
TOKEN_FILE = ROOT / "graph_token.json"
CLIENT_ID = "14d82eec-204b-4c2f-b7e5-296a70ad1237"
SCOPES = [
    "https://graph.microsoft.com/Mail.Send",
    "https://graph.microsoft.com/User.Read",
    "offline_access",
]
REDIRECT_URI = "http://localhost:8400"
PORT = 8400


def _tenant() -> str:
    import os
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    t = (os.getenv("MS_GRAPH_TENANT_ID") or "").strip()
    return t if t else "organizations"


def _authority() -> str:
    return f"https://login.microsoftonline.com/{_tenant()}"


def _save_tokens(data: dict) -> None:
    if "expires_in" in data:
        data["expires_at"] = time.time() + int(data["expires_in"]) - 60
    TOKEN_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Token saved: {TOKEN_FILE}")


def _exchange_code(code: str) -> dict | None:
    resp = requests.post(
        f"{_authority()}/oauth2/v2.0/token",
        data={
            "client_id": CLIENT_ID,
            "scope": " ".join(SCOPES),
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        },
        timeout=30,
    )
    if resp.status_code != 200:
        print(f"Token exchange failed ({resp.status_code}): {resp.text[:400]}")
        return None
    return resp.json()


def _auth_url() -> str:
    params = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "response_mode": "query",
        "prompt": "select_account",
    })
    return f"{_authority()}/oauth2/v2.0/authorize?{params}"


def ensure_playwright():
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError:
        print("Install: py -3 -m pip install playwright requests python-dotenv")
        print("         py -3 -m playwright install chromium")
        sys.exit(1)


def login_with_playwright() -> bool:
    ensure_playwright()
    from playwright.sync_api import sync_playwright

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    url = _auth_url()
    code_holder: dict[str, str | None] = {"code": None}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            code_holder["code"] = qs.get("code", [None])[0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<html><body><h2>Login OK. Close this tab.</h2></body></html>")

        def log_message(self, fmt, *args):
            pass

    server = HTTPServer(("127.0.0.1", PORT), Handler)
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()

    print(f"Opening Microsoft login (tenant: {_tenant()})...")
    print("Pick info@roseempire.co.uk and click Accept.")

    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=False,
                args=["--start-maximized"],
                viewport=None,
                no_viewport=True,
            )
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=120000)
            time.sleep(4)
            for label in ("Accept", "Yes", "Continue", "Accept permissions"):
                btn = page.get_by_role("button", name=label)
                if btn.count():
                    try:
                        btn.first.click(timeout=4000)
                        time.sleep(2)
                    except Exception:
                        pass
            print("Waiting for login (up to 3 min)...")
            deadline = time.time() + 180
            while time.time() < deadline:
                if code_holder["code"]:
                    code = code_holder["code"]
                    try:
                        context.close()
                    except Exception:
                        pass
                    data = _exchange_code(code)
                    if data and data.get("access_token"):
                        _save_tokens(data)
                        return True
                    return False
                if "code=" in page.url:
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(page.url).query)
                    code = parsed.get("code", [None])[0]
                    if code:
                        try:
                            context.close()
                        except Exception:
                            pass
                        data = _exchange_code(code)
                        if data and data.get("access_token"):
                            _save_tokens(data)
                            return True
                        return False
                time.sleep(1)
            try:
                context.close()
            except Exception:
                pass
    except Exception as exc:
        print(f"Playwright error: {exc}")

    if code_holder["code"]:
        data = _exchange_code(code_holder["code"])
        if data and data.get("access_token"):
            _save_tokens(data)
            return True
    print("Login timed out. Run run_fix_ms365_email.bat and click Accept in the browser.")
    return False

def test_send() -> bool:
    sys.path.insert(0, str(ROOT))
    from email_agent import send_email
    ok = send_email("info@roseempire.co.uk", "Rose Empire email test", "Graph mail working.")
    print("Test email:", "SENT" if ok else "FAILED")
    return ok


def main() -> int:
    print("\n=== Rose Empire M365 Playwright login ===\n")
    if not login_with_playwright():
        return 1
    test_send()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
