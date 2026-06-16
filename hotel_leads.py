"""Detect hotel / hospitality leads for UK wholesale outreach."""
from __future__ import annotations

import re

HOTEL_KEYWORDS = re.compile(
    r"\b("
    r"hotel|hotels|inn\b|inns\b|suites|resort|motel|lodging|"
    r"marriott|hilton|premier\s*inn|travelodge|holiday\s*inn|"
    r"radisson|ibis|novotel|best\s*western|whitbread|macdonald\s*hotel|"
    r"doubletree|crowne\s*plaza|hyatt|sheraton|mercure|"
    r"guest\s*house|b\s*&\s*b|bed\s*and\s*breakfast"
    r")\b",
    re.I,
)

NOT_HOTEL = re.compile(
    r"\b("
    r"care\s*home|nursing|hospital|school|university|college|"
    r"restaurant(?!\s*hotel)|\bpub\b|\bbar\b|nightclub|casino|"
    r"car\s*hire|parking|estate\s*agent|supermarket|gym\b|"
    r"carehome\.co\.uk"
    r")\b",
    re.I,
)


def is_hotel_lead(name: str, *, query: str = "", address: str = "", website: str = "") -> bool:
    blob = " ".join([name or "", query or "", address or "", website or ""])
    if not blob.strip():
        return False
    if NOT_HOTEL.search(blob):
        return False
    return bool(HOTEL_KEYWORDS.search(blob))
