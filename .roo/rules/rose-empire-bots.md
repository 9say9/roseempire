# Rose Empire Bot Fleet — Roo Code + Cursor Agent Rules

## Sarah — multi-source internet scraper
Sarah now searches **multiple sources** in one run:

| Source | Key | Status |
|--------|-----|--------|
| Google Maps | `google_maps` | Live (browser) |
| Google / Web | `google_web` | Live |
| LinkedIn | `linkedin` | Live (public pages + CSV) |
| Reddit | `reddit` | Live (public posts) |
| Facebook | `facebook` | Beta (public pages) |
| Instagram | `instagram` | Beta (public profiles) |

## Sarah — Playwright (Roo Code command)
```bat
py -3 fleet_scraper.py --limit 5 --sources google_maps --mission "care homes Manchester UK"
```
Or double-click `run_sarah_playwright.bat` (opens browser for Google Maps).

First time: accept Google consent in the browser window when it appears.

Output CSV: `linkedin-outreach/sarah_multi_source_leads.csv`

## Other bots
| Bot | Command |
|-----|---------|
| James | `py -3 fleet_ai.py --agent james "Hotel Manchester"` |
| Adeel | `py -3 lead_pipeline.py --qualify` |

Orchestrator: `py -3 fleet_orchestrator.py sarah --mission "care homes Manchester UK"`

## Notes
- Google Maps: run `--headed` once for consent, then headless works
- LinkedIn/Facebook/Instagram: public pages only (no login scraping)
- Reddit: research signals from public posts, not direct business listings
- Do not use `--no-browser` unless debugging — skips fresh Maps leads

## Local AI (free)
Ollama: `start_ollama.bat` | AI Router: `start_ai_router.bat` | Roo: OpenAI @ `http://127.0.0.1:8000/v1` model `gpt-3.5-turbo` or `gemini-free`

NotebookLM: `setup_notebooklm.bat` — business knowledge in Roo via MCP (not for code).

Dashboard: `run_ai_fleet.bat` -> http://127.0.0.1:5050
