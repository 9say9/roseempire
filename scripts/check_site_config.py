#!/usr/bin/env python3
"""Fail CI if live checkout / Sarah URLs are rewritten to localhost or placeholders."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "site-config.js"

REQUIRED = (
    "https://rose-empire-checkout.adeelcolchester.workers.dev",
    "https://rose-empire-sarah.adeelcolchester.workers.dev",
)
FORBIDDEN = (
    "http://127.0.0.1",
    "http://localhost",
    "sk_live_",
    "sk_test_",
    "pk_live_",
    "pk_test_",
)


def main() -> int:
    text = CONFIG.read_text(encoding="utf-8")
    for url in REQUIRED:
        if url not in text:
            print(f"FAIL: site-config.js must include {url}")
            return 1
    for bad in FORBIDDEN:
        if bad in text:
            print(f"FAIL: site-config.js must not contain {bad}")
            return 1
    print("site-config.js OK — live checkout + Sarah URLs present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
