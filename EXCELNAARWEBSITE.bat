@echo off
echo === EXCEL NAAR WEBSITE ===
echo De boekendata uit het Excel-bestand wordt teruggezet naar de website.
echo.
uv run --with openpyxl python sync.py import
pause
