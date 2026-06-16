"""Rose Empire fleet orchestrator — single entry for Roo Code, Cursor Agent, and batch scripts."""
from __future__ import annotations

import argparse
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _py() -> str:
    return sys.executable


def _run(cmd: list[str]) -> int:
    print(f"\n>> {' '.join(cmd)}\n")
    return subprocess.call(cmd, cwd=ROOT)


def cmd_status() -> int:
    from fleet_ai import active_model, ai_available, ai_provider, ollama_online

    print("Rose Empire Bot Fleet — Status")
    print("=" * 40)
    print(f"Project:  {ROOT}")
    print(f"Ollama:   {'online' if ollama_online() else 'OFFLINE — run start_ollama.bat'}")
    print(f"AI:       {ai_provider()} ({active_model()})" if ai_available() else "AI:       offline")
    print(f"Dashboard: http://127.0.0.1:5050 (run_ai_fleet.bat)")

    try:
        req = urllib.request.Request("http://127.0.0.1:5050/health", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            print(f"Fleet API: online (HTTP {resp.status})")
    except Exception:
        print("Fleet API: offline — run run_ai_fleet.bat")

    csv = ROOT / "linkedin-outreach" / "qualified_manchester_leads.csv"
    print(f"Leads CSV: {csv} ({'exists' if csv.is_file() else 'missing'})")
    return 0


def cmd_sarah(mission: str, limit: int, no_browser: bool, headed: bool, sources: str) -> int:
    cmd = [_py(), "fleet_scraper.py", "--limit", str(limit), "--mission", mission]
    if sources:
        cmd.extend(["--sources", sources])
    if no_browser:
        cmd.append("--no-browser")
    if headed:
        cmd.append("--headed")
    return _run(cmd)


def cmd_james(target: str) -> int:
    return _run([_py(), "fleet_ai.py", "--agent", "james", target])


def cmd_adeel(qualify: bool) -> int:
    cmd = [_py(), "lead_pipeline.py"]
    if qualify:
        cmd.append("--qualify")
    return _run(cmd)


def cmd_sarah_hotels(max_cities: int, per_city: int, headed: bool, enrich_only: bool) -> int:
    cmd = [_py(), "scrape_uk_hotels.py", "--max-cities", str(max_cities), "--per-city", str(per_city)]
    if headed:
        cmd.append("--headed")
    if enrich_only:
        cmd.append("--enrich-only")
    return _run(cmd)


def cmd_test_all() -> int:
    from fleet_ai import ai_available

    failures = 0

    print("\n=== TEST 1/3: Sarah (scraper, free) ===")
    if cmd_sarah("care homes Manchester UK", 5, no_browser=False, headed=False, sources="") != 0:
        failures += 1

    print("\n=== TEST 2/3: James (copy, needs Ollama or OpenAI) ===")
    if not ai_available():
        print("SKIP: AI offline — run start_ollama.bat first")
        failures += 1
    elif cmd_james("Test Boutique Hotel Manchester") != 0:
        failures += 1

    print("\n=== TEST 3/3: Adeel (data, free) ===")
    if cmd_adeel(qualify=False) != 0:
        failures += 1

    print("\n" + "=" * 40)
    if failures:
        print(f"DONE with {failures} failure(s). Fix issues above.")
        return 1
    print("ALL 3 BOTS OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Rose Empire fleet orchestrator")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Show Ollama, AI, and fleet status")

    p_sarah = sub.add_parser("sarah", help="Run Sarah lead scraper")
    p_sarah.add_argument("--mission", default="boutique hotels Manchester UK")
    p_sarah.add_argument("--limit", type=int, default=5)
    p_sarah.add_argument("--sources", default="", help="google_maps,linkedin,reddit,facebook,instagram,google_web")
    p_sarah.add_argument("--no-browser", action="store_true", help="Skip Google Maps only")
    p_sarah.add_argument("--headed", action="store_true", help="Show browser for Google consent")

    p_james = sub.add_parser("james", help="Run James email draft")
    p_james.add_argument("target", nargs="?", default="Test Hotel Manchester")

    p_adeel = sub.add_parser("adeel", help="Run Adeel lead qualify/merge")
    p_adeel.add_argument("--qualify", action="store_true", help="Save qualified_manchester_leads.csv")

    p_hotels = sub.add_parser("sarah-hotels", help="Scrape UK hotels (Maps + emails)")
    p_hotels.add_argument("--max-cities", type=int, default=12)
    p_hotels.add_argument("--per-city", type=int, default=6)
    p_hotels.add_argument("--headed", action="store_true", help="Visible browser for Google consent")
    p_hotels.add_argument("--enrich-only", action="store_true", help="Find emails on existing uk_hotel_leads.csv")

    sub.add_parser("test-all", help="Smoke-test all 3 bots")

    args = parser.parse_args()

    if args.command == "status":
        return cmd_status()
    if args.command == "sarah":
        return cmd_sarah(args.mission, args.limit, args.no_browser, args.headed, args.sources)
    if args.command == "james":
        return cmd_james(args.target)
    if args.command == "adeel":
        return cmd_adeel(args.qualify)
    if args.command == "sarah-hotels":
        return cmd_sarah_hotels(args.max_cities, args.per_city, args.headed, args.enrich_only)
    if args.command == "test-all":
        return cmd_test_all()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
