@echo off
title Rose Empire - Deploy LIVE (Netlify + AI chat)
cd /d "%~dp0"

echo.
echo ======================================================
echo   Rose Empire LIVE deploy (roseempire.co.uk)
echo   Includes Sarah + Alex chat via Netlify Functions
echo ======================================================
echo.

if exist "node_modules\.bin\netlify.cmd" (
    set "NETLIFY=node_modules\.bin\netlify.cmd"
) else (
    where netlify >nul 2>&1
    if errorlevel 1 (
        echo Netlify CLI not found. Run: npm install
        pause
        exit /b 1
    )
    set "NETLIFY=netlify"
)

echo Linking to Netlify site say9 if needed...
"%NETLIFY%" link --name say9 2>nul

echo.
echo Deploying to production...
"%NETLIFY%" deploy --prod --dir .
set "RC=%errorLevel%"

echo.
if %RC% equ 0 (
    echo DONE — Live at https://roseempire.co.uk
    echo.
    echo IMPORTANT: In Netlify dashboard add environment variable:
    echo   GEMINI_API_KEY = your Gemini key
    echo   GEMINI_MODEL   = gemini-2.5-flash-lite  ^(optional^)
    echo Then run: py -3 verify_live_chat.py
) else (
    echo Deploy failed. Try: netlify login
)
echo.
pause
exit /b %RC%
