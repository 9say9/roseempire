"""Fix double-encoded UTF-8 mojibake in site files."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REPLACEMENTS = (
    ("Â£", "\u00a3"),
    ("Â·", "\u00b7"),
    ("\u00e2\u20ac\u201d", "\u2014"),  # em dash mojibake
    ("\u00e2\u20ac\u201c", "\u2013"),  # en dash mojibake
    ("â€\u0094", "\u2014"),
    ("â€\u0093", "\u2013"),
    ("â€¦", "\u2026"),
    ("Ã—", "\u00d7"),
    ("â€™", "'"),
    ("â€˜", "'"),
)

FILES = (
    "index.html",
    "chat-widget.js",
    "404.html",
    "catalog-data.json",
    "quote-pdf.js",
)


def fix_text(text: str) -> str:
    for bad, good in REPLACEMENTS:
        text = text.replace(bad, good)
    # Double UTF-8: UTF-8 bytes were interpreted as Latin-1 and re-saved as UTF-8
    if "Ã" in text or "Â" in text:
        try:
            text = text.encode("latin-1").decode("utf-8")
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass
    return text


def main() -> None:
    for name in FILES:
        path = ROOT / name
        if not path.is_file():
            continue
        original = path.read_text(encoding="utf-8")
        fixed = fix_text(original)
        if fixed != original:
            path.write_text(fixed, encoding="utf-8", newline="\n")
            print(f"Fixed: {name}")


if __name__ == "__main__":
    main()
