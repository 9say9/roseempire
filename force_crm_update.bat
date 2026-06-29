@echo off
title Rose Empire - FORCE CRM Update
cd /d "%~dp0"

echo.
echo  ============================================================
echo   FORCE UPDATE to new CRM (Automation Hub v1.2)
echo   Fixes: old dark "Mission Command" / Alex-era dashboard
echo  ============================================================
echo.
echo  Folder: %CD%
echo.
echo  This will reset code to GitHub main (keeps your .env file).
pause

where git >nul 2>&1 || (echo ERROR: Install Git first & pause & exit /b 1)

if not exist ".git" (
    echo ERROR: Not a git repo. Clone fresh:
    echo   git clone https://github.com/9say9/roseempire.git
    pause & exit /b 1
)

echo.
echo [1/6] Backup .env if present...
if exist ".env" copy /Y ".env" ".env.backup" >nul

echo [2/6] Stop old servers on ports 5050 and 5000...
for /f "tokens=5" %%p in ('netstat -ano 2^>nul ^| findstr ":5050" ^| findstr "LISTENING"') do taskkill /F /PID %%p >nul 2>&1
for /f "tokens=5" %%p in ('netstat -ano 2^>nul ^| findstr ":5000" ^| findstr "LISTENING"') do taskkill /F /PID %%p >nul 2>&1
timeout /t 2 /nobreak >nul

echo [3/6] git fetch + hard reset to origin/main...
git fetch origin main
git reset --hard origin/main
if errorlevel 1 (echo git reset failed & pause & exit /b 1)

echo [4/6] Restore .env backup...
if exist ".env.backup" copy /Y ".env.backup" ".env" >nul

echo [5/6] Install Python deps...
py -3 -m pip install -q -r requirements-fleet.txt

echo [6/6] Verify CRM files...
findstr /C:"Automation Hub v1.2" templates\index.html >nul
if errorlevel 1 (
    echo ERROR: templates\index.html still OLD after git reset.
    echo Wrong repo? Use: git clone https://github.com/9say9/roseempire.git
    pause & exit /b 1
)
if not exist dashboard_api.py (
    echo ERROR: dashboard_api.py missing
    pause & exit /b 1
)
echo CRM files OK.

echo.
echo Starting NEW dashboard server...
start "Rose Empire Fleet SERVER" cmd /k "cd /d %~dp0 && py -3 app.py"
timeout /t 5 /nobreak >nul
start "" "http://127.0.0.1:5050/api/version"
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:5050"

echo.
echo  SUCCESS - browser should show LIGHT theme "Automation Hub v1.2"
echo  NOT the dark "Mission Command" screen.
echo.
echo  If still wrong, you have TWO roseempire folders - delete the old one.
echo  Search PC for:  dir /s /b roseempire\app.py
echo.
pause
