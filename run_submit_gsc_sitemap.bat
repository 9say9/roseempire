@echo off
title Rose Empire - Google Search Console verify + sitemap
cd /d "%~dp0"
py -3.12 submit_gsc_sitemap.py
pause
