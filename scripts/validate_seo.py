#!/usr/bin/env python3
"""Local SEO / JSON-LD checks for Rose Empire public HTML. No network required."""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PAGES = [
    "index.html",
    "hotels.html",
    "care-homes.html",
    "holiday-lets.html",
    "wholesale-mattress-protectors.html",
    "wholesale-pillows.html",
    "shipping-and-returns.html",
    "privacy.html",
    "404.html",
]
CANONICAL_HOST = "https://www.roseempire.co.uk"
FORBIDDEN_HANDLES = ("@roseempireuk",)
FORBIDDEN_SCHEMA = ("aggregateRating", "reviewCount", "ratingValue")


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self._in_title = False
        self.metas: list[tuple[str, str, str]] = []
        self.canonical = ""
        self.h1s: list[str] = []
        self._in_h1 = False
        self._h1_buf: list[str] = []
        self.json_ld: list[str] = []
        self._in_ld = False
        self._ld_buf: list[str] = []
        self.ld_type = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        ad = {k: (v or "") for k, v in attrs}
        if tag == "title":
            self._in_title = True
        if tag == "h1":
            self._in_h1 = True
            self._h1_buf = []
        if tag == "link" and ad.get("rel") == "canonical":
            self.canonical = ad.get("href", "")
        if tag == "meta":
            key = ad.get("property") or ad.get("name") or ""
            self.metas.append((key, ad.get("content", ""), ad.get("name", "")))
        if tag == "script" and ad.get("type") == "application/ld+json":
            self._in_ld = True
            self._ld_buf = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "h1":
            self._in_h1 = False
            self.h1s.append(re.sub(r"\s+", " ", "".join(self._h1_buf)).strip())
        if tag == "script" and self._in_ld:
            self._in_ld = False
            self.json_ld.append("".join(self._ld_buf))

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        if self._in_h1:
            self._h1_buf.append(data)
        if self._in_ld:
            self._ld_buf.append(data)


def meta_map(parser: PageParser) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, content, _name in parser.metas:
        if key:
            out[key] = content
    return out


def check_page(path: Path, titles: dict[str, str]) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(text)
    rel = path.name

    title = parser.title.strip()
    if not title:
        errors.append(f"{rel}: missing <title>")
    elif title in titles:
        errors.append(f"{rel}: duplicate title with {titles[title]}")
    else:
        titles[title] = rel

    if len(parser.h1s) != 1:
        errors.append(f"{rel}: expected 1 H1, found {len(parser.h1s)} {parser.h1s!r}")

    if not parser.canonical.startswith(CANONICAL_HOST):
        errors.append(f"{rel}: canonical is not on www ({parser.canonical!r})")

    metas = meta_map(parser)
    if rel != "404.html":
        for key in ("og:title", "og:description", "og:image", "twitter:card", "twitter:image"):
            if not metas.get(key):
                errors.append(f"{rel}: missing {key}")
        if metas.get("og:image:width") != "1200" or metas.get("og:image:height") != "630":
            errors.append(
                f"{rel}: og image size {metas.get('og:image:width')}x{metas.get('og:image:height')} (want 1200x630)"
            )
        if metas.get("og:image") and not metas["og:image"].endswith("og-share.jpg"):
            errors.append(f"{rel}: og:image should be og-share.jpg")
        if rel != "404.html" and "noindex" not in metas.get("robots", ""):
            desc = metas.get("description", "")
            if not (50 <= len(desc) <= 170):
                errors.append(f"{rel}: meta description length {len(desc)} (want 50–170)")

    if "twitter:site" in metas or "twitter:creator" in metas:
        errors.append(f"{rel}: invented twitter:site/creator present")

    for token in FORBIDDEN_HANDLES:
        if token in text:
            errors.append(f"{rel}: contains forbidden handle {token}")

    cdn_fa = "cdnjs.cloudflare.com/ajax/libs/font-awesome" in text
    if cdn_fa:
        errors.append(f"{rel}: unused Font Awesome CDN still linked")

    if rel != "404.html" and not parser.json_ld:
        errors.append(f"{rel}: missing JSON-LD")

    for blob in parser.json_ld:
        try:
            data = json.loads(blob)
        except json.JSONDecodeError as exc:
            errors.append(f"{rel}: JSON-LD parse error: {exc}")
            continue
        dumped = json.dumps(data)
        for bad in FORBIDDEN_SCHEMA:
            if bad in dumped:
                errors.append(f"{rel}: JSON-LD contains {bad}")
        if isinstance(data, dict) and data.get("@context") not in (
            "https://schema.org",
            "http://schema.org",
        ):
            errors.append(f"{rel}: JSON-LD missing schema.org context")

    return errors


def main() -> int:
    errors: list[str] = []
    titles: dict[str, str] = {}
    for name in PUBLIC_PAGES:
        path = ROOT / name
        if not path.is_file():
            errors.append(f"missing file {name}")
            continue
        errors.extend(check_page(path, titles))

    og = ROOT / "assets" / "og-share.jpg"
    if not og.is_file():
        errors.append("missing assets/og-share.jpg")
    else:
        # JPEG SOF0 scan for dimensions
        data = og.read_bytes()
        i = 2
        dims = None
        while i < len(data) - 8:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2):
                h, w = int.from_bytes(data[i + 5 : i + 7], "big"), int.from_bytes(
                    data[i + 7 : i + 9], "big"
                )
                dims = (w, h)
                break
            if marker in (0xD8, 0xD9):
                i += 2
                continue
            seglen = int.from_bytes(data[i + 2 : i + 4], "big")
            i += 2 + seglen
        if dims != (1200, 630):
            errors.append(f"og-share.jpg is {dims}, want 1200x630")
        if og.stat().st_size > 400_000:
            errors.append(f"og-share.jpg is {og.stat().st_size} bytes (too heavy)")

    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    for needle in (
        "holiday-lets.html",
        "llms.txt",
        "2026-09-29",
        "og-share.jpg",
    ):
        if needle not in sitemap:
            errors.append(f"sitemap.xml missing {needle}")

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "Sitemap: https://www.roseempire.co.uk/sitemap.xml" not in robots:
        errors.append("robots.txt missing sitemap line")
    if "GPTBot" not in robots:
        errors.append("robots.txt missing GPTBot allow")

    workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
    if "holiday-lets.html" not in workflow or "site.webmanifest" not in workflow:
        errors.append("pages.yml does not copy holiday-lets.html or site.webmanifest")

    if errors:
        print("SEO validation FAILED")
        for err in errors:
            print(" -", err)
        return 1
    print(f"SEO validation OK — {len(PUBLIC_PAGES)} pages, unique titles, JSON-LD parses.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
