@echo off
title Rose Empire - Local Preview Server
cd /d "%~dp0"

echo.
echo  ============================================
echo   Rose Empire - Website Preview
echo  ============================================
echo.
echo  Keep this window OPEN while your partner views the site.
echo.

set PORT=8765

REM Show local network address for same-WiFi sharing
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    goto :foundip
)
:foundip
set IP=%IP:~1%

echo  On THIS computer:     http://localhost:%PORT%
echo  Same WiFi / network:  http://%IP%:%PORT%
echo.
echo  Partner elsewhere?   See SHARE_WITH_PARTNER.md - use Netlify Drop.
echo.
echo  Press Ctrl+C to stop the server.
echo  ============================================
echo.

py -3.12 -m http.server %PORT%
if errorlevel 1 (
    echo.
    echo  Python 3.12 not found. Trying default py launcher...
    py -m http.server %PORT%
)

pause
