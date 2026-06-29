@echo off
title Rose Empire - Start Ollama
set "OLLAMA=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"

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
echo  Warming qwen2.5-coder:1.5b into memory for Roo Code / Zoo Code...
echo  (First warm-up can take 30-60 seconds — please wait)
py -3.12 -c "import urllib.request,json;p=json.dumps({'model':'qwen2.5-coder:1.5b','prompt':'OK','stream':False,'keep_alive':'1h','options':{'num_predict':3}}).encode();urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:11434/api/generate',data=p,headers={'Content-Type':'application/json'},method='POST'),timeout=300);print('  Model warm: qwen2.5-coder:1.5b ready')" 2>nul
if errorlevel 1 echo  Warm-up skipped — run ollama pull qwen2.5-coder:1.5b if model missing

echo.
echo  Ready for Roo Code, Continue, and run_rose_empire_bot.bat
echo  Roo Code settings: Provider=Ollama, URL=http://127.0.0.1:11434, Model=qwen2.5-coder:1.5b
echo.
if /I "%~1"=="silent" exit /b 0
pause
