from pathlib import Path
p = Path(r"D:\roseempire\scripts\record_demo_video.py")
t = p.read_text(encoding="utf-8")
t = t.replace(
    "enrich_details=True, headed=True",
    "enrich_details=False, headed=True",
)
t = t.replace(
    "            leads = await _scrape_maps(page, mission, limit)\n",
    "            try:\n                leads = await _scrape_maps(page, mission, limit)\n            except Exception as exc:\n                print(f\"\\n  Scrape interrupted ({exc}) — saving partial video.\", file=sys.stderr)\n                leads = leads if \"leads\" in dir() else []\n",
)
# fix the leads variable - bad approach. Let me do it properly
