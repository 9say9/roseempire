#!/usr/bin/env python3
"""Build a 1200x630 social share image from existing Rose Empire brand assets."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUT_PNG = ASSETS / "og-share.png"
OUT_JPG = ASSETS / "og-share.jpg"
LOGO_SVG = ASSETS / "logo-mark.svg"
PRODUCT = ASSETS / "products" / "wqmp-skirt-fitted.jpg"
WIDTH, HEIGHT = 1200, 630
NAVY = (16, 34, 65)
NAVY_DEEP = (8, 20, 36)
GOLD = (184, 149, 73)
CREAM = (246, 244, 240)
WHITE = (255, 255, 255)


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _rasterize_logo(size: int) -> Image.Image:
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        dest = Path(tmp.name)
    subprocess.run(
        ["rsvg-convert", "-w", str(size), "-h", str(size), str(LOGO_SVG), "-o", str(dest)],
        check=True,
    )
    logo = Image.open(dest).convert("RGBA")
    dest.unlink(missing_ok=True)
    return logo


def _product_panel() -> Image.Image:
    src = Image.open(PRODUCT).convert("RGB")
    # Cover-crop to the right panel.
    panel_w, panel_h = 520, HEIGHT
    scale = max(panel_w / src.width, panel_h / src.height)
    resized = src.resize((int(src.width * scale), int(src.height * scale)), Image.Resampling.LANCZOS)
    left = max(0, (resized.width - panel_w) // 2)
    top = max(0, (resized.height - panel_h) // 8)
    cropped = resized.crop((left, top, left + panel_w, top + panel_h))
    return cropped


def main() -> None:
    canvas = Image.new("RGB", (WIDTH, HEIGHT), NAVY_DEEP)
    draw = ImageDraw.Draw(canvas)

    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        r = int(NAVY_DEEP[0] + (NAVY[0] - NAVY_DEEP[0]) * t)
        g = int(NAVY_DEEP[1] + (NAVY[1] - NAVY_DEEP[1]) * t)
        b = int(NAVY_DEEP[2] + (NAVY[2] - NAVY_DEEP[2]) * t)
        draw.line([(0, y), (680, y)], fill=(r, g, b))

    product = _product_panel()
    canvas.paste(product, (WIDTH - product.width, 0))

    # Soft fade from navy copy into the product photo.
    fade = Image.new("L", (160, HEIGHT), 0)
    fade_draw = ImageDraw.Draw(fade)
    for x in range(160):
        fade_draw.line([(x, 0), (x, HEIGHT)], fill=int(255 * (1 - x / 159)))
    overlay = Image.new("RGB", (160, HEIGHT), NAVY)
    canvas.paste(overlay, (WIDTH - product.width - 40, 0), fade)

    gold_bar = Image.new("RGB", (WIDTH, 8), GOLD)
    canvas.paste(gold_bar, (0, 0))
    canvas.paste(gold_bar, (0, HEIGHT - 8))

    logo = _rasterize_logo(92)
    canvas.paste(logo, (56, 48), logo)

    serif_sm = _font(22, bold=True)
    serif_lg = _font(46, bold=True)
    sans = _font(22, bold=False)
    sans_sm = _font(18, bold=False)

    draw = ImageDraw.Draw(canvas)
    draw.text((168, 72), "ROSE EMPIRE", font=serif_sm, fill=GOLD)
    draw.text((56, 168), "Wholesale mattress", font=serif_lg, fill=WHITE)
    draw.text((56, 226), "protectors & pillows", font=serif_lg, fill=WHITE)
    draw.text((56, 300), "UK trade supply for hotels, care homes,", font=sans, fill=CREAM)
    draw.text((56, 334), "holiday lets, student halls and retailers.", font=sans, fill=CREAM)

    facts = "MOQ 20/size  ·  Pillows 5/box  ·  Manchester stock"
    draw.text((56, 410), facts, font=sans_sm, fill=GOLD)
    draw.text((56, 520), "roseempire.co.uk", font=serif_sm, fill=WHITE)
    draw.text((56, 556), "+44 7999 988450", font=sans_sm, fill=(200, 188, 160))

    # Slight sharpening after composite.
    canvas = canvas.filter(ImageFilter.UnsharpMask(radius=0.6, percent=80, threshold=2))
    canvas.save(OUT_PNG, format="PNG", optimize=True)
    canvas.save(OUT_JPG, format="JPEG", quality=82, optimize=True)
    kb = OUT_JPG.stat().st_size / 1024
    print(f"Wrote {OUT_JPG.relative_to(ROOT)} {canvas.size[0]}x{canvas.size[1]} ({kb:.1f} KB)")
    print(f"Wrote {OUT_PNG.relative_to(ROOT)} ({OUT_PNG.stat().st_size / 1024:.1f} KB)")
    if canvas.size != (WIDTH, HEIGHT):
        raise SystemExit("OG image is not 1200x630")
    if kb > 500:
        raise SystemExit("og-share.jpg is too heavy")


if __name__ == "__main__":
    main()
