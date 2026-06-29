"""Search YouTube, download top result, crop 9:16, mirror, mix voiceover — TikTok pipeline."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from moviepy.editor import AudioFileClip, CompositeAudioClip, VideoFileClip, vfx
from yt_dlp import YoutubeDL

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "vibe-output"
RAW_FILE = OUT_DIR / "raw_download.mp4"
DEFAULT_OUT = OUT_DIR / "tiktok_output.mp4"


def search_top_video(keyword: str) -> dict | None:
    print(f"Searching YouTube for: '{keyword}'...")
    opts = {"default_search": "ytsearch1", "quiet": True, "skip_download": True}
    with YoutubeDL(opts) as ydl:
        result = ydl.extract_info(keyword, download=False)
    entries = (result or {}).get("entries") or []
    if not entries:
        print("No videos found for that keyword.")
        return None
    video = entries[0]
    print(f"Top video: {video.get('title', '?')}")
    print(f"URL: {video.get('webpage_url', '?')}")
    return video


def download_video(url: str, dest: Path) -> Path:
    print("Downloading footage...")
    dest.parent.mkdir(parents=True, exist_ok=True)
    opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": str(dest.with_suffix("")),
        "overwrites": True,
        "quiet": True,
        "merge_output_format": "mp4",
    }
    with YoutubeDL(opts) as ydl:
        ydl.download([url])
    # yt-dlp may write raw_download.mp4 or raw_download.webm etc.
    for candidate in dest.parent.glob(dest.stem + ".*"):
        if candidate.suffix.lower() in {".mp4", ".mkv", ".webm"}:
            return candidate
    if dest.exists():
        return dest
    raise FileNotFoundError(f"Download failed — no file in {dest.parent}")


def process_video(
    source: Path,
    *,
    start_time: float,
    end_time: float,
    voiceover_path: Path | None,
    output_path: Path,
) -> Path:
    print("Processing vertical crop + mirror...")
    clip = VideoFileClip(str(source)).subclip(start_time, end_time)
    w, h = clip.size
    target_w = int(h * (9 / 16))
    x1 = max(0, (w - target_w) // 2)
    cropped = clip.crop(x1=x1, y1=0, x2=x1 + target_w, y2=h)
    mirrored = cropped.fx(vfx.mirror_x)

    print("Mixing audio...")
    if voiceover_path and voiceover_path.is_file():
        voiceover = AudioFileClip(str(voiceover_path))
        if mirrored.audio is not None:
            background = mirrored.audio.volumex(0.1)
            final_audio = CompositeAudioClip(
                [voiceover, background.set_duration(voiceover.duration)]
            )
        else:
            final_audio = voiceover
        final = mirrored.set_audio(final_audio).set_duration(voiceover.duration)
    else:
        print("No voiceover found — exporting mirrored clip only.")
        final = mirrored.volumex(0.3) if mirrored.audio is not None else mirrored

    print("Rendering final TikTok file...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final.write_videofile(
        str(output_path),
        codec="libx264",
        audio_codec="aac",
        fps=30,
        verbose=False,
        logger=None,
    )
    clip.close()
    final.close()
    print(f"Done: {output_path}")
    return output_path


def search_and_process_video(
    search_keyword: str,
    start_time: float = 0,
    end_time: float = 30,
    voiceover_path: str | Path = "voiceover.mp3",
    output_path: str | Path = DEFAULT_OUT,
) -> Path | None:
    video = search_top_video(search_keyword)
    if not video:
        return None
    url = video.get("webpage_url")
    if not url:
        print("Missing video URL in search result.")
        return None

    raw = download_video(url, RAW_FILE)
    vo = Path(voiceover_path)
    if not vo.is_file():
        vo = ROOT / voiceover_path
    return process_video(
        raw,
        start_time=start_time,
        end_time=end_time,
        voiceover_path=vo if vo.is_file() else None,
        output_path=Path(output_path),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="YouTube search -> TikTok vertical editor")
    parser.add_argument("keyword", help="YouTube search keyword")
    parser.add_argument("--start", type=float, default=0, help="Clip start (seconds)")
    parser.add_argument("--end", type=float, default=30, help="Clip end (seconds)")
    parser.add_argument("--voiceover", default="voiceover.mp3", help="Optional voiceover MP3")
    parser.add_argument("--output", default=str(DEFAULT_OUT), help="Output MP4 path")
    args = parser.parse_args()

    try:
        result = search_and_process_video(
            args.keyword,
            start_time=args.start,
            end_time=args.end,
            voiceover_path=args.voiceover,
            output_path=args.output,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0 if result else 1


if __name__ == "__main__":
    raise SystemExit(main())
