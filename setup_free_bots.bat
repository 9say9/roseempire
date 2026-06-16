@echo off
title Rose Empire - Free Bot Setup
cd /d "%~dp0"

echo.
echo ======================================================
echo   Rose Empire - Free Bot Setup (Ollama + 3 bots)
echo ======================================================
echo.

where py >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install from https://python.org
    pause
    exit /b 1
)

echo [1/4] Installing Python dependencies...
py -3 -m pip install -q -r requirements-fleet.txt
if errorlevel 1 (
    echo ERROR: pip install failed
    pause
    exit /b 1
)

echo [2/4] Starting Ollama (free local AI)...
call "%~dp0start_ollama.bat" silent
if errorlevel 1 (
    echo.
    echo Ollama not ready. Run setup_rose_empire_ai.bat once to download models.
    pause
    exit /b 1
)

echo [3/4] Checking Ollama model...
set "OLLAMA=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
"%OLLAMA%" list 2>nul | findstr /I "qwen2.5-coder:7b" >nul
if errorlevel 1 (
    echo Model qwen2.5-coder:7b missing — pulling now (~4.7 GB, may take a while)...
    "%OLLAMA%" pull qwen2.5-coder:7b
)

echo [4/4] Testing all 3 bots...
py -3 fleet_orchestrator.py test-all
set TEST_RESULT=%errorLevel%

echo.
if %TEST_RESULT% equ 0 (
    echo ======================================================
    echo   SUCCESS - All 3 bots ready (100%% free with Ollama)
    echo ======================================================
    echo.
    echo   Dashboard:  run_ai_fleet.bat  then  http://127.0.0.1:5050
    echo   Roo Code:   Provider=Ollama, Model=qwen2.5-coder:7b
    echo   Cursor:     Ask Agent to run fleet_orchestrator.py
    echo.
) else (
    echo Some tests failed. Read output above, then retry.
)

pause
exit /b %TEST_RESULT%
