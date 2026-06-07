@echo off
title Rose Empire — Enable GitHub Pages
cd /d "%~dp0"
echo.
echo  Opens GitHub in Chromium to turn on Pages for 9say9/roseempire
echo  Log in if prompted, then follow on-screen instructions.
echo.
py -3 enable_github_pages.py
pause
