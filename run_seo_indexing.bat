@echo off
title Rose Empire - SEO indexing (no Netlify deploy)
cd /d "%~dp0"
py -3.12 seo_indexing.py
pause
