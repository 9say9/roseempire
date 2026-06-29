# AI Router — traffic controller (Code mode)

Roo must use the **local LiteLLM router**, not direct cloud APIs.

| Setting | Value |
|---------|--------|
| Provider | OpenAI Compatible |
| Base URL | `http://127.0.0.1:8001/v1` (or `8000` if free — run `restart_ai_router.bat`) |
| Model | `gpt-3.5-turbo` or `gemini-free` (same pool) |
| API key | `local` (any placeholder) |

**NOT** `http://127.0.0.1:11434/v1` — that is Ollama, not the router.

Before long sessions: `restart_ai_router.bat` (clears cooldowns; cloud keys rotate; Ollama is free fallback).

**Roo tool calls:** Router forwards `tools` / `tool_choice` to Gemini/Groq. Ollama 1.5b cannot run Roo tools — if you see JSON text instead of actions, restart `restart_ai_router.bat` and ensure Gemini keys are in `.env`.

**Business knowledge** (MOQ, pitches, catalog): NotebookLM MCP — not the router.

**Terminal bots**: Sarah/James/Adeel use `fleet_ai.py` with `AI_ROUTER_URL` when router is healthy.
