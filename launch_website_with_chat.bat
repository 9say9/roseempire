@echo off
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
