@echo off
title Rose Empire - Chat API Server (Gemini)
cd /d "%~dp0"

echo.
echo  Rose Empire Chat Server
echo  -----------------------
echo  Site + API: http://127.0.0.1:5000
echo.

if not exist ".env" (
    echo  ERROR: .env file missing in this folder.
    echo  Create .env with: GEMINI_API_KEY=your_key_here
    echo.
    pause
    exit /b 1
)

findstr /B /C:"GEMINI_API_KEY=" .env >nul 2>&1
if errorlevel 1 (
    echo  ERROR: .env must contain GEMINI_API_KEY=...
    echo.
    pause
    exit /b 1
)

echo  Starting server... Keep this window OPEN while using the chat.
echo  Open http://127.0.0.1:5000 in your browser (not the GitHub Pages URL).
echo.

py -3 server.py
if errorlevel 1 (
    echo.
    echo  Python failed. Install dependencies:
    echo    py -3 -m pip install flask requests
    echo.
    pause
    exit /b 1
)

pause
