from pathlib import Path
p = Path("d:/roseempire/fleet_ai.py")
text = p.read_text(encoding="utf-8")
if text.startswith("import os"):
    text = """\"\"\"Sarah / James / Alex — OpenAI GPT-4o-mini for fleet dashboard.\"\"\"
from __future__ import annotations

import os

import requests
from dotenv import load_dotenv

load_dotenv()

""" + text.split("from __future__ import annotations", 1)[-1].split("import os\n", 1)[-1]
    p.write_text(text, encoding="utf-8")
import py_compile
py_compile.compile(str(p))
print("fleet_ai fixed")
