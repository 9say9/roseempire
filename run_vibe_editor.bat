@echo off
title Rose Empire - Vibe Editor (YouTube to TikTok)
cd /d "%~dp0"

echo.
echo  YouTube search -^> 9:16 crop -^> mirror -^> voiceover mix
echo.

py -3 -m pip install -r requirements-vibe.txt -q
if errorlevel 1 (
    echo pip install failed
    pause
    exit /b 1
)

if "%~1"=="" (
    echo Usage: run_vibe_editor.bat "search keywords" [start_sec] [end_sec]
    echo Example:
    echo   run_vibe_editor.bat "World Cup 2026 England highlights" 15 45
    pause
    exit /b 1
)

set "KW=%~1"
set "START=0"
set "END=30"
if not "%~2"=="" set "START=%~2"
if not "%~3"=="" set "END=%~3"

py -3 vibe_editor.py "%KW%" --start %START% --end %END%
if errorlevel 1 (
    echo Failed.
    pause
    exit /b 1
)

echo.
echo Output: vibe-output\tiktok_output.mp4
start "" "vibe-output\tiktok_output.mp4"
pause
