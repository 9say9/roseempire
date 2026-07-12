@echo off
title Rose Empire - Deploy Sarah AI Worker (Cloudflare)
cd /d "%~dp0..\my plugin\sarah-widget-agent"

echo.
echo  Sarah Worker deploy
echo  -------------------
echo  Account: adeelcolchester (same as old rose-empire-chat)
echo.

where wrangler >nul 2>&1
if errorlevel 1 (
  echo Installing wrangler...
  call npm install wrangler --save-dev
)

echo Step 1: Create KV namespace (first time only)
echo   npx wrangler kv namespace create SITE_CONFIG
echo   Copy the id into wrangler.toml, then run this script again.
echo.

npx wrangler deploy
if errorlevel 1 (
  echo.
  echo Deploy failed. If KV error: run kv namespace create above.
  pause
  exit /b 1
)

echo.
echo  Worker live at: https://rose-empire-sarah.adeelcolchester.workers.dev
echo  Owner mode:    ?sarah_admin=rose-empire-owner-2026
echo.
pause
