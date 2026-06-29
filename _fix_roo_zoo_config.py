"""Fix Roo Code and Zoo Code Ollama settings in Cursor (fully automated)."""
from __future__ import annotations

import base64
import json
import shutil
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

DB_CANDIDATES = [
    Path.home() / "AppData/Roaming/Code/User/globalStorage/state.vscdb",
    Path.home() / "AppData/Roaming/Cursor/User/globalStorage/state.vscdb",
    Path.home() / "AppData/Roaming/Code - Insiders/User/globalStorage/state.vscdb",
    Path.home() / "AppData/Local/Programs/Microsoft VS Code/User/globalStorage/state.vscdb",
]
LOCAL_STATE_CANDIDATES = [
    Path.home() / "AppData/Roaming/Code/Local State",
    Path.home() / "AppData/Roaming/Cursor/Local State",
    Path.home() / "AppData/Roaming/Code - Insiders/Local State",
    Path.home() / "AppData/Local/Programs/Microsoft VS Code/User/Local State",
]
SETTINGS_FILE = Path(__file__).resolve().parent / "roo-ollama-settings.json"
OLLAMA_URL = "http://127.0.0.1:11434"
MODEL = "qwen2.5-coder:1.5b"
PROFILE_NAME = "default"


def sanitize_ollama_url(url: str | None) -> str:
    """Fix corrupted URLs like D:\\roseempire\\http:\\127.0.0.1:11434."""
    if not url:
        return OLLAMA_URL
    if "127.0.0.1:11434" in url or "localhost:11434" in url:
        return OLLAMA_URL
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return OLLAMA_URL

ROO_STATE_KEY = "RooVeterinaryInc.roo-cline"
ZOO_STATE_KEY = "ZooCodeOrganization.zoo-code"
ROO_SECRET_KEY = (
    'secret://{"extensionId":"rooveterinaryinc.roo-cline","key":"roo_cline_config_api_config"}'
)
ZOO_SECRET_KEY = (
    'secret://{"extensionId":"zoocodeorganization.zoo-code","key":"roo_cline_config_api_config"}'
)


def build_default_profile() -> dict:
    return {
        "id": "local-ollama-default",
        "apiProvider": "ollama",
        "ollamaBaseUrl": OLLAMA_URL,
        "ollamaModelId": MODEL,
    }


def build_profiles_blob() -> dict:
    cfg = build_default_profile()
    return {
        "currentApiConfigName": PROFILE_NAME,
        "apiConfigs": {PROFILE_NAME: cfg},
        "modeApiConfigs": {},
        "pinnedApiConfigs": {},
    }


def build_list_api_config_meta() -> list[dict]:
    cfg = build_default_profile()
    return [{"name": PROFILE_NAME, "id": cfg["id"], "apiProvider": "ollama"}]


def patch_global_state(state: dict) -> dict:
    cfg = build_default_profile()
    state["currentApiConfigName"] = PROFILE_NAME
    state["apiProvider"] = "ollama"
    state["ollamaBaseUrl"] = sanitize_ollama_url(state.get("ollamaBaseUrl"))
    state["ollamaModelId"] = MODEL
    state["listApiConfigMeta"] = build_list_api_config_meta()

    for key in list(state.keys()):
        if key.startswith("qwen") and key != "ollamaModelId":
            state.pop(key, None)
        if key.startswith("openAi") or key in ("apiModelId", "openRouterModelId"):
            state.pop(key, None)
        if key.endswith("BaseUrl") and key != "ollamaBaseUrl":
            state.pop(key, None)
        if key.endswith("ModelId") and key not in ("ollamaModelId",):
            state.pop(key, None)
    return state


def get_chrome_aes_key() -> bytes | None:
    try:
        import win32crypt  # type: ignore
    except ImportError:
        return None

    for local_state_path in LOCAL_STATE_CANDIDATES:
        if not local_state_path.exists():
            continue
        try:
            local_state = json.loads(local_state_path.read_text(encoding="utf-8"))
            encrypted_key_b64 = local_state["os_crypt"]["encrypted_key"]
            encrypted_key = base64.b64decode(encrypted_key_b64)
            if encrypted_key[:5] != b"DPAPI":
                continue
            return win32crypt.CryptUnprotectData(encrypted_key[5:], None, None, None, 0)[1]
        except Exception:
            continue
    return None


def decrypt_cursor_secret(raw: str) -> dict | None:
    aes_key = get_chrome_aes_key()
    if aes_key is None:
        return None
    try:
        from Cryptodome.Cipher import AES  # type: ignore
    except ImportError:
        try:
            from Crypto.Cipher import AES  # type: ignore
        except ImportError:
            return None

    try:
        payload = json.loads(raw)
        if payload.get("type") != "Buffer":
            return None
        data = bytes(payload["data"])
        if data[:3] != b"v10":
            return None
        nonce = data[3:15]
        ciphertext = data[15:-16]
        tag = data[-16:]
        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return json.loads(plaintext.decode("utf-8"))
    except Exception:
        return None


