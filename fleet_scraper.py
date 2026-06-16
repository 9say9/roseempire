"""Sarah — multi-source lead scraper (Google, LinkedIn, web, Reddit, Facebook, Instagram)."""
from __future__ import annotations

import sys

from sarah_sources import SOURCE_REGISTRY, list_sources, scrape_fresh_leads, scrape_multi_source


def scrape_all_leads(mission: str, limit: int = 5, *, use_browser: bool = True, headed: bool = False) -> list[str]:
    if not use_browser:
        sources = [s for s in SOURCE_REGISTRY if s != "google_maps"]
        return scrape_fresh_leads(mission, limit=limit, headed=headed, sources=sources or None)
    return scrape_fresh_leads(mission, limit=limit, headed=headed)


def _cli() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Sarah — multi-source B2B lead scraper")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument(
        "--mission",
        default="care homes boutique hotels Manchester UK",
        help="Search mission / query",
    )
    parser.add_argument(
        "--sources",
        default="",
        help="Comma-separated: google_maps,google_web,linkedin,reddit,facebook,instagram",
    )
    parser.add_argument("--headed", action="store_true", help="Show browser (Google consent)")
    parser.add_argument("--no-browser", action="store_true", help="Skip Google Maps only")
    parser.add_argument("--list-sources", action="store_true", help="Show available sources")
    args = parser.parse_args()

    if args.list_sources:
        print(list_sources())
        return 0

    sources = [s.strip() for s in args.sources.split(",") if s.strip()] or None
    if args.no_browser:
        sources = [s for s in (sources or list(SOURCE_REGISTRY)) if s != "google_maps"]
        print("NOTE: Skipping google_maps (no browser).", file=sys.stderr)

    leads = scrape_multi_source(
        args.mission,
        limit=args.limit,
        sources=sources,
        headed=args.headed,
    )

    if not leads:
        print(
            "No leads found.\n"
            "Try: py -3 fleet_scraper.py --headed --mission \"care homes Manchester UK\"\n"
            "Sources: py -3 fleet_scraper.py --list-sources",
            file=sys.stderr,
        )
        return 1

    for i, lead in enumerate(leads, 1):
        print(lead.to_line(i))
    print(f"\nOK: {len(leads)} lead(s) from {len({l.source for l in leads})} source(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
