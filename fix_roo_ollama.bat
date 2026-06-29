@echo off
title Fix Roo Code + Zoo Code - Ollama
cd /d "%~dp0"
set "OLLAMA=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"

echo.
echo  ============================================
echo   FIX ROO CODE + ZOO CODE - Ollama
echo   Model: qwen2.5-coder:1.5b (fast local coding — fits this PC)
echo  ============================================
echo.
echo  PROBLEM FOUND:
echo    Both extensions were still on old "default" profile
echo    from your previous PC (Qwen Code on port 52057).
echo    Ollama on port 11434 IS working on this PC.
echo.

if not exist "%OLLAMA%" (
    echo  ERROR: Ollama not found. Install from https://ollama.com
    pause
    exit /b 1
)

echo  [1/2] Patching Roo Code + Zoo Code + restarting Ollama...
py -3.12 -m pip install pycryptodome pywin32 -q
py -3.12 "%~dp0_fix_roo_zoo_config.py"
if errorlevel 1 (
    echo  Config patch failed.
    pause
    exit /b 1
)

echo.
echo  [2/2] DONE - close Cursor fully, reopen, then test Roo/Zoo.
echo.
echo  Settings are already fixed. You do NOT need to find them manually.
echo  Just close Cursor completely and open it again.
echo.
pause
