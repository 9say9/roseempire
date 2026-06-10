@echo off
title Rose Empire - Website + Chat Bots
cd /d "%~dp0"

echo.
echo  Rose Empire — local site with working Alex ^& Sarah chat
echo  ========================================================
echo.

if not exist ".env" (
    echo  ERROR: .env missing. Add GEMINI_API_KEY=your_key
    pause
    exit /b 1
)

echo  Starting chat server on http://127.0.0.1:5000 ...
echo  Keep this window OPEN. Chat bots respond on this URL only.
echo  For live GitHub Pages chat, run deploy_chat_worker.bat after wrangler login.
echo.

start "" "http://127.0.0.1:5000"
py -3 server.py
