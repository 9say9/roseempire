"""Rose Empire AI bot — local chat via Ollama with full project knowledge."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

OLLAMA_GENERATE_URL = os.getenv("OLLAMA_GENERATE_URL", "http://127.0.0.1:11434/api/generate")
OLLAMA_CHAT_URL = os.getenv("OLLAMA_API_URL", "http://127.0.0.1:11434/api/chat")
MODELS = ["qwen2.5-coder:1.5b", "gemma3:4b", "qwen2.5-coder:7b"]
REQUEST_TIMEOUT_SEC = 120
KNOWLEDGE_DIR = Path(r"C:\Users\ADLSH\.continue\knowledge")
RULES_PATH = Path(r"C:\Users\ADLSH\.continue\rules\rose-empire-agent.md")
PROJECT_ROOT = Path(__file__).resolve().parent

KNOWLEDGE_FILES = [
    "rose-empire-business.md",
    "rose-empire-pricing.md",
    "rose-empire-website.md",
    "rose-empire-deploy-dns.md",
    "rose-empire-linkedin-sales.md",
    "rose-empire-status.md",
]


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3 :].lstrip()
    return text.strip()


def load_knowledge_file(path: Path, limit: int = 1200) -> str:
    if not path.is_file():
        return ""
    return strip_frontmatter(path.read_text(encoding="utf-8"))[:limit]


def load_system_prompt() -> str:
    if RULES_PATH.is_file():
        parts = [strip_frontmatter(RULES_PATH.read_text(encoding="utf-8"))[:2000]]
    else:
        parts = ["You are the Rose Empire wholesale bedding AI assistant."]

    parts.append(f"\n\n# PROJECT ROOT\n{PROJECT_ROOT}\n")

    for name in KNOWLEDGE_FILES:
        content = load_knowledge_file(KNOWLEDGE_DIR / name)
        if content:
            parts.append(f"\n\n# KNOWLEDGE: {name}\n{content}")

    parts.append("\n\nAnswer from Rose Empire context. Be direct and B2B-savvy.")
    return "".join(parts)[:6500]


def ollama_online() -> bool:
    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def _post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SEC) as resp:
        return json.loads(resp.read().decode("utf-8"))


def generate_reply(system_prompt: str, user_input: str, history: list[tuple[str, str]]) -> str:
    history_block = ""
    for user, assistant in history[-4:]:
        history_block += f"\nUser: {user}\nAssistant: {assistant}\n"

    prompt = (
        f"{system_prompt}\n\n"
        f"{history_block}\n"
        f"User: {user_input}\n"
        "Assistant:"
    )

    last_error = ""
    for model in MODELS:
        try:
            data = _post_json(
                OLLAMA_GENERATE_URL,
                {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "keep_alive": "3600s",
                    "options": {"temperature": 0.35, "num_predict": 512},
                },
            )
            text = (data.get("response") or "").strip()
            if text:
                return text
            last_error = f"Empty response from {model}"
        except urllib.error.URLError as exc:
            last_error = str(getattr(exc, "reason", exc))
            continue
        except Exception as exc:
            last_error = str(exc)
            continue

    raise SystemExit(
        f"Ollama could not reply. Last error: {last_error}\n"
        "Run start_ollama.bat and wait for 'Ollama API: ONLINE'."
    )


def run_interactive() -> None:
    if not ollama_online():
        raise SystemExit("Ollama is offline. Run start_ollama.bat first.")

    system_prompt = load_system_prompt()
    kb_count = sum(1 for n in KNOWLEDGE_FILES if (KNOWLEDGE_DIR / n).is_file())
    history: list[tuple[str, str]] = []

    print()
    print("Rose Empire AI (Ollama + knowledge base)")
    print("=" * 50)
    print(f"Knowledge files loaded: {kb_count}/{len(KNOWLEDGE_FILES)}")
    print(f"Models: {', '.join(MODELS)}")
    print("Commands: exit | quit | /clear | /status")
    print()

    while True:
        try:
            user_input = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Bye.")
            break
        if user_input.lower() == "/clear":
            history.clear()
            print("Chat cleared.")
            continue
        if user_input.lower() == "/status":
            print("Live site: https://www.roseempire.co.uk")
            print("Fleet dashboard: http://127.0.0.1:5050 (run_ai_fleet.bat)")
            print("MOQ: 20 | Discounts: 10% at 50+, 20% at 200+")
            print("Leads: linkedin-outreach/manchester_textile_leads.csv")
            continue

        print("Rose Empire> ", end="", flush=True)
        reply = generate_reply(system_prompt, user_input, history)
        print(reply)
        print()
        history.append((user_input, reply))


def run_test(prompt: str) -> None:
    if not ollama_online():
        raise SystemExit("Ollama is offline. Run start_ollama.bat first.")
    print(generate_reply(load_system_prompt(), prompt, []))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_test(
            sys.argv[2]
            if len(sys.argv) > 2
            else "What is our MOQ, live website URL, and top 3 things left to do?"
        )
    else:
        run_interactive()
