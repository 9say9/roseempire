from pathlib import Path
p = Path("d:/roseempire/email_agent.py")
lines = p.read_text(encoding="utf-8").splitlines()
out = []
i = 0
while i < len(lines):
    line = lines[i]
    if line.strip() == "print(\"Sign in as info@roseempire.co.uk if asked, then click Accept.":
        out.append("        print(\"Sign in as info@roseempire.co.uk if asked, then click Accept.\")")
        i += 2
        continue
    if line.strip() == "print(\"" and i+2 < len(lines) and "Waiting for approval" in lines[i+1]:
        out.append("        print(\"Waiting for approval in browser...\")")
        i += 3
        continue
    out.append(line)
    i += 1
p.write_text("\n".join(out)+"\n", encoding="utf-8")
import py_compile
py_compile.compile(str(p))
print("fixed")
