"""Build minified CSS + optimized WebP images for PageSpeed."""
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
PRODUCTS = ASSETS / "products"

IMAGE_JOBS = [
    (PRODUCTS / "wqmp-waterproof-quilted.jpg", PRODUCTS / "wqmp-waterproof-quilted.webp", 640, 78),
    (PRODUCTS / "qmp-quilted.jpg", PRODUCTS / "qmp-quilted.webp", 640, 78),
    (PRODUCTS / "terry-lifestyle-bed.jpg", PRODUCTS / "terry-lifestyle-bed.webp", 640, 80),
    (ASSETS / "down_pillows.png", ASSETS / "down_pillows.webp", 640, 80),
    (ASSETS / "favicon.png", ASSETS / "favicon-192.png", 192, 85),
]


def minify_css(src: Path, dest: Path) -> None:
    raw = src.read_text(encoding="utf-8")
    out = re.sub(r"/\*[\s\S]*?\*/", "", raw)
    out = re.sub(r"\s*([{}:;,>~+])\s*", r"\1", out)
    out = re.sub(r"\s+", " ", out).strip()
    dest.write_text(out, encoding="utf-8")
    print(f"CSS {src.name}: {src.stat().st_size // 1024}KB -> {dest.stat().st_size // 1024}KB")


def optimize_image(src: Path, dest: Path, max_w: int, quality: int) -> None:
    if not src.is_file():
        print(f"  skip missing {src.name}")
        return
    img = Image.open(src)
    w, h = img.size
    if w > max_w:
        img = img.resize((max_w, int(h * max_w / w)), Image.Resampling.LANCZOS)
    if dest.suffix == ".webp":
        img.convert("RGB").save(dest, "WEBP", quality=quality, method=6)
    else:
        img.save(dest, optimize=True)
    print(f"  {dest.name}: {dest.stat().st_size // 1024}KB")


def main() -> None:
    minify_css(ROOT / "styles.css", ROOT / "styles.min.css")
    for src, dest, max_w, q in IMAGE_JOBS:
        optimize_image(src, dest, max_w, q)


if __name__ == "__main__":
    main()
