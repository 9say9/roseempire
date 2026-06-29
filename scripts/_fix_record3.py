from pathlib import Path
p = Path(r"D:\roseempire\scripts\record_demo_video.py")
t = p.read_text(encoding="utf-8")
header = '''"""Record a short Sarah scraper demo MP4 for TikTok/Shorts test edits."""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

from playwright.async_api import Page, async_playwright

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
'''
# replace broken header through playwright import block
start = t.index('"""Record')
end = t.index('OUT_DIR = ROOT')
t = header + t[end:]
p.write_text(t, encoding="utf-8")
print("fixed imports")
