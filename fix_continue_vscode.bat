@echo off
title Fix VS Code Continue - Rose Empire
echo.
echo  Fixing Continue stuck on API config...
echo.

REM Ensure Ollama is running
call "%~dp0start_ollama.bat" silent

echo  1. Cloud models removed from main config (fixes API key hang)
echo  2. Main config: C:\Users\ADLSH\.continue\config.yaml
echo  3. Optional cloud config: config-cloud.yaml (needs API keys)
echo.
echo  In VS Code:
echo    - Open Continue sidebar
echo    - Dropdown at top: select "Rose Empire AI Stack"
echo    - NOT "Default Assistant" or "Local Agent"
echo    - Click gear icon -^> Reload config
echo    - Pick model: Qwen2.5 Coder 7B (Local Rose Empire)
echo.
echo  If still stuck: close VS Code completely and reopen antigravity.code-workspace
echo.
pause
