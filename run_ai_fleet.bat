@echo off
title Rose Empire - AI Fleet Command
cd /d "%~dp0"
set FLEET_PORT=5050
set FLEET_URL=http://127.0.0.1:%FLEET_PORT%

echo.
echo ======================================================
echo   Rose Empire AI Fleet Command
echo ======================================================
echo.

where py >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install from https://python.org
    pause
    exit /b 1
)

echo [1/4] Installing dependencies...
py -3 -m pip install -q -r requirements-fleet.txt
if errorlevel 1 (
    echo ERROR: pip install failed
    pause
    exit /b 1
)

echo [2/5] Starting AI Router (key rotation + Ollama fallback)...
start "Rose Empire AI Router" cmd /k "cd /d %~dp0 && py -3 -m pip install -q -r ai_router\requirements.txt && py -3 ai_router\main.py"
timeout /t 2 /nobreak >nul

echo [3/5] Stopping old server on port %FLEET_PORT%...
for /f "tokens=5" %%p in ('netstat -ano 2^>nul ^| findstr ":%FLEET_PORT%" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%p >nul 2>&1
)
timeout /t 1 /nobreak >nul

echo [4/5] Starting fleet server - keep SERVER window open...
start "Rose Empire Fleet SERVER" cmd /k "cd /d %~dp0 && title Rose Empire Fleet SERVER && py -3 app.py || pause"

echo [5/5] Waiting for dashboard...
set /a WAIT=0
:waitloop
set /a WAIT+=1
powershell -NoProfile -Command "try { (Invoke-WebRequest -Uri '%FLEET_URL%/health' -UseBasicParsing -TimeoutSec 2).StatusCode | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
if %errorLevel% equ 0 goto openbrowser
if %WAIT% geq 30 (
    echo.
    echo ERROR: Server did not start within 60 seconds.
    echo Look at the "Rose Empire Fleet SERVER" window for the error.
    echo Manual start: cd /d %~dp0 ^& py -3 app.py
    pause
    exit /b 1
)
timeout /t 2 /nobreak >nul
goto waitloop

:openbrowser
echo.
echo Server online. Opening browser...
start "" "%FLEET_URL%"
echo.
echo Dashboard: %FLEET_URL%
echo IMPORTANT: Keep "Rose Empire Fleet SERVER" window open.
echo.
pause
