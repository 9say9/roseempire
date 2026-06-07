@echo off
title Sync Rose Empire knowledge to Ollama bot
cd /d "%~dp0"

echo.
echo  Rose Empire knowledge lives in:
echo    C:\Users\ADLSH\.continue\knowledge\
echo    C:\Users\ADLSH\.continue\rules\rose-empire-agent.md
echo.
echo  Loaded automatically by:
echo    - VS Code Continue (config: Rose Empire AI Stack)
echo    - run_rose_empire_bot.bat
echo.
echo  To refresh after site changes, re-run this script or edit knowledge files.
echo.

C:\Windows\py.exe -3.12 -c "from pathlib import Path; d=Path(r'C:\Users\ADLSH\.continue\knowledge'); print('Knowledge files:'); [print('  OK', f.name) for f in sorted(d.glob('*.md'))]"

echo.
pause
