from pathlib import Path
p = Path(r"D:\roseempire\ai_router\main.py")
t = p.read_text(encoding="utf-8")
t = t.replace('"tier": "tools"', '"tier": "free", "supports_tools": True')
t = t.replace(
    'if m.get("model_info", {}).get("tier") == "tools"',
    'if m.get("model_info", {}).get("id") == "ollama-tools"',
)
p.write_text(t, encoding="utf-8")
print("fixed tier")
