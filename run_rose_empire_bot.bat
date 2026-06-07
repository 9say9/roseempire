@echo off
title Rose Empire AI Bot
cd /d "%~dp0"

echo.
echo ======================================================
echo   Rose Empire AI Bot
echo ======================================================
echo.

call "%~dp0start_ollama.bat" silent
if %errorLevel% neq 0 (
    echo ERROR: Could not start Ollama.
    pause
    exit /b 1
)

echo Waiting for Ollama API...
set /a tries=0
:waitloop
set /a tries+=1
powershell -NoProfile -Command "try { (Invoke-WebRequest -Uri 'http://127.0.0.1:11434/api/tags' -UseBasicParsing -TimeoutSec 3).StatusCode | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
if %errorLevel% equ 0 goto ready
if %tries% geq 15 (
    echo ERROR: Ollama did not respond. Open Ollama from the Start menu, then retry.
    pause
    exit /b 1
)
timeout /t 2 /nobreak >nul
goto waitloop

:ready
echo Warming up AI model (first reply may take 30-60 seconds)...
"%LOCALAPPDATA%\Programs\Ollama\ollama.exe" run qwen2.5-coder:1.5b "ready" >nul 2>&1
echo Ollama is online.
echo.
echo Starting chat bot. Type exit to quit.
echo.

py -3.12 run_rose_empire_bot.py
pause
