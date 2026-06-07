@echo off
title Rose Empire - Google Search Console setup
cd /d "%~dp0"
echo.
echo Opening Google Search Console setup in Chromium...
echo Log in to Google if this is your first run.
echo.
py -3.12 setup_google_search_console.py
pause
