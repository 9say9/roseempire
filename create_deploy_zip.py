"""
Rose Empire - create static site deploy zip (GitHub Pages or manual upload).
Run: py -3.12 create_deploy_zip.py
"""
from __future__ import annotations

import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "rose-empire-website-deploy.zip"
OUT_ALT = ROOT / f"rose-empire-deploy-{datetime.now().strftime('%Y%m%d-%H%M%S')}.zip"

FILES = [
    "index.html",
    "styles.css",
    "app.js",
    "site-config.js",
    "chat-widget.js",
    "quote-pricing.js",
    "quote-shipping.js",
    "quote-pdf.js",
    "robots.txt",
    "sitemap.xml",
    "404.html",
]

ASSETS_DIR = ROOT / "assets"


def add_path(zf: zipfile.ZipFile, path: Path, arc_prefix: str = "") -> None:
    if path.is_dir():
        for child in sorted(path.rglob("*")):
            if child.is_file():
                rel = child.relative_to(ROOT)
                zf.write(child, rel.as_posix())
    else:
        name = arc_prefix or path.name
        zf.write(path, name)


def build_zip(dest: Path) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.unlink()

    count = 0
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for name in FILES:
            p = ROOT / name
            if not p.is_file():
                raise FileNotFoundError(f"Missing required file: {name}")
            zf.write(p, name)
            count += 1

        if not ASSETS_DIR.is_dir():
            raise FileNotFoundError("Missing assets folder")
        for f in sorted(ASSETS_DIR.rglob("*")):
            if f.is_file():
                zf.write(f, f.relative_to(ROOT).as_posix())
                count += 1

    return count


def main() -> None:
    print()
    print("=" * 56)
    print("  Rose Empire - Create deploy zip")
    print("=" * 56)
    print()

    target = OUT
    try:
        n = build_zip(target)
        print(f"  SUCCESS: {target.name}")
        print(f"  Files packed: {n}")
        print(f"  Size: {target.stat().st_size:,} bytes")
        print(f"  Path: {target}")
    except (PermissionError, OSError) as e:
        print(f"  Note: could not write {OUT.name} ({e})")
        print("  Trying alternate filename...")
        target = OUT_ALT
        n = build_zip(target)
        print(f"  SUCCESS: {target.name}")
        print(f"  Files packed: {n}")
        print(f"  Size: {target.stat().st_size:,} bytes")
        print(f"  Path: {target}")
        print()
        print("  Upload THIS zip if the default filename was locked open.")

    print()
    print("  Next: push to GitHub Pages or upload the zip to your static host.")
    print()


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as e:
        print(f"\n  ERROR: {e}\n")
        raise SystemExit(1) from e
    except Exception as e:
        print(f"\n  ERROR: {e}\n")
        raise SystemExit(1) from e
