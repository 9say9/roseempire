@echo off
title Rose Empire - Create deploy zip
cd /d "%~dp0"

echo.
echo  Building deploy zip with Python...
echo.

C:\Windows\py.exe -3.12 create_deploy_zip.py
if errorlevel 1 (
    echo.
    echo  Python failed - trying PowerShell backup...
    set "OUT=rose-empire-deploy-backup.zip"
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path 'index.html','styles.css','app.js','site-config.js','quote-pricing.js','quote-shipping.js','quote-pdf.js','robots.txt','sitemap.xml','404.html','assets' -DestinationPath '%OUT%' -Force"
    if exist "%OUT%" (
        echo  SUCCESS: %OUT%
        start "" explorer /select,"%CD%\%OUT%"
    ) else (
        echo  FAILED - close any open zip file in Cursor and try again.
    )
) else (
    if exist "rose-empire-website-deploy.zip" (
        start "" explorer /select,"%CD%\rose-empire-website-deploy.zip"
    ) else (
        for %%F in (rose-empire-deploy-*.zip) do start "" explorer /select,"%CD%\%%F"
    )
)

echo.
pause
