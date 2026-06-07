@echo off
title Rose Empire - GitHub Pages (sign in once)
cd /d "%~dp0"
echo.
echo  STEP 1: Sign in to GitHub as 9say9 when the browser opens.
echo  STEP 2: The script will open Settings ^> Pages and save branch main.
echo  STEP 3: Wait until https://9say9.github.io/roseempire/ is live.
echo.
py -3 enable_github_pages.py
if errorlevel 1 (
    echo.
    echo  Manual fallback:
    echo  https://github.com/9say9/roseempire/settings/pages
    echo  Source: Deploy from a branch -^> main -^> / (root) -^> Save
    echo.
)
pause
