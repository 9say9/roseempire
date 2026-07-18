#!/usr/bin/env python3
"""Quick live health check for roseempire.co.uk (run anytime after deploy)."""
from __future__ import annotations

import json
import sys
import urllib.request

CHECKS = [
    ("homepage", "https://www.roseempire.co.uk/", ("stripe-checkout-btn", "sarah-widget.js", "rose-empire-sarah")),
    (
        "checkout worker",
        "https://rose-empire-checkout.adeelcolchester.workers.dev/api/checkout/config",
        None,
    ),
    (
        "sarah api",
        "https://rose-empire-sarah.adeelcolchester.workers.dev/health",
        ("ok", "sarah"),
    ),
]


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "roseempire-smoke/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="replace")


def main() -> int:
    failed = 0
    for name, url, needles in CHECKS:
        try:
            body = fetch(url)
            if name == "checkout worker":
                data = json.loads(body)
                ok = data.get("status") == "success" and data.get("enabled") is True
                detail = f"mode={data.get('mode')} enabled={data.get('enabled')}"
            else:
                ok = all(n in body for n in (needles or ()))
                detail = "markers ok" if ok else "missing expected markers"
            print(("OK  " if ok else "FAIL") + f" {name}: {detail}")
            if not ok:
                failed += 1
        except Exception as exc:  # noqa: BLE001 — smoke script
            print(f"FAIL {name}: {exc}")
            failed += 1
    if failed:
        print(f"\n{failed} check(s) failed.")
        return 1
    print("\nAll live checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
