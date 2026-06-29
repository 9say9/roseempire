"""Verify AI router forwards Roo-style tool calls (not text-only JSON)."""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

ROUTER_PORTS = (8001, 8000)

TOOLS_BODY = {
    "model": "gpt-3.5-turbo",
    "stream": False,
    "messages": [
        {
            "role": "user",
            "content": "Use the update_todo_list tool to add one todo: Test router tools",
        }
    ],
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "update_todo_list",
                "description": "Update the task todo list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "todos": {"type": "string", "description": "Markdown todo list"},
                    },
                    "required": ["todos"],
                },
            },
        }
    ],
    "tool_choice": "required",
}


def find_router() -> tuple[str, dict]:
    for port in ROUTER_PORTS:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=5) as resp:
                info = json.loads(resp.read().decode("utf-8"))
                return f"http://127.0.0.1:{port}/v1/chat/completions", info
        except Exception:
            continue
    raise RuntimeError("No router on ports 8001 or 8000 — run restart_ai_router.bat")


def post(url: str, body: dict) -> dict:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    print("Rose Empire — Roo tool-call router test\n")
    try:
        router, info = find_router()
    except RuntimeError as exc:
        print(f"  FAIL: {exc}")
        return 1

    print(f"  Router: {router}")
    print(f"  tools_passthrough: {info.get('tools_passthrough', False)}")
    print(f"  cloud deployments: {info.get('cloud_keys', 0)}")
    if not info.get("tools_passthrough"):
        print("\n  FAIL: Old router on port 8000 — run restart_ai_router.bat")
        return 1

    try:
        result = post(router, TOOLS_BODY)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")[:400]
        print(f"  FAIL: HTTP {exc.code} — {body}")
        if "cooldown" in body.lower() or "no deployments" in body.lower():
            print("  Fix: restart_ai_router.bat (clears cooldowns)")
        return 1

    choice = (result.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    tool_calls = message.get("tool_calls") or []
    content = (message.get("content") or "").strip()

    if tool_calls:
        fn = tool_calls[0].get("function") or {}
        print(f"  OK: Native tool_calls returned — {fn.get('name', '?')}")
        return 0

    if "update_todo_list" in content and content.startswith("{"):
        print("  FAIL: Model returned tool JSON as plain text (Roo will break).")
        print("  Fix: restart router; ensure GEMINI_API_KEY in .env; disable Ollama-only routing.")
        print(f"  Sample: {content[:200]}")
        return 1

    print(f"  WARN: No tool_calls in response. Content: {content[:200] or '(empty)'}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
