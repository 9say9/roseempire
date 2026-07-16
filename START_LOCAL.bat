@echo off
title Rose Empire — local site
cd /d "%~dp0"

where py >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed. Install Python 3.12+, then re-run.
    pause
    exit /b 1
)

if not exist ".env" (
    copy /Y ".env.example" ".env" >nul
    echo Created .env from .env.example — add your Stripe keys before checkout.
)

py -3 -m pip install -q -r requirements.txt
echo.
echo Starting http://127.0.0.1:5000 ...
echo.
start "" "http://127.0.0.1:5000"
py -3 server.py
pause
