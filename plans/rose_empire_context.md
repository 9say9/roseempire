# 🌹 Rose Empire Business & Automation Context

## 🏢 Business Overview
- **Company:** Rose Empire
- **Website:** [roseempire.co.uk](https://roseempire.co.uk)
- **Core Products:**
  - Mattress Protectors
  - Goose Feather Pillows
  - Duck Down Pillows
- **Primary Goal:** Generate B2B sales.
- **Target Audience:** Hospitality sector (Hotels, Care Homes, etc.).

## 🤖 Automation Fleet (The 3 Bots)
The system is a fully integrated B2B lead generation and outreach engine.

### 1. Sarah (The Scraper)
- **Role:** Multi-source lead discovery.
- **Sources:** Google Maps, Google Web, LinkedIn (Public), Reddit, Facebook (Beta), Instagram (Beta).
- **Key File:** `fleet_scraper.py`, `sarah_sources.py`
- **Output:** `linkedin-outreach/sarah_multi_source_leads.csv`

### 2. James (The AI Copywriter)
- **Role:** Generating personalized email pitches and LinkedIn drafts.
- **Key File:** `fleet_ai.py`
- **AI Stack:** Local Ollama (qwen2.5-coder:7b) or AI Router.

### 3. Adeel (The Pipeline Manager)
- **Role:** Lead qualification, merging, and deduplication.
- **Key File:** `lead_pipeline.py`, `lead_validation.py`
- **Output:** `outreach_master.csv`

## 🛠️ Technical Infrastructure
- **Orchestrator:** `fleet_orchestrator.py` (Single entry point for testing/running).
- **CRM/Dashboard:** `app.py` (Accessible at http://127.0.0.1:5050).
- **Outreach:** `send_leads_emails.py` (M365 integration).
- **Knowledge Base:** NotebookLM (contains catalog, MOQ, and playbook).
- **Data Storage:** All lead data is stored locally in `linkedin-outreach/` (gitignored).

## 🔄 Workflow Loop
`Scrape (Sarah)` → `Qualify/Merge (Adeel)` → `Draft Copy (James)` → `Review/Send (Email Agent)`

## 📌 Session Persistence Note
This file serves as the primary context for all future interactions. Any changes to the bot logic, business strategy, or project state should be reflected here.
