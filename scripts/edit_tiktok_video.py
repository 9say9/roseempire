from pathlib import Path
import subprocess

ROOT = Path(r"D:\roseempire\demo-recordings")
filter_file = ROOT / "tiktok_filter.txt"
filter_file.write_text(
    "[0:v]setpts=0.72*PTS,crop=608:1080:656:0,scale=1080:960:flags=lanczos,setsar=1[top];\n"
    "[1:v]scale=1080:960:flags=lanczos,setsar=1[bot];\n"
    "[top][bot]vstack=inputs=2[stacked];\n"
    "[stacked]drawtext=fontfile=C\\\\:/Windows/Fonts/arialbd.ttf:text=Watch AI scrape 3 B2B clients for free:fontsize=46:fontcolor=white:borderw=5:bordercolor=black@0.85:x=(w-text_w)/2:y=100:enable=lt(t\\,4)[v1];\n"
    "[v1]drawtext=fontfile=C\\\\:/Windows/Fonts/arialbd.ttf:text=Rose Empire lead machine:fontsize=30:fontcolor=0x7DD3FC:x=(w-text_w)/2:y=170:enable=lt(t\\,4)[out]\n",
    encoding="utf-8",
)
FFMPEG = Path(r"C:\Users\Adeel\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe")
OUT = ROOT / "rose-empire-tiktok-edit.mp4"
cmd = [str(FFMPEG), "-y", "-i", str(ROOT / "rose-empire-demo-20260620-152139.webm"), "-loop", "1", "-framerate", "25", "-i", str(ROOT / "crm_bottom.png"), "-filter_complex_script", str(filter_file), "-map", "[out]", "-an", "-t", "33", "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUT)]
print("Rendering...")
subprocess.run(cmd, check=True)
print("Done", OUT)
