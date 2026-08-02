from pathlib import Path

ROOT = Path(r"d:\rose empire main")
files = ["index.html", "hotels.html", "care-homes.html", "wholesale-mattress-protectors.html"]

replacements = [
    ("styles.min.css?v=20260802e", "styles.min.css?v=20260802h"),
    ("styles.css?v=20260802e", "styles.css?v=20260802h"),
    ("styles.css?v=20260802d", "styles.css?v=20260802h"),
    ("app.js?v=20260802g", "app.js?v=20260802h"),
    ("conversion-analytics.js?v=20260802g", "conversion-analytics.js?v=20260802h"),
    ("Rose-Empire-Wholesale-Catalog.pdf\"", "Rose-Empire-Wholesale-Catalog.pdf?v=20260802h\""),
    ("Rose-Empire-Wholesale-Catalog.pdf'", "Rose-Empire-Wholesale-Catalog.pdf?v=20260802h'"),
]

for name in files:
    path = ROOT / name
    text = path.read_text(encoding="utf-8")
    for old, new in replacements:
        text = text.replace(old, new)
    # Avoid double-busting if script re-run
    text = text.replace(
        "Rose-Empire-Wholesale-Catalog.pdf?v=20260802h?v=20260802h",
        "Rose-Empire-Wholesale-Catalog.pdf?v=20260802h",
    )
    path.write_text(text, encoding="utf-8", newline="\n")
    print(name, "updated")
