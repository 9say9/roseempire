@echo off
title Rose Empire - Fix Microsoft 365 Email
cd /d "%~dp0"
py -3 -m pip install -q msal playwright requests python-dotenv
py -3 -m playwright install chromium
py -3 fix_ms365_email.py
pause
