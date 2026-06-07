@echo off
title Rose Empire - Deploy chat API (Cloudflare Worker)
cd /d "%~dp0"

echo.
echo  Rose Empire Chat Worker (replaces Netlify function)
echo  Requires: wrangler login + wrangler secret put GEMINI_API_KEY
echo.

copy /Y "chat-prompts.json" "cloudflare\chat-worker\src\chat-prompts.json" >nul
cd cloudflare\chat-worker

where wrangler >nul 2>&1
if errorlevel 1 (
    echo Installing wrangler...
    npm install -g wrangler
)

wrangler deploy
if errorlevel 1 (
    echo Deploy failed. Run: wrangler login
    pause
    exit /b 1
)

echo.
echo Copy the workers.dev URL into site-config.js -^> cloudflareChatApi
echo Then run deploy-github.bat
pause
