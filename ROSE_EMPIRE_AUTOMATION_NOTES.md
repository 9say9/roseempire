# Rose Empire automation note

## What this project is
- 3-bot fleet for Rose Empire lead generation and outreach.
- Sarah scrapes leads from Google/LinkedIn/web/Reddit and writes a CSV.
- James drafts outreach copy using the local AI stack.
- Adeel qualifies and merges lead data into outreach-ready CSVs.

## Main repo files
- [AGENTS.md](AGENTS.md)
- [fleet_scraper.py](fleet_scraper.py)
- [sarah_sources.py](sarah_sources.py)
- [fleet_ai.py](fleet_ai.py)
- [lead_pipeline.py](lead_pipeline.py)
- [send_leads_emails.py](send_leads_emails.py)
- [run_outreach_pipeline.bat](run_outreach_pipeline.bat)
- [run_ai_fleet.bat](run_ai_fleet.bat)

## Current setup notes
- The project already contains the workflow, scripts, batch runners, and the main output folder [linkedin-outreach](linkedin-outreach).
- The AI layer is designed to work without paid tokens by preferring Ollama or the local router.
- The environment file template is [.env.example](.env.example). Keep real credentials only in the local `.env` file and never commit it.

## C: drive search result
- I searched the common Windows locations for extra Rose Empire folders or related bot files.
- No additional Rose Empire project copy was found on the C drive in the locations checked.

## Offline / zero-token plan
1. Keep the AI provider on local mode.
   - Set `AI_PROVIDER=auto` or `AI_PROVIDER=ollama` in the local `.env`.
   - Leave `OPENAI_API_KEY` and `GEMINI_API_KEY` blank unless you explicitly want paid cloud usage.
2. Run local services first.
   - Start Ollama with [start_ollama.bat](start_ollama.bat).
   - If the router is needed, use [start_ai_router.bat](start_ai_router.bat).
3. Use the one-click launcher.
   - Run [run_local_fleet.bat](run_local_fleet.bat) for the full local workflow.
   - For a quick check, use `run_local_fleet.bat --check-only`.
4. Run the fleet in order.
   - Sarah: `py -3 fleet_scraper.py --limit 10 --mission "care homes Manchester UK"`
   - Adeel: `py -3 lead_pipeline.py --qualify --export-outreach`
   - James: `py -3 fleet_ai.py --agent james "Hotel Name Manchester"`
   - Email dry run: `py -3 send_leads_emails.py --dry-run --limit 5`
5. Keep outreach safe and cheap.
   - Use `--dry-run` until the lead list looks correct.
   - Only switch to real sends after the dry run passes.

## Recommended automation routine
- Daily scrape: Sarah collects leads.
- Daily qualify: Adeel cleans and scores them.
- Daily draft: James creates email copy.
- Weekly/controlled send: run the email sender only after review.

## Best way to make it reliable
- Prefer local Ollama models and keep the router as a fallback, not the primary path.
- Use the existing CSV files in [linkedin-outreach](linkedin-outreach) as the source of truth.
- Keep the workflow simple: scrape -> qualify -> draft -> review -> send.
