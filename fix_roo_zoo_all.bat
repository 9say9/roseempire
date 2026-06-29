@echo off
title Rose Empire - Fix Roo + Zoo (webview + Ollama)
cd /d "%~dp0"
set "CURSOR_DATA=%APPDATA%\Cursor"
set "OLLAMA=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"

echo.
echo  ============================================================
echo   FULL FIX: Roo Code + Zoo Code not opening / API stuck
echo  ============================================================
echo.
echo  Fixes:
echo    - Broken auto-import paths (old LM Studio / OpenRouter)
echo    - Cursor webview service worker cache
echo    - Ollama profile: qwen2.5-coder:1.5b
echo.
echo  SAVE WORK. Cursor will close in 5 seconds...
timeout /t 5 /nobreak >nul

echo.
echo  [1/5] Closing Cursor...
taskkill /IM Cursor.exe /F >nul 2>&1
timeout /t 4 /nobreak >nul

echo  [2/5] Clearing webview caches...
for %%D in (
    "Service Worker"
    "Cache"
    "Code Cache"
    "GPUCache"
    "CachedData"
    "WebStorage"
    "blob_storage"
    "DawnGraphiteCache"
    "DawnWebGPUCache"
) do (
    if exist "%CURSOR_DATA%\%%~D" (
        rmdir /s /q "%CURSOR_DATA%\%%~D" 2>nul
        echo   cleared %%~D
    )
)
if exist "%LOCALAPPDATA%\Cursor\Service Worker" rmdir /s /q "%LOCALAPPDATA%\Cursor\Service Worker" 2>nul

echo  [3/5] Clearing Roo/Zoo extension caches...
if exist "%CURSOR_DATA%\User\globalStorage\rooveterinaryinc.roo-cline\cache" (
    rmdir /s /q "%CURSOR_DATA%\User\globalStorage\rooveterinaryinc.roo-cline\cache"
)
if exist "%CURSOR_DATA%\User\globalStorage\zoocodeorganization.zoo-code\cache" (
    rmdir /s /q "%CURSOR_DATA%\User\globalStorage\zoocodeorganization.zoo-code\cache"
)

echo  [4/5] Patching Roo + Zoo Ollama settings...
py -3 "%~dp0_fix_roo_zoo_config.py"
if errorlevel 1 echo   WARN: config patch had issues

echo  [5/5] Starting Ollama...
if exist "%OLLAMA%" (
    start "" "%LOCALAPPDATA%\Programs\Ollama\Ollama.exe"
    timeout /t 3 /nobreak >nul
    "%OLLAMA%" run qwen2.5-coder:1.5b "OK" >nul 2>&1
)

echo.
echo  DONE. Reopen Cursor and:
echo    1. Settings ^> General ^> Default Layout = EDITOR
echo    2. Open Roo/Zoo from LEFT side bar (not bottom panel)
echo    3. Ctrl+Shift+P ^> Developer: Reload Window
echo    4. Model should be: qwen2.5-coder:1.5b via Ollama
echo.
pause
