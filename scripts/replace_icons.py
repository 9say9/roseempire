"""Replace Font Awesome markup with local SVG sprite icons."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MAP = {
    "fa-location-dot": "location",
    "fa-phone": "phone",
    "fa-envelope": "envelope",
    "fa-clock": "clock",
    "fa-bars": "bars",
    "fa-moon": "moon",
    "fa-sun": "sun",
    "fa-file-invoice": "invoice",
    "fa-industry": "industry",
    "fa-certificate": "certificate",
    "fa-file-shield": "shield",
    "fa-truck-fast": "truck",
    "fa-box-open": "box",
    "fa-tag": "tag",
    "fa-shield-halved": "shield",
    "fa-arrows-up-down": "tag",
    "fa-percent": "percent",
    "fa-file-pdf": "pdf",
    "fa-boxes-packing": "box",
    "fa-shield-check": "shield",
    "fa-warehouse": "warehouse",
    "fa-handshake-angle": "award",
    "fa-award": "award",
    "fa-magnifying-glass": "search",
    "fa-magnifying-glass-plus": "search",
    "fa-xmark": "xmark",
    "fa-folder-open": "folder",
    "fa-credit-card": "card",
    "fa-paper-plane": "send",
    "fa-calculator": "calc",
    "fa-circle-notch": "spinner",
    "fa-spinner": "spinner",
    "fa-brands fa-linkedin": "linkedin",
    "fa-circle-exclamation": "warn",
    "fa-circle-info": "info",
    "fa-circle-check": "check",
    "fa-trash-can": "trash",
    "fa-cart-plus": "cart",
    "fa-feather": "award",
    "fa-ruler": "calc",
    "fa-comments": "comments",
    "fa-building": "building",
    "fa-bag-shopping": "bag",
}

def svg_use(name: str, spin: bool = False) -> str:
    cls = "ico ico-spin" if spin else "ico"
    return f'<svg class="{cls}" viewBox="0 0 24 24" width="1em" height="1em" aria-hidden="true"><use href="assets/icons.svg#{name}"></use></svg>'


ICON_RE = re.compile(r'<i class="([^"]+)"></i>')


def replace_icons(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        classes = match.group(1)
        spin = "fa-spin" in classes
        for fa_cls, icon_id in sorted(MAP.items(), key=lambda x: len(x[0]), reverse=True):
            if fa_cls in classes:
                return svg_use(icon_id, spin)
        return match.group(0)

    return ICON_RE.sub(repl, text)


def main() -> None:
    for rel in ("index.html", "app.js", "chat-widget.js"):
        path = ROOT / rel
        raw = path.read_text(encoding="utf-8")
        out = replace_icons(raw)
        if out != raw:
            path.write_text(out, encoding="utf-8")
            print(f"updated {rel}")


if __name__ == "__main__":
    main()
