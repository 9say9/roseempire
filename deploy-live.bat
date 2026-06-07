@echo off
title Rose Empire - DEPRECATED Netlify deploy
cd /d "%~dp0"
echo.
echo  Netlify is no longer used. Rose Empire is on GitHub Pages.
echo  Run deploy-github.bat instead.
echo.
start "" notepad GITHUB_PAGES.md
call deploy-github.bat
