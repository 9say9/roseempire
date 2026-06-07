@echo off
title Rose Empire - Start Ollama
set "OLLAMA=C:\Users\ADLSH\AppData\Local\Programs\Ollama\ollama.exe"

echo.
echo  Starting Ollama AI server...
echo.

if not exist "%OLLAMA%" (
    echo  ERROR: Ollama not found. Install from https://ollama.com/download
    pause
    exit /b 1
)

REM Start Ollama app if not already running (Windows service/tray)
start "" "%LOCALAPPDATA%\Programs\Ollama\Ollama.exe" 2>nul

timeout /t 2 /nobreak >nul

REM Verify API is up
powershell -NoProfile -Command "try { (Invoke-WebRequest -Uri 'http://127.0.0.1:11434/api/tags' -UseBasicParsing -TimeoutSec 5).StatusCode | Out-Null; Write-Host '  Ollama API: ONLINE' -ForegroundColor Green } catch { Write-Host '  Waiting for Ollama...' -ForegroundColor Yellow; Start-Sleep 5; (Invoke-WebRequest -Uri 'http://127.0.0.1:11434/api/tags' -UseBasicParsing).StatusCode | Out-Null; Write-Host '  Ollama API: ONLINE' -ForegroundColor Green }"

echo.
echo  Models installed:
"%OLLAMA%" list

echo.
echo  Ready for VS Code Continue (config: Rose Empire AI Stack)
echo  Main model: qwen2.5-coder:7b
echo.
if /I "%~1"=="silent" exit /b 0
pause
