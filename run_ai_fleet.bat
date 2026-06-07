@echo off
title Rose Empire - AI Fleet Command
cd /d "%~dp0"
set "FLEET_PORT=5050"
set "FLEET_URL=http://127.0.0.1:%FLEET_PORT%"

echo.
echo ======================================================
echo   Rose Empire AI Fleet Command
echo ======================================================
echo.

where py >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python not found. Install Python 3.12 first.
    pause
    exit /b 1
)

echo Installing dependencies...
py -3.12 -m pip install -q -r requirements-fleet.txt
if %errorLevel% neq 0 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo Stopping any old server on port 5050...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":5050" ^| findstr "LISTENING"') do taskkill /F /PID %%p >nul 2>&1

echo.
echo ======================================================
echo   Dashboard URL: %FLEET_URL%
echo   KEEP THIS WINDOW OPEN while using the dashboard.
echo ======================================================
echo.
start "" "%FLEET_URL%"
set FLEET_PORT=%FLEET_PORT%
py -3.12 app.py
