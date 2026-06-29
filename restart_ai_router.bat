@echo off
title Rose Empire - Restart AI Router
cd /d "%~dp0"
setlocal enabledelayedexpansion

echo.
echo  ============================================================
echo   Restart AI Router (clears cooldowns, picks free port)
echo  ============================================================
echo.

for %%P in (8000 8001) do (
    for /f "tokens=5" %%Q in ('netstat -aon ^| findstr ":%%P" ^| findstr "LISTENING"') do (
        echo  Stopping PID %%Q on port %%P...
        taskkill /F /PID %%Q >nul 2>&1
    )
)

ping 127.0.0.1 -n 3 >nul

set "ROUTER_PORT=8000"
netstat -aon | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo  Port 8000 still busy - using 8001
    set "ROUTER_PORT=8001"
    for /f "tokens=5" %%P in ('netstat -aon ^| findstr ":8001" ^| findstr "LISTENING"') do taskkill /F /PID %%P >nul 2>&1
    ping 127.0.0.1 -n 2 >nul
)

echo  Starting router on port !ROUTER_PORT!
echo  Roo URL: http://127.0.0.1:!ROUTER_PORT!/v1
echo.

set AI_ROUTER_PORT=!ROUTER_PORT!
set AI_ROUTER_URL=http://127.0.0.1:!ROUTER_PORT!/v1
set AI_ROUTER_MODEL=boss-model

py -3 -m pip install -r ai_router\requirements.txt -q
start "" "%LOCALAPPDATA%\Programs\Ollama\Ollama.exe" 2>nul
ping 127.0.0.1 -n 2 >nul

start "Rose Empire - AI Router" py -3 ai_router\main.py

ping 127.0.0.1 -n 4 >nul
powershell -NoProfile -Command "try { $h = Invoke-RestMethod -Uri 'http://127.0.0.1:!ROUTER_PORT!/health' -TimeoutSec 10; Write-Host ('  Router OK | tools=' + $h.tools_passthrough + ' | cloud=' + $h.cloud_keys) -ForegroundColor Green } catch { Write-Host '  Router health check failed - see router window' -ForegroundColor Red }"

echo.
echo  If Roo still fails, run: fix_roo_router.bat
echo  (Close VS Code/Cursor first, then reopen)
echo.
pause
