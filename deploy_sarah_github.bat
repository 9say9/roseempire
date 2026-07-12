@echo off
title Rose Empire - Push Sarah widget to GitHub Pages
cd /d "%~dp0"

echo.
echo  Sync latest widget from sarah-widget-agent...
copy /Y "..\my plugin\sarah-widget-agent\src\public\widget.js" "sarah-widget.js" >nul

echo.
echo  Files going live:
echo    - index.html (new Sarah embed)
echo    - 404.html
echo    - sarah-widget.js
echo.
echo  Live in 1-2 min after push:
echo    https://www.roseempire.co.uk
echo    https://9say9.github.io/roseempire/
echo.

git add index.html 404.html sarah-widget.js SARAH-INSTALL.txt deploy_sarah_worker.bat deploy_sarah_github.bat
git status

set MSG=Add new Sarah AI widget (replaces broken chat-widget)
git commit -m "%MSG%"
if errorlevel 1 (
  echo Nothing to commit or commit failed.
  git push origin main
  goto done
)

git push origin main
if errorlevel 1 (
  echo Push failed - check git login.
  pause
  exit /b 1
)

echo.
echo  Done! Open https://www.roseempire.co.uk in 2 minutes.
:done
pause
