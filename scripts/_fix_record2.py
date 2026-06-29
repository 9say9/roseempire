from pathlib import Path
p = Path(r"D:\roseempire\scripts\record_demo_video.py")
t = p.read_text(encoding="utf-8")
if "sys.path.insert" not in t:
    t = t.replace(
        "import argparse\nimport asyncio",
        "import argparse\nimport asyncio\nimport sys\n\nROOT = Path(__file__).resolve().parent.parent\nif str(ROOT) not in sys.path:\n    sys.path.insert(0, str(ROOT))",
    )
    t = t.replace("ROOT = Path(__file__).resolve().parent.parent\nOUT_DIR", "OUT_DIR")
p.write_text(t, encoding="utf-8")
print("fixed path")
