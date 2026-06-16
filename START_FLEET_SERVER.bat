@echo off
title Rose Empire Fleet SERVER - DO NOT CLOSE
cd /d "%~dp0"

echo.
echo ============================================
echo   Rose Empire Fleet SERVER
echo   DO NOT CLOSE THIS WINDOW
echo ============================================
echo.

where py >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed.
    pause
    exit /b 1
)

py -3 -m pip install -q -r requirements-fleet.txt

echo Starting on http://127.0.0.1:5050 ...
echo.
py -3 app.py

echo.
echo Server stopped.
pause
