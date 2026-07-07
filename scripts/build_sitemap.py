"""Regenerate sitemap.xml from public URLs."""
from __future__ import annotations

from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITEMAP = ROOT / "sitemap.xml"
TODAY = date.today().isoformat()

URLS = [
    ("/", "weekly", "1.0"),
    ("/care-homes.html", "monthly", "0.9"),
    ("/hotels.html", "monthly", "0.9"),
    ("/wholesale-mattress-protectors.html", "monthly", "0.9"),
    ("/privacy.html", "yearly", "0.3"),
    ("/catalog-data.json", "weekly", "0.6"),
]

lines = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
]
for path, freq, priority in URLS:
    loc = f"https://www.roseempire.co.uk{path}"
    lines.extend([
        "  <url>",
        f"    <loc>{loc}</loc>",
        f"    <lastmod>{TODAY}</lastmod>",
        f"    <changefreq>{freq}</changefreq>",
        f"    <priority>{priority}</priority>",
        "  </url>",
    ])
lines.append("</urlset>")
lines.append("")
SITEMAP.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {SITEMAP} ({len(URLS)} URLs)")
