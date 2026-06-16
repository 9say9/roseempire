from pathlib import Path

# app.py - load dotenv early
app = Path("d:/roseempire/app.py")
t = app.read_text(encoding="utf-8")
if "load_dotenv" not in t:
    t = t.replace(
        "import os\n\nfrom flask",
        "import os\n\nfrom dotenv import load_dotenv\n\nload_dotenv()\n\nfrom flask",
    )
    app.write_text(t, encoding="utf-8")
    print("app.py: dotenv added")

# fleet_ai.py - load dotenv
fa = Path("d:/roseempire/fleet_ai.py")
ft = fa.read_text(encoding="utf-8")
if "load_dotenv" not in ft:
    ft = "import os\nfrom dotenv import load_dotenv\nload_dotenv()\n\n" + ft.replace("import os\n\nimport requests", "import requests")
    fa.write_text(ft, encoding="utf-8")
    print("fleet_ai.py: dotenv added")

# run_ai_fleet.bat - reliable start
bat = r'''@echo off
title Rose Empire - AI Fleet Command
cd /d "%~dp0"
set FLEET_PORT=5050
set FLEET_URL=http://127.0.0.1:%FLEET_PORT%

echo.
echo ======================================================
echo   Rose Empire AI Fleet Command
echo ======================================================
echo.

where py >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install from https://python.org
    pause
    exit /b 1
)

echo Installing dependencies...
py -3 -m pip install -q -r requirements-fleet.txt
if errorlevel 1 (
    echo ERROR: pip install failed
    pause
    exit /b 1
)

echo Stopping old server on port %FLEET_PORT%...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%FLEET_PORT%" ^| findstr "LISTENING"') do taskkill /F /PID %%p >nul 2>&1

echo.
echo Starting server... (browser opens when ready)
echo KEEP THIS WINDOW OPEN.
echo.

start "Rose Empire Fleet Server" /MIN cmd /c "cd /d %~dp0 && py -3 app.py"

powershell -NoProfile -Command "$ok=$false; for($i=0;$i -lt 45;$i++){ try { $r=Invoke-WebRequest -Uri '%FLEET_URL%/health' -UseBasicParsing -TimeoutSec 2; if($r.StatusCode -eq 200){$ok=$true; break} } catch {} Start-Sleep 2 }; if($ok){ Start-Process '%FLEET_URL%' } else { Write-Host 'Server did not start - check the Fleet Server window for errors.' }"

echo.
echo Dashboard: %FLEET_URL%
echo If browser did not open, paste that URL manually.
echo.
pause
'''
Path("d:/roseempire/run_ai_fleet.bat").write_text(bat, encoding="ascii")
print("run_ai_fleet.bat updated")

# OPEN_BOTS.bat - one click
open_bots = r'''@echo off
title Rose Empire - Open All Bots
cd /d "%~dp0"
echo Opening AI Fleet bots (Sarah / James / Alex)...
call "%~dp0run_ai_fleet.bat"
'''
Path("d:/roseempire/OPEN_BOTS.bat").write_text(open_bots, encoding="ascii")

# launch_website_with_chat.bat - wait for server
lw = r'''@echo off
title Rose Empire - Website + Chat Bots
cd /d "%~dp0"
if not exist ".env" (
    echo ERROR: .env missing in %~dp0
    pause
    exit /b 1
)
echo Starting website + Sarah/Alex chat on http://127.0.0.1:5000
echo KEEP THIS WINDOW OPEN.
start "Rose Empire Chat" /MIN cmd /c "cd /d %~dp0 && py -3 server.py"
powershell -NoProfile -Command "$ok=$false; for($i=0;$i -lt 45;$i++){ try { $r=Invoke-WebRequest -Uri 'http://127.0.0.1:5000/health' -UseBasicParsing -TimeoutSec 2; if($r.StatusCode -eq 200){$ok=$true; break} } catch {} Start-Sleep 2 }; if($ok){ Start-Process 'http://127.0.0.1:5000' } else { Write-Host 'Chat server did not start.' }"
pause
'''
Path("d:/roseempire/launch_website_with_chat.bat").write_text(lw, encoding="ascii")
print("launch_website_with_chat.bat updated")
