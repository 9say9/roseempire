"""Register Rose Empire B2B notebook in NotebookLM MCP local library."""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

LIBRARY = Path.home() / "AppData/Local/notebooklm-mcp/Data/library.json"
NAME = "Rose Empire B2B"


def slug(name: str, existing: set[str]) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:30]
    sid = base or "notebook"
    n = 1
    while sid in existing:
        sid = f"{base}-{n}"
        n += 1
    return sid


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: py -3 scripts/register_notebooklm_notebook.py <notebooklm-url>")
        print("Example URL: https://notebooklm.google.com/notebook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        return 1

    url = sys.argv[1].strip()
    if "notebooklm.google.com" not in url:
        print("ERROR: Paste the full URL from your browser when viewing the notebook.")
        return 1

    LIBRARY.parent.mkdir(parents=True, exist_ok=True)
    if LIBRARY.is_file():
        lib = json.loads(LIBRARY.read_text(encoding="utf-8"))
    else:
        lib = {
            "notebooks": [],
            "active_notebook_id": None,
            "last_modified": "",
            "version": "1.0.0",
        }

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    existing_ids = {n["id"] for n in lib.get("notebooks", [])}
    for nb in lib.get("notebooks", []):
        if nb.get("url") == url:
            lib["active_notebook_id"] = nb["id"]
            lib["last_modified"] = now
            LIBRARY.write_text(json.dumps(lib, indent=2), encoding="utf-8")
            print(f"Already registered. Active notebook: {nb['id']}")
            return 0

    nb_id = slug(NAME, existing_ids)
    entry = {
        "id": nb_id,
        "url": url,
        "name": NAME,
        "description": "Rose Empire wholesale mattress protectors — catalog, MOQ, bots, outreach workflow",
        "topics": ["mattress protectors", "B2B wholesale", "care homes", "hotels", "outreach"],
        "content_types": ["documentation", "catalog", "workflow"],
        "use_cases": [
            "Product MOQ and pricing questions",
            "Cold email angles for care homes and hotels",
            "Sarah/James/Adeel bot workflow",
        ],
        "added_at": now,
        "last_used": now,
        "use_count": 0,
        "tags": ["rose-empire"],
    }
    lib.setdefault("notebooks", []).append(entry)
    lib["active_notebook_id"] = nb_id
    lib["last_modified"] = now
    lib["version"] = "1.0.0"
    LIBRARY.write_text(json.dumps(lib, indent=2), encoding="utf-8")
    print(f"Registered: {NAME} ({nb_id})")
    print(f"Library: {LIBRARY}")
    print("Re-run: py -3 scripts/test_notebooklm_setup.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
