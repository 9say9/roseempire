@echo off

title Rose Empire - Deploy site to GitHub Pages

cd /d "%~dp0"



echo.

echo  Rose Empire - GitHub Pages deploy

echo  ---------------------------------

echo  Push to main branch - GitHub builds automatically.

echo  Live: https://www.roseempire.co.uk (after GoDaddy DNS points to GitHub)

echo  Preview: https://9say9.github.io/roseempire/

echo.



git status

echo.

set /p MSG="Commit message (or press Enter for default): "

if "%MSG%"=="" set MSG=Update Rose Empire site on GitHub Pages



git add -A

git commit -m "%MSG%"

if errorlevel 1 (

    echo Nothing new to commit, or commit failed.

    git push origin main

    goto done

)



git push origin main

if errorlevel 1 (

    echo Push failed.

    pause

    exit /b 1

)



echo.

echo  Pushed. GitHub Pages will update in 1-2 minutes.

:done

pause

