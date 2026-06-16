@echo off

title Rose Empire - Deploy UK Certificate

cd /d "%~dp0"

echo.

echo  Drop your UK test report into any of:

echo    %~dp0certificate upload

echo    %~dp0certificates

echo    D:\roseempire certificates

echo.

echo  Supported: PDF, JPG, PNG

echo.

py -3 deploy_uk_certificate.py

echo.

pause

