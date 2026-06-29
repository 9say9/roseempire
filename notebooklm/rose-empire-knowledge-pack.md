# Rose Empire — NotebookLM knowledge pack
Generated: 2026-06-20 18:48 UTC

Upload this file to a NotebookLM notebook titled **Rose Empire B2B**.
Then enable the NotebookLM MCP server in Cursor for Roo Code.



---

## Source: AGENTS.md


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

## NotebookLM (business brain for Roo)

NotebookLM is **not** a coding model — it holds your **Rose Empire docs** (catalog, MOQ, outreach playbook) with citations.

```bat
setup_notebooklm.bat
```

1. Builds `notebooklm/rose-empire-knowledge-pack.md`
2. Configures MCP in `.cursor/mcp.json` (works in Cursor + Roo)
3. Run Google auth once: `npx -y notebooklm-mcp@latest auth`
4. Upload the knowledge pack to [NotebookLM](https://notebooklm.google.com) notebook **Rose Empire B2B**

**Roo example:** *"Query NotebookLM Rose Empire B2B for care home pitch angles."*

See `.roo/rules/notebooklm-workflow.md` for full workflow.

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



---

## Source: PARTNER_BOT_SETUP.md


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
| **Roo not loading / service worker error** | Run `fix_cursor_webview.bat`, set Cursor layout to **Editor**, open Roo from **left sidebar** |
| **Roo ignores GitHub URL** | **Normal.** Roo does not clone repos. Use Git, then **File → Open Folder** on `roseempire` |
| **Playwright not working in Roo** | **Normal.** Playwright runs outside Roo: double-click `run_sarah_playwright.bat` |
| **Roo API stuck / wrong model** | Close Cursor → `setup_roo_on_this_pc.bat` → `start_ai_router.bat` → reopen |

---

## Roo Code + GitHub (important)

Roo Code **does not** open GitHub URLs or run Playwright inside the chat panel.

**Correct workflow on a new PC (e.g. via TeamViewer):**

```bat
git clone https://github.com/9say9/roseempire.git
cd roseempire
setup_friend_pc.bat
```

Then in **Cursor**: **File → Open Folder** → select the `roseempire` folder (not a URL).

1. Adeel sends `.env` → save as `roseempire\.env`
2. `start_ai_router.bat` (cloud keys + free Ollama fallback)
3. Close Cursor → `setup_roo_on_this_pc.bat` → reopen Cursor
4. **Sarah scrape:** `run_sarah_playwright.bat` (browser opens separately)
5. **Dashboard:** `run_ai_fleet.bat` → http://127.0.0.1:5050

**Roo AI settings (after `setup_roo_on_this_pc.bat`):**

| Setting | Value |
|---------|--------|
| Provider | OpenAI |
| Base URL | `http://127.0.0.1:8000/v1` |
| API Key | `local` |
| Model | `gpt-3.5-turbo` |

Fallback (no router): Ollama → `http://127.0.0.1:11434` → `qwen2.5-coder:1.5b`

---

## Contact

Ask **Adeel** for:
- `.env` / M365 app password (secure message only)
- Mission targets (cities, industries)
- Approval before large email sends (`--limit` keeps batches small)

Happy scraping.



---

## Source: .roo/rules/rose-empire-bots.md


﻿# Rose Empire Bot Fleet — Roo Code + Cursor Agent Rules

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
Ollama: `start_ollama.bat` | AI Router: `start_ai_router.bat` | Roo: OpenAI @ `http://127.0.0.1:8000/v1`

NotebookLM: `setup_notebooklm.bat` — business knowledge in Roo via MCP (not for code).

Dashboard: `run_ai_fleet.bat` -> http://127.0.0.1:5050



---

## Source: catalog-data.json


{
  "updatedAt": "2026-06-19",
  "contact": {
    "email": "info@roseempire.co.uk",
    "phone": "+447999988450",
    "phoneDisplay": "+44 7999 988450",
    "siteUrl": "https://www.roseempire.co.uk"
  },
  "wholesale": {
    "moqPerSize": 20,
    "boxLabel": "1 trade box = 20 pieces",
    "volumeDiscounts": [
      {
        "minPieces": 50,
        "percent": 10,
        "label": "10% off at 50+ pieces"
      },
      {
        "minPieces": 200,
        "percent": 20,
        "label": "20% off at 200+ pieces"
      }
    ],
    "quoteNote": "Formal quotes confirmed within 24 hours via RFQ form or email."
  },
  "products": [
    {
      "id": "protector-wqmp",
      "title": "WQMP – Waterproof Quilted Mattress Protector",
      "category": "protectors",
      "tag": "Bestseller",
      "tagClass": "",
      "image": "assets/mattress_protector.png",
      "gallery": [
        "assets/mattress_protector.png",
        "assets/products/protector-lifestyle.png",
        "assets/products/wqmp-layers.png"
      ],
      "desc": "The ultimate combination of protection and comfort. A soft quilted top layer paired with our 100% waterproof TPU backing that is completely silent. Machine washable, OEKO-TEX Standard 100 certified, with independent UK test report available for trade buyers.",
      "specs": [
        "Type: Waterproof Quilted Mattress Protector (WQMP)",
        "Top Layer: Soft quilted microfiber surface (150 GSM)",
        "Backing: 100% Silent Waterproof TPU membrane",
        "Certification: OEKO-TEX Standard 100 Certified",
        "Testing: Independent UK test report available on request",
        "Fit: Deep elasticated skirt – fits up to 40cm mattress depth",
        "Washable: Machine washable at 60°C"
      ],
      "moq": 20,
      "boxLabel": "1 trade box = 20 pieces",
      "basePrice": 6.01,
      "sizes": [
        {
          "name": "Pillow Pair",
          "price": 5.44
        },
        {
          "name": "Single (90×190cm)",
          "price": 6.01
        },
        {
          "name": "4ft / Small Double (120×190cm)",
          "price": 6.91
        },
        {
          "name": "Double (135×190cm)",
          "price": 7.25
        },
        {
          "name": "King (150×200cm)",
          "price": 7.88
        },
        {
          "name": "Super King (180×200cm)",
          "price": 8.97
        }
      ],
      "highlights": [
        "100% Waterproof",
        "Elastic Fitted Skirt",
        "OEKO-TEX Certified",
        "Silent TPU Backing"
      ],
      "stockStatus": "In stock"
    },
    {
      "id": "protector-qmp",
      "title": "QMP – Quilted Mattress Protector",
      "category": "protectors",
      "tag": "Essential",
      "tagClass": "",
      "image": "assets/products/protector-lifestyle.png",
      "gallery": [
        "assets/products/protector-lifestyle.png",
        "assets/products/qmp-folded.png"
      ],
      "desc": "A premium non-waterproof quilted protector for everyday comfort and hygiene. Breathable polycotton shell with a soft microfiber quilted fill. Ideal for homes and guest houses.",
      "specs": [
        "Type: Quilted Mattress Protector (QMP)",
        "Top Layer: Soft quilted polycotton surface",
        "Fill: Lightweight microfiber padding (120 GSM)",
        "Backing: Breathable non-waterproof polycotton base",
        "Hypoallergenic: Dust mite and allergen resistant",
        "Fit: Deep elasticated fitted skirt — fits up to 35cm mattress depth",
        "Washable: Machine washable at 60°C"
      ],
      "moq": 20,
      "boxLabel": "1 trade box = 20 pieces",
      "basePrice": 5.4,
      "sizes": [
        {
          "name": "Pillow Pair",
          "price": 4.74
        },
        {
          "name": "Single (90×190cm)",
          "price": 5.4
        },
        {
          "name": "4ft / Small Double (120×190cm)",
          "price": 5.95
        },
        {
          "name": "Double (135×190cm)",
          "price": 6.19
        },
        {
          "name": "King (150×200cm)",
          "price": 6.54
        },
        {
          "name": "Super King (180×200cm)",
          "price": 7.21
        }
      ],
      "highlights": [
        "Quilted Surface",
        "Elastic Fitted Skirt",
        "Breathable",
        "Hypoallergenic"
      ],
      "stockStatus": "In stock"
    },
    {
      "id": "protector-terry",
      "title": "Terry Waterproof Mattress Protector",
      "category": "protectors",
      "tag": "Hotel Grade",
      "tagClass": "tag-gold",
      "image": "assets/products/terry-lifestyle-bed.jpg",
      "gallery": [
        "assets/products/terry-lifestyle-bed.jpg",
        "assets/products/terry-elastic-skirt.jpg",
        "assets/products/terry-waterproof-product.jpg"
      ],
      "desc": "Classic terry towelling surface with a 100% waterproof backing. Highly absorbent cotton loop pile, deep elastic fitted skirt on every size, and industrial-laundry durability — the preferred choice for hotels and care homes.",
      "specs": [
        "Type: Terry Towelling Waterproof Mattress Protector",
        "Surface: 100% Cotton Terry loop pile top layer",
        "Backing: 100% Waterproof PU/TPU membrane",
        "Absorbency: High-absorbent cotton loop pile surface",
        "Fit: Deep elasticated fitted skirt — all sizes, fits mattresses up to 35cm deep",
        "Durability: Industrial-laundry resistant – up to 60°C wash"
      ],
      "moq": 20,
      "boxLabel": "1 trade box = 20 pieces",
      "basePrice": 5.2,
      "sizes": [
        {
          "name": "Pillow Pair",
          "price": 4.4
        },
        {
          "name": "Cot",
          "price": 4.4
        },
        {
          "name": "Single (90×190cm)",
          "price": 5.2
        },
        {
          "name": "4ft / Small Double (120×190cm)",
          "price": 5.6
        },
        {
          "name": "Double (135×190cm)",
          "price": 5.7
        },
        {
          "name": "King (150×200cm)",
          "price": 6.3
        },
        {
          "name": "Super King (180×200cm)",
          "price": 6.85
        }
      ],
      "highlights": [
        "Terry Cotton Surface",
        "Deep Elastic Skirt",
        "100% Waterproof",
        "Hotel Grade"
      ],
      "stockStatus": "In stock"
    },
    {
      "id": "pillow-feather-down",
      "title": "Goose Feather & Duck Down Pillows (2-Piece)",
      "category": "pillows",
      "tag": "Wholesale",
      "tagClass": "tag-gold",
      "image": "assets/down_pillows.png",
      "desc": "Wholesale feather and down pillows with goose feather or duck down filling. Down-proof cover, medium loft, sold as a pair of 2 pillows per piece. Standard size only.",
      "specs": [
        "Sold as: Pair of 2 pillows per piece",
        "Fill options: Goose feather & down, or duck feather & down",
        "Goose fill: 85% white goose feather, 15% soft goose down",
        "Duck fill: 80% duck feather, 20% soft duck down",
        "Size: Standard (50×75cm) only",
        "Care: Machine washable at 40°C"
      ],
      "moq": 20,
      "boxLabel": "1 trade box = 20 pieces",
      "basePrice": 8.5,
      "sizes": [
        {
          "name": "Standard (50×75cm) – 2 Piece",
          "price": 8.5
        }
      ],
      "highlights": [
        "Goose Feather & Down",
        "Duck Feather & Down",
        "Standard Size",
        "Set of 2 Pieces"
      ],
      "stockStatus": "In stock"
    }
  ]
}


---

## Source: chat-prompts.json


{
  "sarah": "You are Sarah, the Rose Empire Wholesale Representative on the Rose Empire B2B website.\n\nROLE: Qualify commercial volume leads and guide trade buyers toward a formal quote.\n\nWHOLESALE FACTS:\n- MOQ: 20 pieces per product size (one trade box).\n- Volume discounts: 10% at 50+ pieces, 20% at 200+ pieces.\n- Products: WQMP waterproof quilted protectors, QMP quilted protectors, Terry waterproof protectors, and Goose Feather & Duck Down pillows (2-piece sets, standard size only).\n- Pillows: Goose feather & down or duck feather & down fill — standard size (50×75cm) only. From approx. £8.50/piece depending on fill. Goose costs more than duck.\n- Trade pricing from approx. £2.40/piece for protectors depending on product and size.\n- UK-wide delivery; freight quoted by destination and volume.\n- Quote process: add to cart on site → RFQ form → PDF quote. Contact: info@roseempire.co.uk, +44 7999 988450.\n\nLEAD QUALIFICATION — collect these naturally across the conversation (do not interrogate):\n1. Business / facility name\n2. Facility type (hotel, care home, guest house, retailer, distributor, other)\n3. Business email address\n4. Estimated order volume (pieces or boxes per SKU)\n5. Products and sizes of interest\n6. UK delivery region if relevant\n\nSTRICT RULES:\n- Be professional, B2B-focused, and efficient. Stay in wholesale/trade context only.\n- Prioritise capturing: facility/business name, facility type, business email, estimated order volume, products/sizes, and UK delivery region.\n- Ask for missing lead fields naturally (one or two at a time), never as a rigid form interrogation.\n- When facility type, email, and approximate volume are known, summarise the qualified lead and invite the RFQ form or email to info@roseempire.co.uk.\n- Do NOT answer detailed retail care or consumer product-comparison questions — suggest the retail assistant or catalog for shoppers.\n- Do not promise final pricing — explain quotes are confirmed within 24 hours.\n- Never share API keys, internal systems, or fabricated client references.",
  "adeel": "You are Adeel, the Rose Empire Retail Assistant on the Rose Empire website.\n\nROLE: Help individual shoppers and small buyers with product questions only.\n\nPRODUCTS YOU KNOW:\n- WQMP Waterproof Quilted Mattress Protector — silent TPU backing, OEKO-TEX, quilted top, washable 60°C. Sizes: Single, 4ft/Small Double, Double, King, Super King.\n- QMP Quilted Mattress Protector — non-waterproof, breathable polycotton, hypoallergenic. Same size range.\n- Terry Waterproof Mattress Protector — hotel-grade cotton terry, waterproof backing, highly absorbent.\n- Goose Feather & Duck Down Pillows (2-piece set) — choose goose feather & down or duck feather & down filling. Standard size (50×75cm) only — no king or super king. Sold as a pair of 2 pillows per piece.\n\nPILLOW GUIDANCE: Goose fill = higher loft; duck fill = great value. Standard size only.\n\nSTRICT RULES:\n- Answer clearly about materials, sizes, waterproofing, care, and which product suits their need.\n- Be warm, concise, and retail-friendly. Use GBP when mentioning indicative pricing.\n- NEVER discuss wholesale MOQs, trade boxes, volume tiers, or bulk discounts — direct those buyers to Sarah or the wholesale section.\n- NEVER request business emails, facility names, or B2B lead data — that is Sarah's role.\n- If unsure, suggest emailing info@roseempire.co.uk or calling +44 7999 988450.\n- Never invent certifications, stock levels, or prices not listed above."
}

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
