@echo off
title Sarah - Playwright fresh leads (Roo Code)
cd /d "%~dp0"
echo.
echo  Sarah: 5 fresh Google Maps leads via Playwright
echo  If a browser opens, click Accept on Google consent once.
echo.
py -3 fleet_scraper.py --limit 5 --sources google_maps --headed --mission "care homes boutique hotels Manchester UK"
echo.
pause
