# -*- coding: utf-8 -*-
"""
Compress mobile warehouse/product videos for the Rose Empire site.

Usage:
  py -3 scripts/optimize-videos.py
  py -3 scripts/optimize-videos.py --webm
  py -3 scripts/optimize-videos.py --max-seconds 30

Reads from:
  assets/actual pics/mp4/
  assets/videos/raw/

Writes to:
  assets/videos/
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "videos"
SELF_HOST_MAX_MB = 6.0
MAX_EDGE = 720
CRF = 32
AUDIO_BITRATE = "64k"

SOURCE_DIRS = [
    ROOT / "assets" / "actual pics" / "mp4",
    ROOT / "assets" / "videos" / "raw",
]

SLOT_NAMES = [
    "warehouse-tour",
    "product-explainer",
]


def find_tool(name: str) -> str:
    exe = shutil.which(name)
    if not exe:
        raise SystemExit(f"{name} not found on PATH.")
    return exe


def probe(ffprobe: str, path: Path) -> dict:
    raw = subprocess.check_output(
        [
            ffprobe,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,duration:format=duration",
            "-of",
            "json",
            str(path),
        ],
        text=True,
    )
    data = json.loads(raw)
    stream = (data.get("streams") or [{}])[0]
    duration = float(stream.get("duration") or data.get("format", {}).get("duration") or 0)
    return {
        "width": int(stream.get("width") or 0),
        "height": int(stream.get("height") or 0),
        "duration": duration,
    }


def collect_sources() -> list[Path]:
    files: list[Path] = []
    for d in SOURCE_DIRS:
        if not d.is_dir():
            continue
        for p in sorted(d.iterdir(), key=lambda x: x.name.lower()):
            if p.suffix.lower() in {".mp4", ".mov", ".m4v", ".webm"} and p.is_file():
                files.append(p)
    seen = set()
    unique = []
    for p in files:
        key = p.name.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(p)
    return unique


def run(cmd: list[str]) -> None:
    print(">", " ".join(cmd))
    subprocess.check_call(cmd)


def compress_one(
    ffmpeg: str,
    ffprobe: str,
    src: Path,
    slot: str,
    *,
    make_webm: bool,
    max_seconds: float | None,
) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    mp4_out = OUT / f"{slot}.mp4"
    webm_out = OUT / f"{slot}.webm"
    poster_out = OUT / f"{slot}-poster.jpg"

    meta = probe(ffprobe, src)
    duration = meta["duration"]
    poster_ss = "0.8" if duration >= 2 else "0.2"

    vf = f"scale='min({MAX_EDGE},iw)':-2"
    # iPhone portrait often has rotation metadata; force transpose if width>height in file
    # but display is portrait (common for phone). Autorotate via ffmpeg display matrix is OK.

    mp4_cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(src),
        "-map",
        "0:v:0",
        "-map",
        "0:a:0?",
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        str(CRF),
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        "-c:a",
        "aac",
        "-b:a",
        AUDIO_BITRATE,
        "-ac",
        "1",
        "-ar",
        "44100",
    ]
    if max_seconds:
        mp4_cmd.extend(["-t", str(max_seconds)])
    mp4_cmd.append(str(mp4_out))
    run(mp4_cmd)

    if make_webm:
        webm_cmd = [
            ffmpeg,
            "-y",
            "-i",
            str(src),
            "-map",
            "0:v:0",
            "-map",
            "0:a:0?",
            "-vf",
            vf,
            "-c:v",
            "libvpx-vp9",
            "-b:v",
            "0",
            "-crf",
            "36",
            "-cpu-used",
            "4",
            "-row-mt",
            "1",
            "-c:a",
            "libopus",
            "-b:a",
            "48k",
            "-ac",
            "1",
        ]
        if max_seconds:
            webm_cmd.extend(["-t", str(max_seconds)])
        webm_cmd.append(str(webm_out))
        try:
            run(webm_cmd)
        except subprocess.CalledProcessError:
            print(f"WARN: WebM failed for {src.name}")
            if webm_out.exists():
                webm_out.unlink()
    elif webm_out.exists():
        webm_out.unlink()

    run(
        [
            ffmpeg,
            "-y",
            "-ss",
            poster_ss,
            "-i",
            str(src),
            "-map",
            "0:v:0",
            "-frames:v",
            "1",
            "-update",
            "1",
            "-q:v",
            "5",
            "-vf",
            vf,
            str(poster_out),
        ]
    )

    out_meta = probe(ffprobe, mp4_out)
    mp4_mb = mp4_out.stat().st_size / (1024 * 1024)
    webm_mb = webm_out.stat().st_size / (1024 * 1024) if webm_out.exists() else None
    src_mb = src.stat().st_size / (1024 * 1024)
    orientation = "portrait" if out_meta["height"] > out_meta["width"] else "landscape"

    return {
        "slot": slot,
        "source": str(src.relative_to(ROOT)).replace("\\", "/"),
        "source_mb": round(src_mb, 2),
        "mp4": f"assets/videos/{slot}.mp4",
        "mp4_mb": round(mp4_mb, 2),
        "webm": f"assets/videos/{slot}.webm" if webm_out.exists() else None,
        "webm_mb": round(webm_mb, 2) if webm_mb is not None else None,
        "poster": f"assets/videos/{slot}-poster.jpg",
        "duration_s": round(out_meta["duration"] or duration, 1),
        "width": out_meta["width"],
        "height": out_meta["height"],
        "orientation": orientation,
        "cdn_required": mp4_mb > SELF_HOST_MAX_MB,
        "self_host_ok": mp4_mb <= SELF_HOST_MAX_MB,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--webm", action="store_true", help="Also encode WebM (slow)")
    parser.add_argument(
        "--max-seconds",
        type=float,
        default=28.0,
        help="Cap output length for homepage (default 28). Use 0 for full length.",
    )
    args = parser.parse_args()
    max_seconds = None if not args.max_seconds else args.max_seconds

    ffmpeg = find_tool("ffmpeg")
    ffprobe = find_tool("ffprobe")
    sources = collect_sources()
    if not sources:
        print("No source videos found. Drop MOV/MP4 into:")
        for d in SOURCE_DIRS:
            print(f"  - {d}")
        return 1

    print(f"Found {len(sources)} source(s). Self-host max: {SELF_HOST_MAX_MB} MB")
    results = []
    for i, src in enumerate(sources[: len(SLOT_NAMES)]):
        slot = SLOT_NAMES[i]
        print(f"\n=== {slot} <- {src.name} ({src.stat().st_size / 1024 / 1024:.1f} MB) ===")
        results.append(
            compress_one(
                ffmpeg,
                ffprobe,
                src,
                slot,
                make_webm=args.webm,
                max_seconds=max_seconds,
            )
        )

    manifest = {
        "updatedAt": date.today().isoformat(),
        "selfHostMaxMb": SELF_HOST_MAX_MB,
        "videos": results,
        "homepagePrimary": "warehouse-tour",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    cdn_needed = [r for r in results if r["cdn_required"]]
    note = OUT / "CDN_REQUIRED.txt"
    if cdn_needed:
        lines = [
            "Optimized MP4s still exceed the self-host size budget for GitHub Pages.",
            f"Limit: {SELF_HOST_MAX_MB} MB per file.",
            "Upload to Cloudflare Stream / R2, then set URLs in site-config.js -> videos.",
            "",
        ]
        for r in cdn_needed:
            lines.append(f"- {r['slot']}: {r['mp4_mb']} MB -> {r['mp4']}")
        note.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("\nCDN REQUIRED:", ", ".join(r["slot"] for r in cdn_needed))
    elif note.exists():
        note.unlink()

    print("\nDone.")
    for r in results:
        flag = "CDN" if r["cdn_required"] else "OK"
        print(
            f"  [{flag}] {r['slot']}: {r['mp4_mb']} MB mp4, "
            f"{r['orientation']} {r['width']}x{r['height']}, {r['duration_s']}s"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
