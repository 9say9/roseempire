@echo off
title Rose Empire - AI Setup (Ollama models)
set "OLLAMA=C:\Users\ADLSH\AppData\Local\Programs\Ollama\ollama.exe"

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

echo  Starting Ollama service...
start "" /B "%OLLAMA%" serve
timeout /t 3 /nobreak >nul

echo.
echo  Pulling Qwen2.5 Coder 7B ^(main coding brain — ~4.7 GB^)...
"%OLLAMA%" pull qwen2.5-coder:7b
if errorlevel 1 goto failed

echo.
echo  Pulling Qwen2.5 Coder 1.5B ^(fast autocomplete — ~1 GB^)...
"%OLLAMA%" pull qwen2.5-coder:1.5b
if errorlevel 1 goto failed

echo.
echo  Pulling Llama 3.1 8B ^(backup chat — ~4.7 GB^)...
"%OLLAMA%" pull llama3.1:8b
if errorlevel 1 goto failed

echo.
echo  Installed models:
"%OLLAMA%" list

echo.
echo  SUCCESS — Ollama models ready.
echo.
echo  Next steps:
echo    1. Open VS Code
echo    2. Install extension: Continue ^(Continue.continue^)
echo    3. Open Continue sidebar ^- select config: Rose Empire AI Stack
echo    4. Add cloud API keys in Continue ^> Settings ^> Secrets
echo.
echo  Config file: C:\Users\ADLSH\.continue\config.yaml
echo.
pause
exit /b 0

:failed
echo.
echo  FAILED — check internet connection and try again.
pause
exit /b 1
