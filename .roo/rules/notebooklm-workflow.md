# NotebookLM + Roo Code workflow

## When to use NotebookLM
Use NotebookLM MCP for **business knowledge** grounded in your uploaded sources:
- Product specs, MOQ, pricing, catalog positioning
- Outreach strategy, sector pain points, compliance talking points
- Bot workflow reminders (Sarah / James / Adeel)

Use **AI Router** (`http://127.0.0.1:8000/v1`) or **Ollama** for **writing code** and running terminal commands.

## Setup (once per PC)
```bat
setup_notebooklm.bat
```
Then upload `notebooklm/rose-empire-knowledge-pack.md` to a NotebookLM notebook named **Rose Empire B2B**.

## Roo prompts
- "List my NotebookLM notebooks and query Rose Empire B2B about Terry protector MOQ."
- "Using NotebookLM sources, draft 3 bullet value props for UK care homes."
- "Before sending emails, ask NotebookLM what compliance points to mention for hotels."

## Refresh knowledge after repo changes
```bat
py -3 scripts\build_notebooklm_bundle.py
```
Re-upload the new `notebooklm/rose-empire-knowledge-pack.md` to NotebookLM (or add as new source).

## MCP
Project config: `.cursor/mcp.json` → `notebooklm` server via `npx notebooklm-mcp@latest`.
Enable in Cursor: **Settings → Tools → MCP** (must show green for notebooklm).
