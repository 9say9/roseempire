"""Compress hero LCP image for PageSpeed (WebP + responsive sizes)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "mattress_protector.png"
OUT_640 = ROOT / "assets" / "mattress_protector-640.webp"
OUT_FULL = ROOT / "assets" / "mattress_protector.webp"


def _save_webp(img: Image.Image, path: Path, quality: int = 80) -> None:
    rgb = img.convert("RGB") if img.mode != "RGB" else img
    rgb.save(path, "WEBP", quality=quality, method=6)
    kb = path.stat().st_size / 1024
    print(f"  {path.name}: {rgb.size[0]}x{rgb.size[1]} — {kb:.1f} KB")


def main() -> None:
    if not SRC.is_file():
        raise SystemExit(f"Missing {SRC}")
    img = Image.open(SRC)
    w, h = img.size

    img640 = img.resize((640, int(h * 640 / w)), Image.Resampling.LANCZOS)
    _save_webp(img640, OUT_640, quality=78)

    target_w = min(w, 1040)
    img_full = img.resize((target_w, int(h * target_w / w)), Image.Resampling.LANCZOS)
    _save_webp(img_full, OUT_FULL, quality=80)

    src_kb = SRC.stat().st_size / 1024
    print(f"Source PNG: {src_kb:.1f} KB")


if __name__ == "__main__":
    main()
