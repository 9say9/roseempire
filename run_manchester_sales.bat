@echo off
title Rose Empire - Manchester Sales Pipeline
cd /d "%~dp0"
echo.
echo  Step 1: Qualify Manchester leads (Google Maps + LinkedIn CSVs)
echo  Step 2: Find emails on business websites
echo  Step 3: Draft or send outreach pointing to roseempire.co.uk (Sarah chat)
echo.
echo  DRY RUN by default. To actually send emails add:  --send
echo  Requires .env with INFO_EMAIL and EMAIL_PASSWORD for Microsoft 365 SMTP.
echo.
py -3 manchester_sales_pipeline.py %*
pause
