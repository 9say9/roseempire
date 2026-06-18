# Rose Empire — Partner bot setup (GitHub collaborators)

You already have **GitHub access** to https://github.com/9say9/roseempire. This guide gets the **3 bots** (Sarah, James, Adeel) running on your PC and ready for **Cursor Agent** to help you improve them.

---

## What you get from GitHub

| Included in repo | You set up locally |
|------------------|-------------------|
| All bot Python code (`fleet_*.py`, `lead_pipeline.py`, etc.) | Python 3.12, Git, Ollama |
| Batch scripts (`setup_partner.bat`, `run_outreach_pipeline.bat`) | Playwright Chromium |
| `.env.example` template | Real `.env` (Adeel sends securely) |
| `AGENTS.md` + Cursor rules for AI assistant | Cursor IDE |
| Roo rules (`.roo/rules/rose-empire-bots.md`) | Ollama models (~10 GB) |

**Not on GitHub (by design):** `.env` secrets, scraped lead CSVs in `linkedin-outreach/`.

---

## Step 1 — Install tools (once)

1. **Git** — https://git-scm.com/download/win  
2. **Python 3.12** — https://python.org (tick “Add to PATH”)  
3. **Ollama** — https://ollama.com/download  
4. **Cursor** — https://cursor.com (same repo, Agent reads `AGENTS.md` automatically)

---

## Step 2 — Clone and run setup

```bat
git clone https://github.com/9say9/roseempire.git
cd roseempire
setup_partner.bat
```

`setup_partner.bat` installs Python deps, Playwright, creates `linkedin-outreach/`, and checks Ollama.

**First time only** — download AI models (30–90 min, ~10 GB):

```bat
setup_rose_empire_ai.bat
```

---

## Step 3 — Email credentials (from Adeel)

Copy the template and fill in values Adeel sends you (**not** via GitHub):

```bat
copy .env.example .env
```

Minimum for sending outreach email:

```env
INFO_EMAIL=info@roseempire.co.uk
EMAIL_PASSWORD=<m365-app-password-from-adeel>
```

Optional (bots work without these if Ollama is running):

```env
AI_PROVIDER=auto
OLLAMA_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5-coder:7b
```

---

## Step 4 — Verify all 3 bots

```bat
start_ollama.bat
test_bots.bat
```

Expected: Sarah scrape OK, James AI pitch OK, Adeel qualify OK.

Dashboard (optional):

```bat
run_ai_fleet.bat
```

Open http://127.0.0.1:5050

---

## Step 5 — Daily workflow (scraping → email)

```bat
start_ollama.bat
run_sarah_playwright.bat
py -3 lead_pipeline.py --qualify --enrich-emails --export-outreach
py -3 generate_catalog_pdf.py
py -3 send_leads_emails.py --dry-run --limit 5
py -3 send_leads_emails.py --send --limit 5
```

Or run everything step-by-step:

```bat
run_outreach_pipeline.bat
```

---

## Working with Cursor Agent

1. Open the cloned `roseempire` folder in **Cursor**.
2. Agent automatically loads **`AGENTS.md`** and **`.cursor/rules/rose-empire-bots.mdc`**.
3. Example prompts:
   - *“Run Sarah for 10 care homes in Leeds and show me the CSV.”*
   - *“Improve lead_validation to reject more fake Google Maps names.”*
   - *“Dry-run 3 outreach emails and show subjects.”*
   - *“Fix why James fails when Ollama is offline.”*

**Before pushing code:** never commit `.env` or `linkedin-outreach/*.csv`.

```bat
py -3 scripts/check_secrets.py
git add .
git commit -m "Describe your bot improvement"
git push
```

Adeel can review your pull requests or direct pushes on `main`.

---

## Bot reference

| Bot | What it does | Command |
|-----|--------------|---------|
| Sarah | Scrapes leads from web/Maps/LinkedIn/Reddit | `py -3 fleet_scraper.py --limit 10 --mission "hotels Manchester UK"` |
| James | Writes email/LinkedIn copy with AI | `py -3 fleet_ai.py --agent james "Business Name"` |
| Adeel | Qualifies and merges lead CSVs | `py -3 lead_pipeline.py --qualify` |

Orchestrator: `py -3 fleet_orchestrator.py status`

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Ollama offline` | Run `start_ollama.bat` or open Ollama from Start menu |
| Google Maps empty | Run with `--headed`, accept consent in browser once |
| Email send fails | Check `.env` — ask Adeel for a fresh M365 app password |
| `playwright` error | `py -3 -m playwright install chromium` |
| No leads CSV | Run Sarah first; folder `linkedin-outreach/` is created automatically |

---

## Contact

Ask **Adeel** for:
- `.env` / M365 app password (secure message only)
- Mission targets (cities, industries)
- Approval before large email sends (`--limit` keeps batches small)

Happy scraping.
