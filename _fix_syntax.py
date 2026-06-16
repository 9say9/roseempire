from pathlib import Path
p = Path("d:/roseempire/fix_ms365_graph_playwright.py")
text = p.read_text(encoding="utf-8")
text = text.replace(
    "print(f\"\nOpening Microsoft login (tenant: {_tenant()})...\n\")",
    "print(f\"Opening Microsoft login (tenant: {_tenant()})...\")",
)
text = text.replace(
    "print(\"Pick info@roseempire.co.uk and click Accept.\n\")",
    "print(\"Pick info@roseempire.co.uk and click Accept.\")",
)
# brute fix lines 108-112 if still broken
lines = text.splitlines()
fixed = []
skip = 0
for i, line in enumerate(lines):
    if skip:
        skip -= 1
        continue
    if line.strip() == "print(f\"":
        fixed.append("    print(f\"Opening Microsoft login (tenant: {_tenant()})...\")")
        skip = 2
        continue
    fixed.append(line)
p.write_text("\n".join(fixed) + "\n", encoding="utf-8")
import py_compile
py_compile.compile(str(p))
print("ok")
