@echo off
title Rose Empire - Start Bots
cd /d "%~dp0"

echo.
echo Step 1: Starting fleet SERVER in a new window...
echo        KEEP that window open!
echo.
start "Rose Empire Fleet SERVER" "%~dp0START_FLEET_SERVER.bat"

echo Step 2: Waiting for server...
set /a N=0
:wait
set /a N+=1
powershell -NoProfile -Command "try{(Invoke-WebRequest -Uri 'http://127.0.0.1:5050/health' -UseBasicParsing -TimeoutSec 2).StatusCode|Out-Null;exit 0}catch{exit 1}" >nul 2>&1
if %errorLevel% equ 0 goto ok
if %N% geq 25 (
    echo.
    echo SERVER NOT READY. Open START_FLEET_SERVER.bat manually and read errors.
    pause
    exit /b 1
)
timeout /t 2 /nobreak >nul
goto wait

:ok
echo Step 3: Opening dashboard in browser...
start "" "http://127.0.0.1:5050"
echo.
echo DONE. Dashboard: http://127.0.0.1:5050
echo Keep "Rose Empire Fleet SERVER" window open.
echo.
pause
