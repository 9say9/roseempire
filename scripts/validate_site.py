import json
import re
from pathlib import Path

html = Path("index.html").read_text(encoding="utf-8")
m = re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', html, re.S)
json.loads(m.group(1))
print("JSON-LD OK")

bad = sum(1 for c in html if c in "\u00c2\u00e2\u00c3" and c)
# simpler check
for pat in ["Â", "â€", "Ã—"]:
    if pat in html:
        print("WARN still has:", pat)
print("Done")
