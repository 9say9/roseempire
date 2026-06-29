from pathlib import Path
p = Path(r"D:\roseempire\scripts\record_demo_video.py")
t = p.read_text(encoding="utf-8")
t = t.replace("enrich_details=True", "enrich_details=False")
old = """            leads = await _scrape_maps(page, mission, limit)

            if leads:"""
new = """            try:
                leads = await _scrape_maps(page, mission, limit)
            except Exception as exc:
                print(f"\\n  Scrape interrupted ({exc}) — saving video anyway.", file=sys.stderr)

            if leads:"""
t = t.replace(old, new)
p.write_text(t, encoding="utf-8")
print("patched")
