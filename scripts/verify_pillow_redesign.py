#!/usr/bin/env python3
"""Pre-commit checks for pillow redesign: local asset refs, JSON-LD, stale copy."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {"node_modules", ".git", "company-hq"}

ASSET_RE = re.compile(
    r"""(?:src|href|srcset)=["']([^"']+)["']|url\(\s*['"]?(assets/[^'")]+)"""
)


def site_files():
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".html", ".css", ".js", ".json"}:
            continue
        if any(s in p.parts for s in SKIP_DIRS):
            continue
        if p.name.endswith(".tmp"):
            continue
        yield p


def check_assets() -> list[str]:
    errors: list[str] = []
    for p in site_files():
        text = p.read_text(encoding="utf-8", errors="ignore")
        for m in ASSET_RE.finditer(text):
            ref = (m.group(1) or m.group(2) or "").split("?")[0].split("#")[0]
            if not ref.startswith("assets/"):
                continue
            if not (ROOT / ref.replace("/", "\\")).exists() and not (ROOT / ref).exists():
                errors.append(f"{p.relative_to(ROOT)}: missing {ref}")
    return errors


def check_json_ld() -> list[str]:
    errors: list[str] = []
    for p in ROOT.glob("*.html"):
        text = p.read_text(encoding="utf-8")
        for block in re.findall(
            r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            text,
            re.I | re.S,
        ):
            try:
                json.loads(block.strip())
            except json.JSONDecodeError as e:
                errors.append(f"{p.name}: JSON-LD: {e}")
    return errors


def check_stale() -> list[str]:
    errors: list[str] = []
    for p in site_files():
        raw = p.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"£8\s*goose|from £7 duck / £8", raw, re.I):
            errors.append(f"{p.relative_to(ROOT)}: stale £8 goose microfibre wording")
        if "7.50" in raw:
            errors.append(f"{p.relative_to(ROOT)}: stale 7.50 price")
        if re.search(r"pillow-zip-pack|assets/warehouse/", raw, re.I):
            errors.append(f"{p.relative_to(ROOT)}: removed asset reference")
    return errors


def main() -> int:
    errors = check_assets() + check_json_ld() + check_stale()
    if errors:
        print("VERIFY FAILED:")
        for e in errors:
            print(" -", e)
        return 1
    print("verify_pillow_redesign: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
