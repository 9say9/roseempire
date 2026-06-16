"""Shared lead quality checks for Sarah / Adeel."""
from __future__ import annotations

import re

BAD_NAMES = {
    "unknown", "?", "website", "visit site", "directions", "share",
    "sponsored", "ad", "advertisement", "learn more", "book now",
    "results", "search", "google maps", "map data",
}

AGGREGATOR_DOMAINS = (
    "carehome.co.uk/carehome.cfm",
    "yell.com",
    "tripadvisor.com",
    "booking.com",
    "google.com/maps",
)


def is_valid_lead_name(name: str) -> bool:
    cleaned = name.strip()
    if not cleaned:
        return False
    lower = cleaned.lower()
    if any(b in lower for b in BAD_NAMES):
        return False
    if len(cleaned) < 4 or len(cleaned) > 80:
        return False
    if cleaned.startswith("http"):
        return False
    if cleaned.count(",") >= 3:
        return False
    if re.fullmatch(r"[\d\s+\-()]+", cleaned):
        return False
    return True


def is_real_business_lead(name: str, address: str = "", website: str = "") -> bool:
    """Reject OSM duplicates, address-as-name, and directory spam."""
    if not is_valid_lead_name(name):
        return False

    name_clean = name.strip()
    address_clean = (address or "").strip()

    # OSM often repeats the name at the start of a long address string
    if address_clean:
        if address_clean.lower().startswith(name_clean.lower()):
            tail = address_clean[len(name_clean) :].lstrip(" ,—-\u2014")
            if len(tail) > 15:
                return False
        if name_clean.lower() in address_clean.lower() and len(address_clean) > len(name_clean) + 40:
            return False

    site = (website or "").lower()
    if site and any(agg in site for agg in AGGREGATOR_DOMAINS):
        return False

    return True


def format_lead_line(index: int, name: str, address: str = "", website: str = "", phone: str = "") -> str:
    parts = [f"Lead #{index}: {name}"]
    if address:
        parts.append(address)
    if website:
        parts.append(website)
    if phone:
        parts.append(phone)
    return " | ".join(parts)
