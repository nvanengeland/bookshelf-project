@echo off
echo === WEBSITE NAAR EXCEL ===
echo De boekendata van de website wordt opgeslagen in een Excel-bestand.
echo.
uv run --with openpyxl python sync.py export
pause
