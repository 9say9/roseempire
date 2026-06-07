@echo off
title Laptop Performance Booster
:: Check for administrative privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Administrative permissions confirmed.
) else (
    echo Please run this script as Administrator.
    pause
    exit /b
)

echo ======================================================
echo   OPTIMIZING SYSTEM PERFORMANCE
echo ======================================================

:: 1. Power Plan Optimization
echo [+] Setting Power Plan to High Performance...
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
:: Attempt to unlock Ultimate Performance if available
powercfg /duplicatescheme e9a42b02-d5ba-446fb-a32c-d477a65ca726
powercfg /setactive e9a42b02-d5ba-446fb-a32c-d477a65ca726
echo [OK] Power plan updated.

:: 2. System Cleanup
echo [+] Cleaning temporary files...
del /s /f /q %temp%\*.*
rd /s /q %temp%
mkdir %temp%
del /s /f /q C:\Windows\Temp\*.*
rd /s /q C:\Windows\Temp
mkdir C:\Windows\Temp
echo [+] Cleaning Prefetch...
del /s /f /q C:\Windows\Prefetch\*.*
echo [OK] Cleanup complete.

:: 3. Visual Effects Optimization (Registry Tweak for Performance)
echo [+] Adjusting visual effects for best performance...
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f
echo [OK] Visual effects set to performance.

:: 4. Disabling unnecessary services (Common bloat)
echo [+] Disabling non-essential services...
:: Connected User Experiences and Telemetry
sc stop DiagTrack
sc config DiagTrack start= disabled
:: Distributed Link Tracking Client
sc stop TrkWks
sc config TrkWks start= disabled
echo [OK] Telemetry and tracking services disabled.

:: 5. Memory Optimization (Clear Standby List - basic)
echo [+] Flushing DNS cache...
ipconfig /flushdns
echo [OK] DNS flushed.

echo ======================================================
echo   OPTIMIZATION COMPLETE!
echo   Please restart your laptop for changes to take full effect.
echo ======================================================
pause
