@echo off
title Rose Empire - Test All 3 Bots
cd /d "%~dp0"

echo.
echo  Testing Sarah, James, and Adeel (free stack)...
echo.

call "%~dp0start_ollama.bat" silent
py -3 fleet_orchestrator.py test-all
pause
