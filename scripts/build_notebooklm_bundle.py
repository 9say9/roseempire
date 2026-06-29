"""Build a single knowledge file to upload into Google NotebookLM (Rose Empire)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "notebooklm"
OUT_FILE = OUT_DIR / "rose-empire-knowledge-pack.md"

SECTIONS = [
    ("AGENTS.md", ROOT / "AGENTS.md"),
    ("PARTNER_BOT_SETUP.md", ROOT / "PARTNER_BOT_SETUP.md"),
    (".roo/rules/rose-empire-bots.md", ROOT / ".roo" / "rules" / "rose-empire-bots.md"),
    ("catalog-data.json", ROOT / "catalog-data.json"),
    ("chat-prompts.json", ROOT / "chat-prompts.json"),
]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    parts: list[str] = [
        "# Rose Empire — NotebookLM knowledge pack",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "Upload this file to a NotebookLM notebook titled **Rose Empire B2B**.",
        "Then enable the NotebookLM MCP server in Cursor for Roo Code.",
        "",
    ]

    for title, path in SECTIONS:
        parts.append(f"\n\n---\n\n## Source: {title}\n\n")
        if not path.is_file():
            parts.append(f"_(missing: {path})_\n")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if path.suffix == ".json":
            try:
                text = json.dumps(json.loads(text), indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                pass
        parts.append(text)

    workflow = """
---

## Rose Empire daily workflow (for NotebookLM Q&A)

1. `start_ollama.bat` + `start_ai_router.bat` + `run_ai_fleet.bat`
2. CRM dashboard: http://127.0.0.1:5050
3. Sarah scrape: `run_sarah_playwright.bat` or fleet_scraper.py
4. Adeel qualify: `py -3 lead_pipeline.py --qualify --enrich-emails --export-outreach`
5. James pitch: CRM pitch generator or `py -3 fleet_ai.py --agent james "Hotel Name"`
6. Email: `py -3 send_leads_emails.py --dry-run --limit 5` then `--send --limit 5`
7. Roo AI: OpenAI @ http://127.0.0.1:8000/v1 model gpt-3.5-turbo (AI Router)

Bots: Sarah (scrape), James (copy), Adeel (qualify/data).
Never commit .env or linkedin-outreach/*.csv to GitHub.
"""
    parts.append(workflow)
    OUT_FILE.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {OUT_FILE} ({OUT_FILE.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
