@echo off

title Rose Empire - Full Outreach Pipeline

cd /d "%~dp0"

echo.

echo  STEP 1 - Sarah scrape (skip if you already ran run_sarah_playwright.bat today)

echo  STEP 2 - Adeel qualify + enrich emails + export clean CSV

echo  STEP 3 - Build wholesale catalog PDF

echo  STEP 4 - James draft emails (dry-run first)

echo.

set /p RUN_SARAH="Run Sarah scrape now? (y/N): "

if /i "%RUN_SARAH%"=="y" (

  call run_sarah_playwright.bat

)

echo.

echo  --- Adeel: qualify, enrich, outreach CSV ---

py -3 lead_pipeline.py --qualify --enrich-emails --export-outreach

echo.

echo  --- Wholesale catalog PDF ---

py -3 generate_catalog_pdf.py

echo.

echo  --- Dry-run emails (with PDF attached) ---

py -3 send_leads_emails.py --dry-run --limit 5

echo.

echo  To send for real:  py -3 send_leads_emails.py --send --limit 5

echo  Call follow-up:    py -3 call_followup.py --export

echo.

pause

