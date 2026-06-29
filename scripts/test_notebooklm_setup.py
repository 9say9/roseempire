"""Verify NotebookLM + Rose Empire integration."""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIBRARY = Path.home() / "AppData/Local/notebooklm-mcp/Data/library.json"
PACK = ROOT / "notebooklm/rose-empire-knowledge-pack.md"
MCP = ROOT / ".cursor/mcp.json"


def check(name: str, ok: bool, detail: str = "") -> bool:
    mark = "OK" if ok else "FAIL"
    line = f"  [{mark}] {name}"
    if detail:
        line += f" — {detail}"
    print(line)
    return ok


def get_json(url: str) -> dict | None:
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def main() -> int:
    print("\nRose Empire — NotebookLM integration test\n")
    ok = True

    ok &= check("Knowledge pack", PACK.is_file(), f"{PACK.stat().st_size // 1024} KB" if PACK.is_file() else "missing")
    if PACK.is_file():
        text = PACK.read_text(encoding="utf-8", errors="ignore")
        ok &= check("Pack has MOQ data", "20 pieces" in text or "MOQ" in text)
        ok &= check("Pack has bot names", "Sarah" in text and "James" in text and "Adeel" in text)

    ok &= check("MCP config", MCP.is_file(), str(MCP))

    notebooks = 0
    active = None
    if LIBRARY.is_file():
        lib = json.loads(LIBRARY.read_text(encoding="utf-8"))
        notebooks = len(lib.get("notebooks") or [])
        active = lib.get("active_notebook_id")
        ok &= check("Notebook registered in MCP", notebooks > 0, f"{notebooks} notebook(s)")
        if notebooks:
            for nb in lib["notebooks"]:
                print(f"       • {nb.get('name', '?')} — {nb.get('url', nb.get('id', ''))}")
            check("Active notebook set", bool(active), active or "none")
    else:
        ok &= check("MCP library file", False, str(LIBRARY))

    router = get_json("http://127.0.0.1:8000/health")
    ok &= check("AI Router", bool(router) and router.get("status") == "healthy")

    crm = get_json("http://127.0.0.1:5050/health")
    ok &= check("CRM dashboard", bool(crm) and crm.get("status") == "ok")

    print()
    if notebooks == 0:
        print("NEXT STEP (required for Roo to query NotebookLM):")
        print("  1. Open https://notebooklm.google.com - Rose Empire B2B notebook")
        print("  2. Copy the URL from the browser address bar")
        print("  Or run (paste your notebook URL):")
        print("     py -3 scripts\\register_notebooklm_notebook.py <notebook-url>")
        print()
        print("  Then in Roo:")
        print('     "ask_question: What is the MOQ for mattress protectors?"')
        print()
        print("  Web upload alone is not enough - MCP needs the notebook URL registered.")
    elif ok:
        print("Setup looks good. Test in Roo:")
        print('  "ask_question: What is Rose Empire MOQ for care home outreach?"')
    else:
        print("Fix FAIL items above, then re-run: py -3 scripts/test_notebooklm_setup.py")
    print()
    return 0 if ok and notebooks > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
