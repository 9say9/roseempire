"""Record a short Sarah scraper demo MP4 for TikTok/Shorts test edits."""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

from playwright.async_api import Page, async_playwright

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
OUT_DIR = ROOT / "demo-recordings"
PROFILE = ROOT / "linkedin-outreach" / "browser_profile"
OVERLAY_HTML = OUT_DIR / "crm_overlay.html"
CSV_OUT = OUT_DIR / "test_leads.csv"

STEALTH_INIT = "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def _write_overlay(leads: list[dict[str, str]], mission: str) -> None:
    rows_html = ""
    for i, lead in enumerate(leads, 1):
        rows_html += (
            f"<tr><td>{i}</td><td>{lead.get('name','')}</td>"
            f"<td>{lead.get('phone','—')}</td><td>{lead.get('website','—')}</td></tr>\n"
        )
    html = f"""<!DOCTYPE html>
<html><head><meta charset='utf-8'><title>Rose Empire CRM</title>
<style>
  body {{ font-family: Segoe UI, sans-serif; background:#0b1220; color:#e8eef7; margin:0; padding:24px; }}
  h1 {{ font-size:28px; margin:0 0 8px; }}
  .sub {{ color:#8ba3c7; margin-bottom:20px; }}
  table {{ width:100%; border-collapse:collapse; background:#121b2e; border-radius:12px; overflow:hidden; }}
  th, td {{ padding:14px 16px; text-align:left; border-bottom:1px solid #1e2a42; }}
  th {{ background:#1a2740; color:#7dd3fc; font-size:13px; text-transform:uppercase; letter-spacing:.06em; }}
  tr:last-child td {{ border-bottom:none; }}
  .badge {{ display:inline-block; background:#065f46; color:#6ee7b7; padding:4px 10px; border-radius:999px; font-size:12px; }}
</style></head>
<body>
  <h1>Rose Empire — Live Lead CRM</h1>
  <p class='sub'>Mission: {mission} &nbsp; <span class='badge'>{len(leads)} leads captured</span></p>
  <table><thead><tr><th>#</th><th>Business</th><th>Phone</th><th>Website</th></tr></thead>
  <tbody>{rows_html or '<tr><td colspan=4>No leads yet</td></tr>'}</tbody></table>
</body></html>"""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OVERLAY_HTML.write_text(html, encoding="utf-8")


def _save_csv(leads: list[dict[str, str]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with CSV_OUT.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["name", "phone", "website", "address", "query"])
        writer.writeheader()
        writer.writerows(leads)


async def _scrape_maps(page: Page, mission: str, limit: int) -> list[dict[str, str]]:
    from directory_scraper import scrape_google_maps_directory

    return await scrape_google_maps_directory(
        page, query=mission, limit=limit, enrich_details=False, headed=True
    )


async def record_demo(mission: str, limit: int, vertical: bool) -> Path | None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    video_dir = OUT_DIR / f"session-{stamp}"
    video_dir.mkdir(parents=True, exist_ok=True)

    if vertical:
        viewport = {"width": 1080, "height": 1920}
        video_size = {"width": 1080, "height": 1920}
    else:
        viewport = {"width": 1920, "height": 1080}
        video_size = {"width": 1920, "height": 1080}

    leads: list[dict[str, str]] = []

    async with async_playwright() as p:
        launch_kwargs = dict(
            headless=False,
            user_agent=USER_AGENT,
            viewport=viewport,
            record_video_dir=str(video_dir),
            record_video_size=video_size,
            args=["--disable-blink-features=AutomationControlled"],
        )
        if PROFILE.is_dir():
            context = await p.chromium.launch_persistent_context(str(PROFILE), **launch_kwargs)
            browser = None
        else:
            browser_args = launch_kwargs.pop("args")
            context_kwargs = {k: v for k, v in launch_kwargs.items() if k != "headless"}
            browser = await p.chromium.launch(headless=False, args=browser_args)
            context = await browser.new_context(**context_kwargs)

        page = context.pages[0] if context.pages else await context.new_page()
        await page.add_init_script(STEALTH_INIT)

        try:
            print(f"\n  Recording demo -> {video_dir}\n")
            print(f"  Mission: {mission}")
            print(f"  Format: {'9:16 vertical' if vertical else '16:9 horizontal'}\n")

            try:
                leads = await _scrape_maps(page, mission, limit)
            except Exception as exc:
                print(f"\n  Scrape interrupted ({exc}) — saving video anyway.", file=sys.stderr)

            if leads:
                _save_csv(leads)
                _write_overlay(leads, mission)
                overlay_url = OVERLAY_HTML.resolve().as_uri()
                print("\n  Opening CRM overlay for split-screen proof...")
                await asyncio.sleep(2)
                await page.goto(overlay_url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(5)
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(3)
            else:
                print("\n  WARN: No leads scraped — video will still save.", file=sys.stderr)

        finally:
            await context.close()
            if browser is not None:
                await browser.close()

    videos = sorted(video_dir.glob("*.webm")) + sorted(video_dir.glob("*.mp4"))
    if not videos:
        print("ERROR: No video file produced.", file=sys.stderr)
        return None

    src = videos[-1]
    dest = OUT_DIR / f"rose-empire-demo-{stamp}.webm"
    if src.suffix.lower() == ".mp4":
        dest = OUT_DIR / f"rose-empire-demo-{stamp}.mp4"
    dest.write_bytes(src.read_bytes())

    meta = {
        "mission": mission,
        "leads": len(leads),
        "video": str(dest),
        "csv": str(CSV_OUT) if leads else None,
        "overlay": str(OVERLAY_HTML) if leads else None,
        "vertical": vertical,
    }
    (OUT_DIR / f"rose-empire-demo-{stamp}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )
    return dest


def main() -> int:
    parser = argparse.ArgumentParser(description="Record Sarah scraper demo video")
    parser.add_argument(
        "--mission",
        default="independent home decor shops Midlands UK",
    )
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--vertical", action="store_true")
    parser.add_argument("--open", action="store_true")
    args = parser.parse_args()

    try:
        path = asyncio.run(record_demo(args.mission, args.limit, args.vertical))
    except KeyboardInterrupt:
        print("\nCancelled.")
        return 130

    if not path:
        return 1

    print("\n" + "=" * 60)
    print("  DEMO VIDEO READY")
    print("=" * 60)
    print(f"  Video:   {path}")
    print(f"  CSV:     {CSV_OUT}")
    print(f"  Overlay: {OVERLAY_HTML}")
    print("=" * 60)

    if args.open:
        webbrowser.open(str(OUT_DIR))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
