"""Fetch synopses from Google Books API for all books."""
import json
import urllib.request
import urllib.parse
import time
import sys
import os
import html
import re

# Map Dutch titles to better search queries (original titles work better)
SEARCH_OVERRIDES = {
    "De heksen": "The Witches Roald Dahl",
    "Percy Jackson en de Olympiërs: De bliksemschicht dief": "Percy Jackson Lightning Thief Rick Riordan",
    "De trein van vier over twaalf": "Quatre soeurs Malika Ferdjoukh",
    "Echo uit de diepte": "Echo Pam Munoz Ryan",
    "De Grijze Jager: De ruïnes van Doorn": "Ranger's Apprentice Ruins of Gorlan John Flanagan",
    "Geen beste dag voor voodoo": "A Bad Day for Voodoo Jeff Strand",
    "De Hongerspelen": "The Hunger Games Suzanne Collins",
    "Shatter Me (Alizeh serie)": "Shatter Me Tahereh Mafi",
    "Schaduw van de Vos": "Shadow of the Fox Julie Kagawa",
    "Zeis": "Scythe Neal Shusterman",
    "Doodleuk": "A Good Girl's Guide to Murder Holly Jackson",
    "Een vloek zo eenzaam": "A Curse So Dark and Lonely Brigid Kemmerer",
    "De duistere profetie": "Unravel Me Tahereh Mafi",
    "Schaduwliefde": "Salt to the Sea Ruta Sepetys",
    "Lang leve Jane": "My Lady Jane Cynthia Hand",
    "De roep van het hart": "The Selection Kiera Cass",
    "Moordgids voor lieve meisjes": "A Good Girl's Guide to Murder Holly Jackson",
    "De kleuren van magie": "A Darker Shade of Magic V.E. Schwab",
    "List & Leugens": "Six of Crows Leigh Bardugo",
    "Het grote misschien": "Looking for Alaska John Green",
    "Aristoteles & Dante ontdekken de geheimen van het universum": "Aristotle and Dante Discover the Secrets of the Universe",
    "Op het einde gaan ze allebei dood": "They Both Die at the End Adam Silvera",
    "5 stappen van jou": "Five Feet Apart Rachael Lippincott",
    "Het parfum": "Das Parfum Patrick Suskind",
    "Een lied voor Achilles": "The Song of Achilles Madeline Miller",
    "Obsidian (Lux serie)": "Obsidian Jennifer Armentrout Lux",
    "FunJungle: Gekidnapt!": "Poached Stuart Gibbs FunJungle",
    "Warrior Cats: De wildernis in": "Warriors Into the Wild Erin Hunter",
    "De magische apotheek": "Die Duftapotheke Anna Ruhe",
    "Iene miene mutte": "Eeny Meeny M.J. Arlidge",
    "Sunrise on the Reaping": "Sunrise on the Reaping Suzanne Collins",
    "Percy Jackson en de Olympiërs": "Percy Jackson Lightning Thief Rick Riordan",
    "Gebroken": "Gebroken Mel Wallis de Vries",
    "Maxton Hall College": "Save Me Maxton Hall Mona Kasten",
    "Heartstopper Volume 1": "Heartstopper Volume 1 Alice Oseman",
    "De Zeven Zussen": "Seven Sisters Lucinda Riley",
    "Talon": "Talon Julie Kagawa dragon",
    "Girl in Pieces": "Girl in Pieces Kathleen Glasgow",
}


def clean_html(text):
    """Remove HTML tags and decode entities."""
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def search_google_books(query):
    """Search Google Books API and return description."""
    params = urllib.parse.urlencode({"q": query, "maxResults": 3, "langRestrict": ""})
    url = f"https://www.googleapis.com/books/v1/volumes?{params}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BookshelfProject/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if data.get("items"):
            for item in data["items"]:
                vol = item.get("volumeInfo", {})
                desc = vol.get("description", "")
                if desc and len(desc) > 50:
                    return clean_html(desc)
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)

    return None


def search_open_library(query):
    """Fallback: search Open Library for description."""
    # First search for the work key
    params = urllib.parse.urlencode({"q": query, "limit": 1, "fields": "key"})
    url = f"https://openlibrary.org/search.json?{params}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BookshelfProject/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if data.get("docs"):
            work_key = data["docs"][0]["key"]
            # Fetch work details for description
            work_url = f"https://openlibrary.org{work_key}.json"
            req2 = urllib.request.Request(work_url, headers={"User-Agent": "BookshelfProject/1.0"})
            with urllib.request.urlopen(req2, timeout=15) as resp2:
                work = json.loads(resp2.read().decode("utf-8"))

            desc = work.get("description", "")
            if isinstance(desc, dict):
                desc = desc.get("value", "")
            if desc and len(desc) > 50:
                return clean_html(desc)
    except Exception as e:
        print(f"  OL ERROR: {e}", file=sys.stderr)

    return None


def main():
    data_dir = os.path.dirname(os.path.abspath(__file__))
    synopses = {}

    # Load existing synopses if any
    synopses_file = os.path.join(data_dir, "synopses.json")
    if os.path.exists(synopses_file):
        with open(synopses_file, "r", encoding="utf-8") as f:
            synopses = json.load(f)

    # Collect all books from JS files
    all_books = []
    for grade in ["graad_1", "graad_2", "graad_3"]:
        js_file = os.path.join(data_dir, f"{grade}.js")
        with open(js_file, "r", encoding="utf-8") as f:
            content = f.read()
            books = json.loads(content[content.index('['):content.rindex(']') + 1])
        for b in books:
            if b["title"] not in [x["title"] for x in all_books]:
                all_books.append(b)

    total = len(all_books)
    found = 0
    skipped = 0

    for i, book in enumerate(all_books):
        title = book["title"]

        # Skip if we already have a long synopsis
        if title in synopses and len(synopses[title]) > 150:
            skipped += 1
            continue

        query = SEARCH_OVERRIDES.get(title, f"{title} {book['author']}")
        print(f"[{i+1}/{total}] {title}")

        # Try Google Books first
        desc = search_google_books(query)
        time.sleep(0.3)

        # Fallback to Open Library
        if not desc:
            desc = search_open_library(query)
            time.sleep(0.3)

        # Try Dutch search if original didn't work
        if not desc and title != query:
            desc = search_google_books(f"{title} {book['author']}")
            time.sleep(0.3)

        if desc:
            synopses[title] = desc
            found += 1
            print(f"  -> {len(desc)} chars")
        else:
            print(f"  -> NOT FOUND")

    # Save
    with open(synopses_file, "w", encoding="utf-8") as f:
        json.dump(synopses, f, ensure_ascii=False, indent=2)

    print(f"\nDone! Found: {found}, Skipped (already had): {skipped}, Total in file: {len(synopses)}")


if __name__ == "__main__":
    main()
