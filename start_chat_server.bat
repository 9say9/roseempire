@echo off
title Rose Empire - Chat API Server (Gemini)
cd /d "%~dp0"

echo.
echo  Rose Empire Chat Server
echo  -----------------------
echo  Site + API: http://127.0.0.1:5000
echo  Requires GEMINI_API_KEY in .env
echo.

py -3.12 server.py 2>nul
if errorlevel 1 py -3 server.py
if errorlevel 1 python server.py

pause
