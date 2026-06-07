@echo off
title Rose Empire - Deploy to Netlify (production)
cd /d "%~dp0"

echo.
echo ======================================================
echo   Rose Empire - Production deploy (roseempire.co.uk)
echo ======================================================
echo.

where netlify >nul 2>&1
if %errorLevel% neq 0 (
    if exist "node_modules\.bin\netlify.cmd" (
        set "NETLIFY=node_modules\.bin\netlify.cmd"
    ) else (
        echo Netlify CLI not found. Run once:
        echo   npm install
        echo   npm run login
        echo   npm run link
        pause
        exit /b 1
    )
) else (
    set "NETLIFY=netlify"
)

if not exist ".netlify\state.json" (
    echo Project not linked yet. Run:
    echo   netlify login
    echo   netlify link --name say9
    pause
    exit /b 1
)

echo Deploying to production...
echo.
"%NETLIFY%" deploy --prod --dir .
set "RC=%errorLevel%"
echo.
if %RC% equ 0 (
    echo Done. Live at https://www.roseempire.co.uk
    echo Backup URL: https://say9.netlify.app
) else (
    echo Deploy failed. Try: netlify status
)
echo.
pause
exit /b %RC%
