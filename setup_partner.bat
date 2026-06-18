@echo off
title Rose Empire - Partner Setup
cd /d "%~dp0"

echo.
echo ======================================================
echo   Rose Empire Partner Setup
echo   For GitHub collaborators - scraping + email bots
echo ======================================================
echo.

set FAIL=0

where py >nul 2>&1 || (echo [MISSING] Python - install from https://python.org & set FAIL=1)
where git >nul 2>&1 || (echo [MISSING] Git - install from https://git-scm.com & set FAIL=1)
if not exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
    echo [MISSING] Ollama - install from https://ollama.com/download
    set FAIL=1
)

if %FAIL%==1 (
    echo.
    echo Install missing tools, then re-run setup_partner.bat
    pause
    exit /b 1
)

echo [1/5] Python packages...
py -3 -m pip install -q -r requirements-fleet.txt
if errorlevel 1 (
    echo ERROR: pip install failed
    pause
    exit /b 1
)

echo [2/5] Playwright Chromium...
py -3 -m playwright install chromium

echo [3/5] Lead data folder...
if not exist "linkedin-outreach" mkdir "linkedin-outreach"

echo [4/5] Environment file...
if not exist ".env" (
    copy /Y ".env.example" ".env" >nul
    echo Created .env from template - ask Adeel for INFO_EMAIL and EMAIL_PASSWORD
) else (
    echo .env already exists
)

echo [5/5] Ollama check...
call "%~dp0start_ollama.bat" silent
if errorlevel 1 (
    echo.
    echo Ollama not ready. After setup, run: setup_rose_empire_ai.bat
    goto done
)

set "OLLAMA=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
"%OLLAMA%" list 2>nul | findstr /I "qwen2.5-coder:7b" >nul
if errorlevel 1 (
    echo.
    echo Model qwen2.5-coder:7b not installed yet.
    echo Run setup_rose_empire_ai.bat once ^(~10 GB download^).
)

:done
echo.
echo ======================================================
echo   Partner setup complete
echo ======================================================
echo.
echo   Next steps:
echo     1. Get .env secrets from Adeel ^(secure message^)
echo     2. setup_rose_empire_ai.bat  ^(first time only^)
echo     3. test_bots.bat
echo     4. Open folder in Cursor - Agent reads AGENTS.md
echo.
echo   Guide: PARTNER_BOT_SETUP.md
echo.
pause
exit /b 0
