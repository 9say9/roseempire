"""Generate Terry mattress protector images via Gemini 2.5 Flash Image (Nano Banana)."""
from __future__ import annotations

import os
import sys
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "products"
MODEL = "gemini-2.5-flash-image"

PROMPTS = {
    "terry-lifestyle-bed.png": (
        "Ultra-realistic professional hotel bedroom product photography. King bed with a fitted "
        "white cotton TERRY TOWELLING mattress protector — visible loop-pile terry texture like "
        "a bath towel, NOT quilted diamonds. The protector has a deep white elastic fitted skirt "
        "stretching down the mattress sides, clearly visible at the corner. Crisp hotel linens, "
        "soft natural daylight, luxury boutique hotel Manchester UK style, 4K commercial catalog "
        "quality, no text, no logos, no watermark."
    ),
    "terry-elastic-skirt.png": (
        "Close-up commercial product photo of a white terry towelling waterproof mattress protector "
        "on a mattress corner. Show the cotton terry loop-pile top surface texture and the deep "
        "elastic fitted skirt hugging the mattress edge (35cm depth). Clean white background, "
        "studio lighting, wholesale catalog style, photorealistic, no text."
    ),
    "terry-waterproof-product.png": (
        "Folded stack of white terry towelling mattress protectors for wholesale trade. Terry cotton "
        "loop pile texture visible on top fold, fitted elastic skirt edge peeking out. Professional "
        "B2B product packshot on light cream background, high-end e-commerce, photorealistic, no text."
    ),
}


def main() -> int:
    load_dotenv(ROOT / ".env")
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("ERROR: Set GEMINI_API_KEY in .env", file=sys.stderr)
        return 1

    try:
        from google import genai
        from google.genai import types
        from PIL import Image
    except ImportError:
        print("Installing google-genai and pillow...", file=sys.stderr)
        os.system(f'"{sys.executable}" -m pip install -q google-genai pillow')
        from google import genai
        from google.genai import types
        from PIL import Image

    client = genai.Client(api_key=api_key)
    OUT.mkdir(parents=True, exist_ok=True)

    for filename, prompt in PROMPTS.items():
        out_path = OUT / filename
        print(f"Generating {filename}...")
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(aspect_ratio="4:3"),
                ),
            )
            saved = False
            for part in response.parts:
                if part.inline_data is not None:
                    image = Image.open(BytesIO(part.inline_data.data))
                    image.save(out_path, format="PNG" if filename.endswith(".png") else "JPEG", quality=92)
                    print(f"  Saved {out_path} ({image.size[0]}x{image.size[1]})")
                    saved = True
                    break
            if not saved:
                print(f"  WARN: No image in response for {filename}")
        except Exception as exc:
            print(f"  ERROR {filename}: {exc}", file=sys.stderr)
            return 1

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
