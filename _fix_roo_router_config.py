"""Point Roo Code + Zoo Code at the local AI Router (OpenAI-compatible)."""
from __future__ import annotations

import json
import os
import shutil
import sqlite3
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

# Reuse crypto helpers from the Ollama fixer
from _fix_roo_zoo_config import (
    ROO_SECRET_KEY,
    ROO_STATE_KEY,
    ZOO_SECRET_KEY,
    ZOO_STATE_KEY,
    decrypt_cursor_secret,
    encrypt_cursor_secret,
    restore_secret_from_backup,
)

DB_CANDIDATES = [
    Path.home() / "AppData/Roaming/Code/User/globalStorage/state.vscdb",
    Path.home() / "AppData/Roaming/Cursor/User/globalStorage/state.vscdb",
    Path.home() / "AppData/Roaming/Code - Insiders/User/globalStorage/state.vscdb",
    Path.home() / "AppData/Local/Programs/Microsoft VS Code/User/globalStorage/state.vscdb",
]

ROUTER_MODEL = os.getenv("AI_ROUTER_MODEL", "boss-model")
PROFILE_NAME = "rose-router"
PROFILE_ID = "rose-router-local"
ROO_MODE_SLUGS = ("code", "architect", "ask", "debug", "orchestrator")


def detect_router_url() -> str:
    env_url = os.getenv("AI_ROUTER_URL", "").strip().rstrip("/")
    if env_url:
        return env_url if env_url.endswith("/v1") else f"{env_url}/v1"

    for port in (8001, 8000):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=3) as resp:
                info = json.loads(resp.read().decode("utf-8"))
                if info.get("tools_passthrough"):
                    return f"http://127.0.0.1:{port}/v1"
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            continue

    return "http://127.0.0.1:8001/v1"


ROUTER_URL = detect_router_url()


def build_router_profile() -> dict:
    return {
        "id": PROFILE_ID,
        "apiProvider": "openai",
        "openAiBaseUrl": ROUTER_URL,
        "openAiApiKey": "local",
        "openAiModelId": ROUTER_MODEL,
        "apiModelId": ROUTER_MODEL,
        "openAiStreamingEnabled": False,
    }


def build_mode_api_configs() -> dict[str, str]:
    return {slug: PROFILE_ID for slug in ROO_MODE_SLUGS}


def patch_global_state(state: dict) -> dict:
    cfg = build_router_profile()
    provider_profiles = {
        "currentApiConfigName": PROFILE_NAME,
        "apiConfigs": {PROFILE_NAME: cfg},
        "modeApiConfigs": build_mode_api_configs(),
        "pinnedApiConfigs": {PROFILE_ID: True},
    }

    state["currentApiConfigName"] = PROFILE_NAME
    state["apiProvider"] = "openai"
    state["openAiBaseUrl"] = ROUTER_URL
    state["openAiApiKey"] = "local"
    state["openAiModelId"] = ROUTER_MODEL
    state["apiModelId"] = ROUTER_MODEL
    state["providerProfiles"] = provider_profiles
    state["listApiConfigMeta"] = [
        {"name": PROFILE_NAME, "id": cfg["id"], "apiProvider": "openai", "modelId": ROUTER_MODEL}
    ]
    for key in list(state.keys()):
        if key.startswith("ollama") or key.startswith("qwen"):
            state.pop(key, None)
        if key.startswith("openAi") or key in ("apiModelId", "openRouterModelId"):
            state.pop(key, None)
        if key.endswith("BaseUrl") and key != "openAiBaseUrl":
            state.pop(key, None)
        if key.endswith("ModelId") and key not in ("openAiModelId", "apiModelId"):
            state.pop(key, None)
    return state


def patch_secret_profiles(existing: dict | None) -> dict:
    patched = dict(existing or {})
    patched["currentApiConfigName"] = PROFILE_NAME
    patched["apiConfigs"] = {PROFILE_NAME: build_router_profile()}
    patched["modeApiConfigs"] = build_mode_api_configs()
    patched["pinnedApiConfigs"] = {PROFILE_ID: True}
    patched["providerProfiles"] = {
        "currentApiConfigName": PROFILE_NAME,
        "apiConfigs": {PROFILE_NAME: build_router_profile()},
        "modeApiConfigs": build_mode_api_configs(),
        "pinnedApiConfigs": {PROFILE_ID: True},
    }
    return patched


def sync_router_settings_json() -> None:
    settings_path = Path(__file__).resolve().parent / "roo-router-settings.json"
    payload = {
        "providerProfiles": {
            "currentApiConfigName": PROFILE_NAME,
            "apiConfigs": {PROFILE_NAME: build_router_profile()},
            "modeApiConfigs": build_mode_api_configs(),
            "pinnedApiConfigs": {PROFILE_ID: True},
        }
    }
    settings_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    global ROUTER_URL
    ROUTER_URL = detect_router_url()
    sync_router_settings_json()

    db_paths = [p for p in DB_CANDIDATES if p.exists()]
    if not db_paths:
        print("ERROR: No VS Code/Cursor state DB found")
        return 1

    fixed_total = 0
    for DB in db_paths:
        backup = DB.with_name(f"state.vscdb.bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        shutil.copy2(DB, backup)
        print(f"Backup: {backup}")

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        for state_key in (ROO_STATE_KEY, ZOO_STATE_KEY):
            cur.execute("SELECT value FROM ItemTable WHERE key=?", (state_key,))
            row = cur.fetchone()
            if not row:
                print(f"WARN: missing {state_key} in {DB}")
                continue
            state = patch_global_state(json.loads(row[0]))
            cur.execute(
                "UPDATE ItemTable SET value=? WHERE key=?",
                (json.dumps(state, separators=(",", ":")), state_key),
            )
            print(f"Patched: {state_key} in {DB}")

        fixed = 0
        for secret_key in (ROO_SECRET_KEY, ZOO_SECRET_KEY):
            cur.execute("SELECT value FROM ItemTable WHERE key=?", (secret_key,))
            row = cur.fetchone()
            existing_raw = row[0] if row else None
            existing = decrypt_cursor_secret(existing_raw) if existing_raw else None
            if existing is None:
                restore_secret_from_backup(cur, secret_key)
                cur.execute("SELECT value FROM ItemTable WHERE key=?", (secret_key,))
                row = cur.fetchone()
                existing_raw = row[0] if row else None
                existing = decrypt_cursor_secret(existing_raw) if existing_raw else None
            encrypted = encrypt_cursor_secret(patch_secret_profiles(existing))
            if encrypted:
                cur.execute(
                    "INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)",
                    (secret_key, encrypted),
                )
                fixed += 1

        conn.commit()
        conn.close()
        fixed_total += fixed

    print()
    print("Roo/Zoo -> AI Router")
    print(f"  URL:   {ROUTER_URL}")
    print(f"  Model: {ROUTER_MODEL}")
    print(f"  DBs patched: {len(db_paths)}")
    print(f"  Secrets: {fixed_total}/2")
    print("Close VS Code/Cursor fully, reopen, run restart_ai_router.bat first.")
    return 0 if fixed_total >= 2 else 1


if __name__ == "__main__":
    raise SystemExit(main())
