"""Shared email validation for lead scraping and outreach."""
from __future__ import annotations

import re

EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$")

JUNK_SUBSTRINGS = (
    ".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp", "@2x", "bootstrap@",
    "user@domain", "example.com", "wixpress", "sentry", "webpack", "cloudflare",
    "schema.org", "yourname@", "email@example", "name@example", "noreply",
    "no-reply", "donotreply", "@localhost", "test@test", "jquery", "w3.org",
    "fonts.googleapis", "fontawesome", "placeholder", "domain.com", "sentry.io",
    "scaled", "crop", "dining-room", "activities-games", "games@", "room-",
    "banner@", "logo@", "sprite@", "icon@", "asset@", "cdn@", "static@",
)


def is_valid_business_email(email: str) -> bool:
    if not email:
        return False
    email = email.strip().lower().rstrip(".")
    if not EMAIL_RE.match(email):
        return False
    if email.count("@") != 1:
        return False
    local, domain = email.rsplit("@", 1)
    if len(local) < 2 or "." not in domain:
        return False
    if any(junk in email for junk in JUNK_SUBSTRINGS):
        return False
    if re.search(r"\d{3,}x\d{3,}", local):
        return False
    return True


def pick_best_email(emails: set[str] | list[str]) -> str | None:
    candidates = [e.strip().lower().rstrip(".") for e in emails if is_valid_business_email(e)]
    if not candidates:
        return None
    preferred = [e for e in candidates if e.startswith(("info@", "enquir", "sales@", "contact@", "hello@"))]
    if preferred:
        return preferred[0]
    return candidates[0]
