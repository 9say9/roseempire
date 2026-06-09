@echo off
title Rose Empire - AI Setup (Ollama models)
set "OLLAMA=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"

echo.
echo  Rose Empire AI Setup
echo  ====================
echo.

if not exist "%OLLAMA%" (
    echo  ERROR: Ollama not found at %OLLAMA%
    echo  Install from https://ollama.com/download
    pause
    exit /b 1
)

REM Use the Ollama desktop app only — do NOT start a second "ollama serve" process.
echo  Starting Ollama app...
start "" "%LOCALAPPDATA%\Programs\Ollama\Ollama.exe"
echo  Waiting for Ollama API...
timeout /t 8 /nobreak >nul

powershell -NoProfile -Command "try { (Invoke-WebRequest -Uri 'http://127.0.0.1:11434/api/tags' -UseBasicParsing -TimeoutSec 10).StatusCode | Out-Null; exit 0 } catch { exit 1 }"
if errorlevel 1 (
    echo  ERROR: Ollama API not responding. Open Ollama from the Start menu, then re-run this script.
    pause
    exit /b 1
)

echo  Ollama API: ONLINE
echo.
echo  NOTE: Large models take 30-90 minutes on slow internet.
echo  The window may look frozen — that is normal. Do NOT close it.
echo.

call :pull_if_missing qwen2.5-coder:1.5b "Qwen2.5 Coder 1.5B (fast autocomplete — ~1 GB)"
if errorlevel 1 goto failed

call :pull_if_missing qwen2.5-coder:7b "Qwen2.5 Coder 7B (main coding brain — ~4.7 GB)"
if errorlevel 1 goto failed

call :pull_if_missing llama3.1:8b "Llama 3.1 8B (backup chat — ~4.7 GB)"
if errorlevel 1 goto failed

echo.
echo  Installed models:
"%OLLAMA%" list

echo.
echo  SUCCESS — Ollama models ready.
echo.
echo  Next steps:
echo    1. Run start_ollama.bat before using local AI
echo    2. Optional: VS Code + Continue extension (config: Rose Empire AI Stack)
echo    3. Or use run_rose_empire_bot.bat / Cursor for AI coding
echo.
echo  Config file: %USERPROFILE%\.continue\config.yaml
echo.
pause
exit /b 0

:pull_if_missing
set "MODEL=%~1"
set "LABEL=%~2"
"%OLLAMA%" list 2>nul | findstr /I /C:"%MODEL%" >nul
if not errorlevel 1 (
    echo  [SKIP] %MODEL% already installed
    exit /b 0
)
echo.
echo  Pulling %LABEL%...
"%OLLAMA%" pull %MODEL%
exit /b %errorlevel%

:failed
echo.
echo  FAILED — download interrupted or no internet.
echo  Fix: close this window, run start_ollama.bat, then run this script again.
echo  Already-downloaded models are kept — it will skip them and resume.
pause
exit /b 1
