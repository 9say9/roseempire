import base64
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent
TOKEN_CACHE = ROOT / ".ms_graph_token_cache.json"
GRAPH_TOKEN_FILE = ROOT / "graph_token.json"

DEFAULT_GRAPH_CLIENT_ID = "14d82eec-204b-4c2f-b7e5-296a70ad1237"


def _load_graph_token_file() -> str | None:
    if not GRAPH_TOKEN_FILE.exists():
        return None
    try:
        import json
        import time as _time
        data = json.loads(GRAPH_TOKEN_FILE.read_text(encoding="utf-8"))
        token = data.get("access_token")
        expires = data.get("expires_at")
        if token and expires and _time.time() > float(expires):
            refresh = data.get("refresh_token")
            if refresh:
                resp = requests.post(
                    f"{_graph_authority()}/oauth2/v2.0/token",
                    data={
                        "client_id": _graph_client_id(),
                        "grant_type": "refresh_token",
                        "refresh_token": refresh,
                        "scope": " ".join(GRAPH_SCOPES) + " offline_access",
                    },
                    timeout=30,
                )
                if resp.status_code == 200:
                    new_data = resp.json()
                    if "expires_in" in new_data:
                        new_data["expires_at"] = _time.time() + int(new_data["expires_in"]) - 60
                    new_data["refresh_token"] = new_data.get("refresh_token") or refresh
                    GRAPH_TOKEN_FILE.write_text(json.dumps(new_data, indent=2), encoding="utf-8")
                    return new_data.get("access_token")
            return None
        return token
    except Exception:
        return None

GRAPH_SCOPES = ["https://graph.microsoft.com/Mail.Send", "https://graph.microsoft.com/User.Read"]


def _sender_credentials():
    sender_email = os.getenv("INFO_EMAIL") or os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")
    if not sender_email or not sender_password:
        raise RuntimeError(
            "Email credentials missing. Set INFO_EMAIL (or EMAIL_ADDRESS) and EMAIL_PASSWORD in .env â€” never commit .env to GitHub."
        )
    return sender_email, sender_password


def _graph_client_id() -> str:
    return os.getenv("MS_GRAPH_CLIENT_ID") or DEFAULT_GRAPH_CLIENT_ID


def _graph_authority() -> str:
    tenant = os.getenv("MS_GRAPH_TENANT_ID") or "organizations"
    return f"https://login.microsoftonline.com/{tenant}"


def _load_msal_cache():
    import msal

    cache = msal.SerializableTokenCache()
    if TOKEN_CACHE.exists():
        cache.deserialize(TOKEN_CACHE.read_text(encoding="utf-8"))
    return cache


def _save_msal_cache(cache) -> None:
    if cache.has_state_changed:
        TOKEN_CACHE.write_text(cache.serialize(), encoding="utf-8")


def get_graph_access_token(*, interactive: bool = False) -> str | None:
    try:
        import msal
    except ImportError as exc:
        raise RuntimeError("Install msal: py -3 -m pip install msal") from exc

    cache = _load_msal_cache()
    app = msal.PublicClientApplication(
        _graph_client_id(),
        authority=_graph_authority(),
        token_cache=cache,
    )

    accounts = app.get_accounts()
    result = None
    if accounts:
        result = app.acquire_token_silent(GRAPH_SCOPES, account=accounts[0])

    if not result and interactive:
        print("Microsoft 365 device login — open the URL below in your browser.")
        print("Sign in as info@roseempire.co.uk if asked, then click Accept.")
        flow = app.initiate_device_flow(scopes=GRAPH_SCOPES)
        if "message" not in flow:
            raise RuntimeError(f"Device flow failed: {flow}")
        print(flow["message"])
        print("Waiting for approval in browser...")
        result = app.acquire_token_by_device_flow(flow)

    _save_msal_cache(cache)

    if result and "access_token" in result:
        return result["access_token"]
    if result and "error_description" in result:
        print(f"Graph auth error: {result['error_description']}")
    return None


def _attachment_payload(path: Path) -> dict:
    data = path.read_bytes()
    return {
        "@odata.type": "#microsoft.graph.fileAttachment",
        "name": path.name,
        "contentType": "application/pdf" if path.suffix.lower() == ".pdf" else "application/octet-stream",
        "contentBytes": base64.b64encode(data).decode("ascii"),
    }


def send_email_graph(recipient_email: str, subject: str, body: str, attachments: list[Path] | None = None) -> bool:
    token = _load_graph_token_file() or get_graph_access_token(interactive=False)
    if not token:
        print("Graph mail: no cached login. Run: py -3 scripts/ms365_graph_auth.py")
        return False

    message: dict = {
        "subject": subject,
        "body": {"contentType": "Text", "content": body},
        "toRecipients": [{"emailAddress": {"address": recipient_email}}],
    }
    if attachments:
        message["attachments"] = [_attachment_payload(p) for p in attachments if p.is_file()]

    payload = {"message": message, "saveToSentItems": True}
    try:
        response = requests.post(
            "https://graph.microsoft.com/v1.0/me/sendMail",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        if response.status_code == 202:
            return True
        if response.status_code == 401:
            TOKEN_CACHE.unlink(missing_ok=True)
            print("Graph mail: session expired. Run: py -3 scripts/ms365_graph_auth.py")
            return False
        print(f"Graph mail error ({response.status_code}): {response.text[:300]}")
        return False
    except Exception as exc:
        print(f"Graph mail error: {exc}")
        return False


def send_email_smtp(recipient_email: str, subject: str, body: str, attachments: list[Path] | None = None) -> bool:
    sender_email, sender_password = _sender_credentials()
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    for path in attachments or []:
        if not path.is_file():
            continue
        part = MIMEApplication(path.read_bytes(), _subtype=path.suffix.lstrip(".") or "octet-stream")
        part.add_header("Content-Disposition", "attachment", filename=path.name)
        message.attach(part)
    try:
        with smtplib.SMTP("smtp.office365.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        return True
    except Exception as exc:
        err = str(exc)
        if "SmtpClientAuthentication is disabled" in err:
            print("SMTP blocked by Microsoft 365 (tenant setting). Using Graph API instead.")
        else:
            print(f"SMTP error: {exc}")
        return False


def send_email(recipient_email: str, subject: str, body: str, attachments: list[Path] | None = None) -> bool:
    if GRAPH_TOKEN_FILE.exists() or TOKEN_CACHE.exists() or os.getenv("MS_GRAPH_FORCE") == "1":
        if send_email_graph(recipient_email, subject, body, attachments):
            return True
    if send_email_smtp(recipient_email, subject, body, attachments):
        return True
    if not TOKEN_CACHE.exists():
        print("Tip: run once â€” py -3 scripts/ms365_graph_auth.py â€” then retry --send")
    return False

