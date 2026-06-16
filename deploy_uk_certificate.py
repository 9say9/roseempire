"""Copy UK test certificate from upload folders to assets/ and deploy to GitHub."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UPLOAD_DIR = ROOT / "certificate upload"
CERTS_DIR = ROOT / "certificates"
EXTERNAL_CERTS = Path(r"D:\roseempire certificates")
OUT_PDF = ROOT / "assets" / "Rose-Empire-BS-EN-12935-Pillow-Report.pdf"
LEGACY_OUT = ROOT / "assets" / "Rose-Empire-UK-Test-Report.pdf"

ALLOWED = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}
SEARCH_DIRS = (UPLOAD_DIR, CERTS_DIR, EXTERNAL_CERTS)


def _find_upload() -> Path | None:
    files: list[Path] = []
    for folder in SEARCH_DIRS:
        if not folder.is_dir():
            continue
        files.extend(
            p
            for p in folder.iterdir()
            if p.is_file()
            and p.suffix.lower() in ALLOWED
            and p.name.lower() not in {"readme.txt", "desktop.ini"}
        )
    if not files:
        return None
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0]


def _image_to_pdf(src: Path, dst: Path) -> None:
    from fpdf import FPDF

    doc = FPDF(orientation="P", unit="mm", format="A4")
    doc.add_page()
    doc.image(str(src), x=8, y=8, w=194)
    dst.parent.mkdir(parents=True, exist_ok=True)
    doc.output(str(dst))


def prepare_certificate_pdf(src: Path) -> Path:
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    if src.suffix.lower() == ".pdf":
        shutil.copy2(src, OUT_PDF)
    else:
        _image_to_pdf(src, OUT_PDF)
    if LEGACY_OUT != OUT_PDF:
        shutil.copy2(OUT_PDF, LEGACY_OUT)
    return OUT_PDF


def deploy(*, push: bool = True) -> int:
    for folder in SEARCH_DIRS:
        folder.mkdir(parents=True, exist_ok=True)

    src = _find_upload()
    if not src:
        print("No certificate found. Drop a PDF or scan into any of:")
        for folder in SEARCH_DIRS:
            print(f"  {folder}")
        return 1

    out = prepare_certificate_pdf(src)
    size_kb = out.stat().st_size // 1024
    print(f"Certificate ready: {out} ({size_kb} KB) from {src}")

    if not push:
        return 0

    subprocess.run(["git", "add", str(out), str(LEGACY_OUT)], cwd=ROOT, check=True)
    msg = "Add BS EN 12935 pillow test report certificate PDF for website downloads."
    subprocess.run(["git", "commit", "-m", msg], cwd=ROOT, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, check=True)
    print("Pushed to GitHub — live at:")
    print(f"  https://www.roseempire.co.uk/assets/{out.name}")
    return 0


def _cli() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Deploy UK certificate from upload folders")
    parser.add_argument("--no-push", action="store_true", help="Copy to assets only, no git push")
    args = parser.parse_args()
    try:
        return deploy(push=not args.no_push)
    except subprocess.CalledProcessError as exc:
        print(f"Git/deploy failed: {exc}", file=sys.stderr)
        return exc.returncode or 1


if __name__ == "__main__":
    raise SystemExit(_cli())
