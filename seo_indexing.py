"""
Rose Empire — ping search engines to discover sitemap (no Netlify deploy needed).
Run: py -3.12 seo_indexing.py
"""
from __future__ import annotations

import sys
import urllib.parse
import urllib.request

SITE = "https://www.roseempire.co.uk/"
SITEMAP = "https://www.roseempire.co.uk/sitemap.xml"

PING_URLS = [
    ("Bing", f"https://www.bing.com/ping?sitemap={urllib.parse.quote(SITEMAP, safe='')}"),
    ("Yandex", f"https://webmaster.yandex.com/ping?sitemap={urllib.parse.quote(SITEMAP, safe='')}"),
]

MANUAL_LINKS = [
    ("Google Search Console — request indexing", "https://search.google.com/search-console?resource_id=https%3A%2F%2Fwww.roseempire.co.uk%2F"),
    ("Google URL Inspection", "https://search.google.com/search-console/inspect?resource_id=https%3A%2F%2Fwww.roseempire.co.uk%2F"),
    ("Bing Webmaster Tools — add site", "https://www.bing.com/webmasters/about"),
    ("LinkedIn Post Inspector", "https://www.linkedin.com/post-inspector/inspect/" + urllib.parse.quote(SITE, safe="")),
]


def ping(name: str, url: str) -> None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "RoseEmpire-SEO/1.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            print(f"  OK  {name} ({resp.status})")
    except Exception as err:
        print(f"  --  {name}: {err}")


def main() -> None:
    print("\n" + "=" * 60)
    print("  Rose Empire — search engine indexing (no deploy)")
    print("=" * 60)
    print(f"\nSite:    {SITE}")
    print(f"Sitemap: {SITEMAP}\n")
    print("Pinging sitemap...")
    for name, url in PING_URLS:
        ping(name, url)
    print("\nManual steps (open in browser):")
    for label, url in MANUAL_LINKS:
        print(f"  • {label}")
        print(f"    {url}")
    if "--open" in sys.argv:
        import webbrowser
        for _, url in MANUAL_LINKS:
            webbrowser.open(url)
    print("\nBacklinks you control (free, do today):")
    print("  1. LinkedIn company page → set website to roseempire.co.uk")
    print("  2. LinkedIn personal profile → website + featured link")
    print("  3. Google Business Profile → add website (if you have a listing)")
    print("  4. Bing Webmaster → verify site + submit sitemap.xml")
    print("  5. Share catalog link on LinkedIn launch post")
    print("\nLocal SEO files updated — deploy when Netlify credits return.\n")


if __name__ == "__main__":
    main()
