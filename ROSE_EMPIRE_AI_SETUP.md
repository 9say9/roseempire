# Rose Empire AI Setup (Ollama + VS Code + Cloud Models)

Your Rose Empire AI stack is configured. **Ollama is installed** but had **no models** — the setup script downloads them.

---

## What was created

| File | Purpose |
|------|---------|
| `C:\Users\ADLSH\.continue\config.yaml` | All models + Rose Empire agent rules |
| `C:\Users\ADLSH\.continue\rules\rose-empire-agent.md` | Business partner system prompt |
| `setup_rose_empire_ai.bat` | Download Ollama models (run once) |
| `antigravity.code-workspace` | Open project in VS Code with Continue |

---

## Step 1 — Download local models (required)

Double-click:

```
Documents\antigravity\setup_rose_empire_ai.bat
```

This pulls:
- **qwen2.5-coder:7b** — main coding brain (stronger than Llama 3.1 for code)
- **qwen2.5-coder:1.5b** — fast tab autocomplete
- **llama3.1:8b** — backup chat model

First run takes 10–30 minutes (large downloads).

---

## Step 2 — VS Code + Continue extension

1. Open **VS Code** (not Cursor for this stack)
2. Extensions → search **Continue** → install **Continue.continue**
3. File → Open Workspace → `Documents\antigravity\antigravity.code-workspace`
4. Open **Continue** sidebar (left panel)
5. At top of Continue chat, change dropdown from **Default Assistant** → **Rose Empire AI Stack**
6. Click **Reload config** if models don’t appear

---

## Step 3 — Cloud API keys (Claude, Gemini, ChatGPT)

You **cannot download Claude/GPT/Gemini locally** — they need API keys:

| Model | Get key from |
|-------|----------------|
| Claude | https://console.anthropic.com/ |
| Gemini | https://aistudio.google.com/apikey |
| ChatGPT | https://platform.openai.com/api-keys |

In VS Code Continue sidebar:
1. Click **gear** (settings)
2. Go to **Secrets**
3. Add:
   - `ANTHROPIC_API_KEY`
   - `GEMINI_API_KEY`
   - `OPENAI_API_KEY`

Template: `C:\Users\ADLSH\.continue\secrets.example.json` (do not commit real keys)

---

## Step 4 — How to use

| Task | How |
|------|-----|
| Fix code | Highlight code → **Ctrl+I** → type instruction |
| Chat | Continue sidebar → pick model → type question |
| Fast autocomplete | **Qwen 1.5B** runs as you type (Tab to accept) |
| Best local coding | **Qwen2.5 Coder 7B** |
| Hardest tasks | **Claude 3.5 Sonnet** (needs API key) |
| Free cloud | **Gemini 1.5 Flash** (needs API key) |
| Cheap cloud | **ChatGPT 4o mini** (needs API key) |

**Slash commands** in Continue chat:
- `/audit-site` — scan website for issues
- `/linkedin-lead` — draft B2B outreach
- `/deploy-zip` — Netlify deploy checklist

---

## Cursor vs VS Code

| Tool | Use for |
|------|---------|
| **Cursor** (what you use now) | Built-in Agent — already has Claude/GPT via Cursor subscription |
| **VS Code + Continue + Ollama** | Free unlimited local AI, your custom Rose Empire prompt |

Both can work — Cursor for heavy agent tasks, VS Code+Ollama for free offline coding.

---

## Troubleshooting

**"Ollama not found" in terminal**
- Ollama is at: `C:\Users\ADLSH\AppData\Local\Programs\Ollama\ollama.exe`
- Run `setup_rose_empire_ai.bat` (uses full path)

**"No models configured" in Continue**
- Select **Rose Empire AI Stack** config (not Default Assistant)
- Reload config
- Run `setup_rose_empire_ai.bat` if models list is empty

**Local model very slow first reply**
- Normal on CPU — wait 30–60 seconds first time
- Model stays loaded for 1 hour after first use

**Claude/Gemini/GPT not in dropdown**
- Add API keys in Continue Secrets first

---

## Security

- Never paste real API keys in chat or commit them to git
- Use Continue Secrets only
- The JSON you shared with `YOUR_GEMINI_API_KEY` placeholders is correct — replace in Secrets UI
