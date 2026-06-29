@echo off
title Rose Empire - Test Demo Video
cd /d "%~dp0"

echo.
echo  ============================================================
echo   Record a test TikTok/Shorts demo (local Playwright video)
echo  ============================================================
echo.
echo  Opens browser, scrapes 3 leads on Google Maps, records video,
echo  then shows CRM overlay page for split-screen proof footage.
echo.
echo  Accept Google consent if prompted.
echo.

py -3 -m pip install playwright -q 2>nul
py -3 -m playwright install chromium 2>nul

echo  Recording horizontal 16:9 (crop to 9:16 in CapCut)...
echo.

py -3 scripts\record_demo_video.py --limit 3 --open

echo.
pause
