@echo off
title Rose Empire - New PC Setup Check
cd /d "%~dp0"

echo.
echo  Rose Empire New PC Setup Verification
echo  =====================================
echo.

set FAIL=0

where node >nul 2>&1 || (echo [MISSING] Node.js - install from https://nodejs.org & set FAIL=1)
where git >nul 2>&1 || (echo [MISSING] Git - install from https://git-scm.com & set FAIL=1)
where py >nul 2>&1 || (echo [MISSING] Python - install Python 3.12 from https://python.org & set FAIL=1)
if not exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (echo [MISSING] Ollama - install from https://ollama.com/download & set FAIL=1)

echo.
echo  Checking versions...
where node >nul 2>&1 && node --version
where git >nul 2>&1 && git --version
where py >nul 2>&1 && py -3.12 --version
if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" --version
where wrangler >nul 2>&1 && wrangler --version

echo.
echo  Installing/updating Python packages...
py -3.12 -m pip install -q -r requirements-fleet.txt
py -3.12 -m playwright install chromium

echo.
echo  Continue AI config: %USERPROFILE%\.continue\config.yaml
if exist "%USERPROFILE%\.continue\config.yaml" (echo [OK] Continue config found) else (echo [MISSING] Continue config)

echo.
if %FAIL%==0 (
    echo  Core tools OK. Next steps:
    echo    1. Run setup_partner.bat or setup_rose_empire_ai.bat ^(~10 GB models^)
    echo    2. Copy .env from .env.example ^(get secrets from repo owner^)
    echo    3. Open in Cursor - Agent reads AGENTS.md
    echo    4. Guide: PARTNER_BOT_SETUP.md
) else (
    echo  Some tools missing - install them first.
)
echo.
pause
