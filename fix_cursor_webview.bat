@echo off
title Fix Cursor Webview - Roo / Zoo Service Worker Error
cd /d "%~dp0"

set "CURSOR_DATA=%APPDATA%\Cursor"

echo.
echo  ============================================================
echo   FIX: "Could not register service worker" (Roo / Zoo blank)
echo  ============================================================
echo.
echo  This is a Cursor webview bug — NOT an Ollama problem.
echo  Save your work. Cursor will be closed to clear bad cache.
echo.
pause

echo.
echo  [1/3] Closing Cursor...
taskkill /IM Cursor.exe /F >nul 2>&1
timeout /t 3 /nobreak >nul

echo  [2/3] Clearing webview / service worker cache...
if exist "%CURSOR_DATA%\Service Worker" (
    rmdir /s /q "%CURSOR_DATA%\Service Worker"
    echo   Deleted: Service Worker
)
if exist "%CURSOR_DATA%\Cache" (
    rmdir /s /q "%CURSOR_DATA%\Cache"
    echo   Deleted: Cache
)
if exist "%CURSOR_DATA%\Code Cache" (
    rmdir /s /q "%CURSOR_DATA%\Code Cache"
    echo   Deleted: Code Cache
)
if exist "%CURSOR_DATA%\GPUCache" (
    rmdir /s /q "%CURSOR_DATA%\GPUCache"
    echo   Deleted: GPUCache
)
if exist "%LOCALAPPDATA%\Cursor\Service Worker" (
    rmdir /s /q "%LOCALAPPDATA%\Cursor\Service Worker"
    echo   Deleted: Local Service Worker
)

echo  [3/3] Done.
echo.
echo  NOW reopen Cursor and do ALL of these:
echo.
echo   1. Cursor Settings ^> General ^> Default Layout = EDITOR
echo      (Agent layout breaks webview panels — known Cursor bug)
echo.
echo   2. Open Roo Code from the PRIMARY side bar (left), not bottom panel
echo      Right-click Roo tab ^> Move View ^> Primary Side Bar
echo.
echo   3. Ctrl+Shift+P ^> "Developer: Reload Window"
echo.
echo   4. If still broken: Help ^> Check for Updates (need Cursor 2.3+)
echo.
echo  Ollama model is still: qwen2.5-coder:1.5b on http://127.0.0.1:11434
echo  Run fix_roo_ollama.bat after this if Roo still won't connect to AI.
echo.
pause
