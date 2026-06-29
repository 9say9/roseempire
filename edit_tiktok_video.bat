@echo off
title Rose Empire - Edit TikTok Video
cd /d "%~dp0"
echo Rendering TikTok edit from latest demo recording...
py -3 scripts\edit_tiktok_video.py
if errorlevel 1 exit /b 1
echo.
echo Opening edited video...
start "" "demo-recordings\rose-empire-tiktok-edit.mp4"
echo Done.