def encrypt_cursor_secret(data: dict) -> str | None:
    aes_key = get_chrome_aes_key()
    if aes_key is None:
        return None
    try:
        from Cryptodome.Cipher import AES  # type: ignore
    except ImportError:
        try:
            from Crypto.Cipher import AES  # type: ignore
        except ImportError:
            return None

    try:
        import os

        nonce = os.urandom(12)
        plaintext = json.dumps(data, separators=(",", ":")).encode("utf-8")
        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        blob = b"v10" + nonce + ciphertext + tag
        return json.dumps({"type": "Buffer", "data": list(blob)})
    except Exception:
        return None


def patch_secret_profiles(existing: dict | None) -> dict:
    profiles = build_profiles_blob()
    patched = existing or {}
    patched["currentApiConfigName"] = PROFILE_NAME
    patched["apiConfigs"] = {PROFILE_NAME: build_default_profile()}
    patched["modeApiConfigs"] = patched.get("modeApiConfigs") or {}
    patched["pinnedApiConfigs"] = patched.get("pinnedApiConfigs") or {}
    return patched


def restore_secret_from_backup(cur, secret_key: str, db_path: Path | None = None) -> str | None:
    backup_dir = (db_path or DB_CANDIDATES[0]).parent
    backups = sorted(backup_dir.glob("state.vscdb.bak-*"), reverse=True)
    for backup in backups:
        try:
            bconn = sqlite3.connect(backup)
            bcur = bconn.cursor()
            bcur.execute("SELECT value FROM ItemTable WHERE key=?", (secret_key,))
            row = bcur.fetchone()
            bconn.close()
            if row and row[0]:
                cur.execute(
                    "INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)",
                    (secret_key, row[0]),
                )
                return backup.name
        except Exception:
            continue
    return None


def restart_ollama_and_warm() -> bool:
    ollama = Path.home() / "AppData/Local/Programs/Ollama/ollama.exe"
    if not ollama.exists():
        print("WARN: Ollama not installed")
        return False

    subprocess.run(
        ["taskkill", "/IM", "ollama.exe", "/F"],
        capture_output=True,
    )
    time.sleep(2)
    subprocess.Popen(
        [str(Path.home() / "AppData/Local/Programs/Ollama/Ollama.exe")],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(4)

    for model in ("qwen2.5-coder:1.5b-zoo", "gemma4:31b-cloud"):
        subprocess.run([str(ollama), "stop", model], capture_output=True)

    payload = json.dumps(
        {
            "model": MODEL,
            "prompt": "OK",
            "stream": False,
            "keep_alive": "1h",
            "options": {"num_predict": 3},
        }
    ).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            resp.read()
        print(f"Ollama warm-up OK ({MODEL})")
        return True
    except urllib.error.HTTPError as exc:
        print(f"WARN: Ollama warm-up failed: HTTP {exc.code}")
        return False
    except Exception as exc:
        print(f"WARN: Ollama warm-up failed: {exc}")
        return False


def main() -> int:
    db_paths = [p for p in DB_CANDIDATES if p.exists()]
    if not db_paths:
        print("ERROR: No VS Code/Cursor state DB found")
        return 1

    secret_fixed = 0
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
            print(f"Patched global state: {state_key} in {DB}")

        for secret_key in (ROO_SECRET_KEY, ZOO_SECRET_KEY):
            cur.execute("SELECT value FROM ItemTable WHERE key=?", (secret_key,))
            row = cur.fetchone()
            existing_raw = row[0] if row else None
            existing = decrypt_cursor_secret(existing_raw) if existing_raw else None

            if existing is None:
                restored = restore_secret_from_backup(cur, secret_key, DB)
                if restored:
                    print(f"Restored secret from {restored}: {secret_key}")
                    cur.execute("SELECT value FROM ItemTable WHERE key=?", (secret_key,))
                    row = cur.fetchone()
                    existing_raw = row[0] if row else None
                    existing = decrypt_cursor_secret(existing_raw) if existing_raw else None

            patched = patch_secret_profiles(existing)
            encrypted = encrypt_cursor_secret(patched)
            if encrypted:
                cur.execute(
                    "INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)",
                    (secret_key, encrypted),
                )
                secret_fixed += 1
                print(f"Patched secret profiles: {secret_key} in {DB}")
            else:
                print(f"WARN: could not write secret for {secret_key} in {DB}")

        conn.commit()
        conn.close()

    restart_ollama_and_warm()

    print()
    print("FIXED:")
    print(f"  Profile: {PROFILE_NAME}")
    print(f"  Provider: ollama")
    print(f"  URL: {OLLAMA_URL}")
    print(f"  Model: {MODEL}")
    print(f"  Secrets written: {secret_fixed}/2")
    print()
    print("Now close Cursor completely, reopen it, and send a NEW message in Roo/Zoo.")
    return 0 if secret_fixed >= 2 else 1


if __name__ == "__main__":
    raise SystemExit(main())
