@echo off
title Rose Empire - One-Click Local Launcher
cd /d "%~dp0"

where py >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.10+ and try again.
    pause
    exit /b 1
)

py -3 run_local_fleet.py %*
exit /b %errorlevel%
