# Rose Empire — Agent instructions (Cursor + collaborators)

This repo runs a **3-bot fleet** for B2B lead scraping and email outreach for [Rose Empire](https://www.roseempire.co.uk) (wholesale bedding / hospitality supplies).

**Human setup:** see `PARTNER_BOT_SETUP.md` first (clone, Ollama, `.env`, Playwright).

---

## The 3 bots

| Bot | Role | Main file | Run |
|-----|------|-----------|-----|
| **Sarah** | Multi-source scraper (Google Maps, web, LinkedIn public, Reddit) | `fleet_scraper.py`, `sarah_sources.py` | `py -3 fleet_scraper.py --limit 10 --mission "care homes Manchester UK"` |
| **James** | AI copy — email pitches, LinkedIn drafts | `fleet_ai.py` | `py -3 fleet_ai.py --agent james "Hotel Name Manchester"` |
| **Adeel** | Merge, qualify, dedupe leads | `lead_pipeline.py`, `lead_validation.py` | `py -3 lead_pipeline.py --qualify --enrich-emails --export-outreach` |

**Orchestrator (single entry):** `py -3 fleet_orchestrator.py test-all`

**Dashboard:** `run_ai_fleet.bat` → http://127.0.0.1:5050 (`app.py`)

**Full outreach pipeline:** `run_outreach_pipeline.bat`

---

## Sarah — scraper details

Sources: `google_maps`, `google_web`, `linkedin`, `reddit`, `facebook` (beta), `instagram` (beta)

```bat
py -3 fleet_scraper.py --list-sources
py -3 fleet_scraper.py --limit 10 --mission "care homes Manchester UK"
py -3 fleet_scraper.py --sources google_maps,linkedin --limit 8 --headed
```

- First Google Maps run: use `--headed` once and accept consent in the browser.
- Do **not** use `--no-browser` for production — skips fresh Maps leads.
- Output: `linkedin-outreach/sarah_multi_source_leads.csv`

---

## Email outreach

```bat
py -3 send_leads_emails.py --dry-run --limit 5
py -3 send_leads_emails.py --send --limit 5
```

Requires `.env` with `INFO_EMAIL` and `EMAIL_PASSWORD` (M365 app password). Never commit `.env`.

Catalog PDF: `py -3 generate_catalog_pdf.py` → `assets/Rose-Empire-Wholesale-Catalog.pdf`

---

## AI stack (free default)

- **Ollama** local models — run `start_ollama.bat` before James or AI email drafts.
- Models: `qwen2.5-coder:7b` (main), fallbacks in `.env.example`.
- Optional cloud keys in `.env`: `OPENAI_API_KEY`, `GEMINI_API_KEY` — not required for bots.

Test AI: `py -3 fleet_orchestrator.py test-all`

---

## Lead data (local only)

All scraped leads live in `linkedin-outreach/` — **gitignored** on purpose. Each machine builds its own CSVs.

Key files after a run:
- `sarah_multi_source_leads.csv` — raw Sarah output
- `qualified_manchester_leads.csv` — Adeel qualified
- `outreach_master.csv` — ready for email + call follow-up
- `email_send_log.csv` — send history

---

## When improving the bots

| Goal | Files to edit |
|------|----------------|
| New scrape sources / better parsing | `sarah_sources.py`, `fleet_scraper.py` |
| Lead quality / fake-name filter | `lead_validation.py`, `lead_pipeline.py` |
| Email discovery on websites | `send_leads_emails.py`, `email_utils.py` |
| AI pitch tone / prompts | `fleet_ai.py` |
| Sending / M365 | `email_agent.py` |
| Dashboard / API | `app.py` |
| Batch scripts | `run_*.bat`, `fleet_orchestrator.py` |

After changes:
1. `py -3 fleet_orchestrator.py test-all`
2. `py -3 send_leads_emails.py --dry-run --limit 3`
3. Commit and push — `.env` and `linkedin-outreach/*.csv` must **never** be committed.

---

## Security rules for agents

- Do **not** commit `.env`, API keys, passwords, or `graph_token.json`.
- Do **not** add real credentials to tracked files — use `.env.example` placeholders only.
- Run `py -3 scripts/check_secrets.py` before pushing if you touched config or email code.

---

## Quick test commands

```bat
setup_partner.bat
test_bots.bat
run_sarah_playwright.bat
py -3 fleet_orchestrator.py status
```
