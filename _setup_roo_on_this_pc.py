"""Configure Roo + Zoo on this PC: correct folder paths, AI router, no broken imports."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
ROUTER_SETTINGS = REPO / "roo-router-settings.json"
OLLAMA_SETTINGS = REPO / "roo-ollama-settings.json"
CURSOR_SETTINGS = Path.home() / "AppData/Roaming/Cursor/User/settings.json"


def patch_cursor_settings() -> None:
    """Stop Roo from importing broken paths from old PC (D:\\ai\\antigravity\\...)."""
    import_path = str(ROUTER_SETTINGS).replace("\\", "\\\\")
    data: dict = {}
    if CURSOR_SETTINGS.exists():
        data = json.loads(CURSOR_SETTINGS.read_text(encoding="utf-8"))

    data["roo-cline.autoImportSettingsPath"] = str(ROUTER_SETTINGS)
    data["zoo-code.autoImportSettingsPath"] = str(ROUTER_SETTINGS)
    CURSOR_SETTINGS.parent.mkdir(parents=True, exist_ok=True)
    CURSOR_SETTINGS.write_text(json.dumps(data, indent=4) + "\n", encoding="utf-8")
    print(f"Cursor settings: autoImport -> {ROUTER_SETTINGS}")


def main() -> int:
    print(f"Repo folder: {REPO}")
    if not ROUTER_SETTINGS.exists():
        print(f"ERROR: missing {ROUTER_SETTINGS}")
        return 1

    patch_cursor_settings()

    # Patch Roo/Zoo DB (needs Cursor closed for best results)
    fix_router = REPO / "_fix_roo_router_config.py"
    fix_ollama = REPO / "_fix_roo_zoo_config.py"
    if fix_router.exists():
        rc = subprocess.call([sys.executable, str(fix_router)])
        if rc != 0 and fix_ollama.exists():
            print("Router patch partial — trying Ollama fallback patch...")
            subprocess.call([sys.executable, str(fix_ollama)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
