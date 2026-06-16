@echo off

title Sarah - UK Hotel Lead Scrape

cd /d "%~dp0"

echo.

echo  Sarah: UK hotels via Google Maps + email enrichment

echo  Cities: 12 major UK cities, 6 hotels each (adjust with --max-cities / --per-city)

echo  Output: linkedin-outreach\uk_hotel_leads.csv

echo.

echo  If browser opens, accept Google consent once.

echo.

py -3 scrape_uk_hotels.py --max-cities 12 --per-city 6 --headed

echo.

echo  Export for outreach:

echo    py -3 outreach_leads.py --qualified linkedin-outreach\uk_hotel_leads.csv --out linkedin-outreach\uk_hotel_outreach.csv

echo.

pause

