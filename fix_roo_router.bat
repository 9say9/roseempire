@echo off
title Fix Roo + Zoo -> AI Router
cd /d "%~dp0"

echo.
echo  Pointing Roo Code + Zoo Code at local AI Router
echo  URL: http://127.0.0.1:8001/v1  Model: gemini-free
echo  Router profile: rose-router
echo.
echo  Close VS Code/Cursor completely before patching.
pause

py -3 "%~dp0_fix_roo_router_config.py"
if errorlevel 1 (
    echo Patch failed.
    pause
    exit /b 1
)

echo.
echo  Start the router with restart_ai_router.bat
echo  Then reopen VS Code/Cursor and test Roo/Zoo with:
echo  Provider = OpenAI Compatible
echo  Base URL = http://127.0.0.1:8001/v1
echo  API Key = local
echo  Model = gemini-free
pause
