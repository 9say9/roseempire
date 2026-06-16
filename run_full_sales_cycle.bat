@echo off
title Rose Empire - Full Sales Cycle
cd /d "%~dp0"
echo.
echo  Sarah scrape -^> Adeel qualify -^> James pitch -^> SMTP send
echo  DRY RUN by default. Add --send to email live leads.
echo  Add --scrape to refresh Google Maps leads first.
echo.
py -3 sales_engine.py %*
pause
