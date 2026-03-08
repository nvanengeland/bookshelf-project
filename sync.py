"""
Synchronisatie-script: Website data <-> Excel

WEBSITE NAAR EXCEL (export):
  Leest de JS-databestanden die de website aandrijven (data/graad_1.js, etc.)
  en schrijft alle boekdata naar een bewerkbare Excel-file (boekentips_data.xlsx).
  Elk tabblad = een graad. Je kan dan in Excel titels, auteurs, synopses, genres,
  uitgevers, etc. aanpassen.

EXCEL NAAR WEBSITE (import):
  Leest de bewerkte Excel-file (boekentips_data.xlsx) terug in en overschrijft
  de JS-databestanden. Na import kan je de site herladen om de wijzigingen te zien.

Gebruik:
  uv run --with openpyxl python sync.py export   -> WEBSITE NAAR EXCEL
  uv run --with openpyxl python sync.py import    -> EXCEL NAAR WEBSITE
"""
import json
import sys
import os

import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
EXCEL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "boekentips_data.xlsx")

GRADES = [
    ("graad_1", "GRAAD_1_DATA", "1ste Graad"),
    ("graad_2", "GRAAD_2_DATA", "2de Graad"),
    ("graad_3", "GRAAD_3_DATA", "3de Graad"),
]

# Column order and headers (Dutch labels for the Excel)
COLUMNS = [
    ("title", "Titel"),
    ("author", "Auteur"),
    ("isbn", "ISBN"),
    ("pages", "Pagina's"),
    ("publication_date", "Publicatiejaar"),
    ("original_language", "Oorspronkelijke taal"),
    ("genre", "Genre"),
    ("publisher", "Uitgever"),
    ("synopsis", "Synopsis"),
    ("cover_front", "Cover URL (voorkant)"),
    ("cover_back", "Cover URL (achterkant)"),
    ("age_category", "Leeftijdscategorie"),
    ("publisher_url", "Uitgever URL"),
]


def load_js_data(grade_key, var_name):
    """Load book data from a JS file."""
    js_file = os.path.join(DATA_DIR, f"{grade_key}.js")
    with open(js_file, "r", encoding="utf-8") as f:
        content = f.read()
    json_str = content[content.index("["):content.rindex("]") + 1]
    return json.loads(json_str)


def save_js_data(grade_key, var_name, books):
    """Save book data to a JS file."""
    js_file = os.path.join(DATA_DIR, f"{grade_key}.js")
    with open(js_file, "w", encoding="utf-8") as f:
        f.write(f"const {var_name} = ")
        json.dump(books, f, ensure_ascii=False, indent=2)
        f.write(";\n")


# ── EXPORT: JS -> Excel ─────────────────────────────────────────────

def export_to_excel():
    """Export all JS data to an Excel workbook with one sheet per grade."""
    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # remove default sheet

    # Styles
    header_font = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="8B5E3C", end_color="8B5E3C", fill_type="solid")
    header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell_align = Alignment(vertical="top", wrap_text=True)
    thin_border = Border(
        left=Side(style="thin", color="CCCCCC"),
        right=Side(style="thin", color="CCCCCC"),
        top=Side(style="thin", color="CCCCCC"),
        bottom=Side(style="thin", color="CCCCCC"),
    )

    for grade_key, var_name, sheet_name in GRADES:
        books = load_js_data(grade_key, var_name)
        ws = wb.create_sheet(title=sheet_name)

        # Headers
        for col_idx, (field, label) in enumerate(COLUMNS, 1):
            cell = ws.cell(row=1, column=col_idx, value=label)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_align
            cell.border = thin_border

        # Data rows
        for row_idx, book in enumerate(books, 2):
            for col_idx, (field, _) in enumerate(COLUMNS, 1):
                value = book.get(field)
                # Convert None to empty string for display
                if value is None:
                    value = ""
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.alignment = cell_align
                cell.border = thin_border

        # Column widths
        col_widths = {
            "title": 30,
            "author": 22,
            "isbn": 16,
            "pages": 10,
            "publication_date": 14,
            "original_language": 18,
            "genre": 28,
            "publisher": 22,
            "synopsis": 60,
            "cover_front": 35,
            "cover_back": 35,
            "age_category": 16,
            "publisher_url": 45,
        }
        for col_idx, (field, _) in enumerate(COLUMNS, 1):
            ws.column_dimensions[get_column_letter(col_idx)].width = col_widths.get(field, 15)

        # Freeze header row
        ws.freeze_panes = "A2"

        # Auto-filter
        ws.auto_filter.ref = f"A1:{get_column_letter(len(COLUMNS))}{len(books) + 1}"

        print(f"  {sheet_name}: {len(books)} boeken")

    wb.save(EXCEL_FILE)
    print(f"\nExcel opgeslagen: {EXCEL_FILE}")


# ── IMPORT: Excel -> JS ─────────────────────────────────────────────

def import_from_excel():
    """Import data from Excel back into JS files."""
    if not os.path.exists(EXCEL_FILE):
        print(f"FOUT: Excel bestand niet gevonden: {EXCEL_FILE}")
        sys.exit(1)

    wb = openpyxl.load_workbook(EXCEL_FILE)

    for grade_key, var_name, sheet_name in GRADES:
        if sheet_name not in wb.sheetnames:
            print(f"  WAARSCHUWING: Sheet '{sheet_name}' niet gevonden, overgeslagen")
            continue

        ws = wb[sheet_name]
        books = []

        # Read header row to map columns
        headers = {}
        for col_idx in range(1, ws.max_column + 1):
            header_val = ws.cell(row=1, column=col_idx).value
            if header_val:
                # Find matching field by label
                for field, label in COLUMNS:
                    if label == header_val.strip():
                        headers[col_idx] = field
                        break

        if not headers:
            print(f"  WAARSCHUWING: Geen geldige headers in '{sheet_name}', overgeslagen")
            continue

        # Read data rows
        for row_idx in range(2, ws.max_row + 1):
            book = {}
            has_data = False

            for col_idx, field in headers.items():
                value = ws.cell(row=row_idx, column=col_idx).value

                # Type conversions
                if field in ("pages", "publication_date"):
                    if value is not None and value != "":
                        try:
                            value = int(float(str(value)))
                        except (ValueError, TypeError):
                            value = None
                    else:
                        value = None
                elif field in ("cover_front", "cover_back", "publisher_url"):
                    # Keep None for empty cover URLs (matches JSON null)
                    if not value or str(value).strip() == "":
                        value = None
                    else:
                        value = str(value).strip()
                else:
                    # Convert to string, empty string for None
                    if value is None:
                        value = ""
                    else:
                        value = str(value).strip()

                book[field] = value
                if value:
                    has_data = True

            # Skip completely empty rows
            if has_data and book.get("title"):
                books.append(book)

        save_js_data(grade_key, var_name, books)
        print(f"  {sheet_name}: {len(books)} boeken geimporteerd")

    print(f"\nJS bestanden bijgewerkt in {DATA_DIR}/")


# ── MAIN ─────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "export":
        print("Exporteren: JS -> Excel...")
        export_to_excel()
    elif command == "import":
        print("Importeren: Excel -> JS...")
        import_from_excel()
    else:
        print(f"Onbekend commando: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
