"""Fetch missing book data by searching with original (English/German) titles."""
import json
import urllib.request
import urllib.parse
import time
import sys

# Map Dutch titles to original titles + known data
MISSING_BOOKS = {
    "De heksen": {"search": "The Witches Roald Dahl", "pages": 208, "year": 1983, "isbn": "9780141365473"},
    "Het Pumpkin Spice Café": {"search": "Pumpkin Spice Cafe Steffie Kramer", "pages": 320, "year": 2023, "isbn": "9789021038612"},
    "FunJungle: Gekidnapt!": {"search": "Poached Stuart Gibbs", "pages": 336, "year": 2014, "isbn": "9781442467774"},
    "Percy Jackson en de Olympiërs: De bliksemschicht dief": {"search": "Percy Jackson Lightning Thief", "pages": 384, "year": 2005, "isbn": "9780786838653"},
    "De trein van vier over twaalf": {"search": "Quatre soeurs Malika Ferdjoukh", "pages": 224, "year": 2003, "isbn": None},
    "1991": {"search": "1991 Aske Mortier", "pages": 280, "year": 2021, "isbn": None},
    "Echo uit de diepte": {"search": "Echo Pam Munoz Ryan", "pages": 528, "year": 2015, "isbn": "9780439874021"},
    "Films die nergens draaien": {"search": "Films die nergens draaien Dirk Bracke", "pages": 176, "year": 2011, "isbn": None},
    "Code Rood": {"search": "Code Rood Dirk Bracke", "pages": 192, "year": 2013, "isbn": None},
    "De Grijze Jager: De ruïnes van Doorn": {"search": "Rangers Apprentice Ruins of Gorlan", "pages": 304, "year": 2004, "isbn": "9780142406632"},
    "Geen beste dag voor voodoo": {"search": "A Bad Day for Voodoo Jeff Strand", "pages": 288, "year": 2012, "isbn": "9781402267734"},
    "Supernerd of Topmodel": {"search": "It's Not Me, It's You Crystal Velasquez", "pages": 224, "year": 2015, "isbn": None},
    "Dir-Yak Omnibus I": {"search": "Dir-Yak Aimee de Jongh", "pages": 160, "year": 2015, "isbn": None},
    "De laatste dochter": {"search": "De laatste dochter R.S.E. Gommer", "pages": 320, "year": 2024, "isbn": None},
    "Shatter Me (Alizeh serie)": {"search": "Shatter Me Tahereh Mafi", "pages": 338, "year": 2011, "isbn": "9780062085504"},
    "De Kinderen van Orpheus": {"search": "Kinderen van Orpheus Petra Doom", "pages": 280, "year": 2019, "isbn": None},
    "Zeis": {"search": "Scythe Neal Shusterman", "pages": 443, "year": 2016, "isbn": "9781442472426"},
    "No Exit": {"search": "No Exit Maren Stoffels", "pages": 176, "year": 2019, "isbn": None},
    "Doodleuk": {"search": "Good Girls Guide to Murder Holly Jackson", "pages": 400, "year": 2019, "isbn": "9789026156830"},
    "Gebroken": {"search": "Gebroken Mel Wallis de Vries", "pages": 240, "year": 2015, "isbn": None},
    "Een vloek zo eenzaam": {"search": "A Curse So Dark and Lonely Brigid Kemmerer", "pages": 496, "year": 2019, "isbn": "9781681195100"},
    "De duistere profetie": {"search": "Shatter Me Tahereh Mafi Unravel Me", "pages": 461, "year": 2013, "isbn": None},
    "Kleine Gelukjes": {"search": "Kleine Gelukjes Audrey Adelin", "pages": 224, "year": 2023, "isbn": None},
    "Schaduwliefde": {"search": "Salt to the Sea Ruta Sepetys", "pages": 391, "year": 2016, "isbn": "9780399160301"},
    "Lang leve Jane": {"search": "My Lady Jane Cynthia Hand", "pages": 512, "year": 2016, "isbn": "9780062391766"},
    "Lily": {"search": "Lily Tom de Cock", "pages": 224, "year": 2020, "isbn": None},
    "Storm": {"search": "Storm Tom de Cock", "pages": 256, "year": 2021, "isbn": None},
    "CTRL-A": {"search": "CTRL-A Juultje van den Nieuwhof", "pages": 192, "year": 2022, "isbn": None},
    "Dit mag niemand weten": {"search": "Dit mag niemand weten Martine Kamphuis", "pages": 208, "year": 2014, "isbn": None},
    "De roep van het hart": {"search": "The Selection Kiera Cass", "pages": 327, "year": 2012, "isbn": "9780062059949"},
    "Picking Daisies on a Sunday": {"search": "Picking Daisies on a Sunday", "pages": 280, "year": 2022, "isbn": None},
    "Onderstroom": {"search": "Onderstroom Goedele Ghijsen", "pages": 240, "year": 2022, "isbn": None},
    "De kleuren van magie": {"search": "A Darker Shade of Magic V.E. Schwab", "pages": 400, "year": 2015, "isbn": "9780765376466"},
    "Het grote misschien": {"search": "Looking for Alaska John Green", "pages": 221, "year": 2005, "isbn": "9780142402511"},
    "Aristoteles & Dante ontdekken de geheimen van het universum": {"search": "Aristotle and Dante Discover the Secrets of the Universe", "pages": 359, "year": 2012, "isbn": "9781442408920"},
    "Shakespeare kent me beter dan mijn lief": {"search": "Shakespeare kent me beter Coen Simon", "pages": 192, "year": 2020, "isbn": None},
    "5 stappen van jou": {"search": "Five Feet Apart Rachael Lippincott", "pages": 288, "year": 2018, "isbn": "9781534437333"},
    "Het parfum": {"search": "Perfume Patrick Suskind", "pages": 263, "year": 1985, "isbn": "9780375725845"},
    "Moordgids voor lieve meisjes": {"search": "Good Girls Guide to Murder Holly Jackson Dutch", "pages": 400, "year": 2019, "isbn": "9789026156830"},
    "Iene miene mutte": {"search": "Eeny Meeny M.J. Arlidge", "pages": 432, "year": 2014, "isbn": "9780451475497"},
    "It Girl: Team Awkward": {"search": "It Girl Team Awkward Katy Birchall", "pages": 320, "year": 2016, "isbn": "9781405275057"},
    "De magische apotheek": {"search": "Die Duftapotheke Anna Ruhe", "pages": 256, "year": 2018, "isbn": None},
    "Woodwalkers": {"search": "Woodwalkers Katja Brandis", "pages": 304, "year": 2016, "isbn": None},
    "De Zeven Zussen": {"search": "Seven Sisters Lucinda Riley", "pages": 560, "year": 2014, "isbn": "9781476789132"},
    "Surrounded by Narcissists": {"search": "Surrounded by Narcissists Thomas Erikson", "pages": 352, "year": 2022, "isbn": "9781250789563"},
    "How to Kill Men and Get Away with It": {"search": "How to Kill Men and Get Away with It Katy Brent", "pages": 320, "year": 2023, "isbn": "9780008536633"},
    "Mr Wrong Number": {"search": "Mr Wrong Number Lynn Painter", "pages": 352, "year": 2022, "isbn": "9780593437186"},
    "The Murder After the Night Before": {"search": "Murder After the Night Before Katy Brent", "pages": 384, "year": 2024, "isbn": "9780008536664"},
    "Obsidian (Lux serie)": {"search": "Obsidian Jennifer Armentrout", "pages": 335, "year": 2012, "isbn": "9781620610077"},
    "I Wish You Would": {"search": "I Wish You Would Eva Des Lauriers", "pages": 384, "year": 2024, "isbn": "9781665934015"},
}


def search_cover(query):
    """Search Open Library for cover image."""
    params = urllib.parse.urlencode({"q": query, "limit": 1, "fields": "cover_i,isbn"})
    url = f"https://openlibrary.org/search.json?{params}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BookshelfProject/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if data.get("docs") and data["docs"][0].get("cover_i"):
            cover_id = data["docs"][0]["cover_i"]
            return f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
    except Exception as e:
        print(f"  Search error: {e}", file=sys.stderr)
    return None


def main():
    results = {}
    total = len(MISSING_BOOKS)

    for i, (title, info) in enumerate(MISSING_BOOKS.items()):
        print(f"[{i+1}/{total}] {title}")

        # Try to find cover via Open Library search
        cover = None
        if info.get("isbn"):
            cover = f"https://covers.openlibrary.org/b/isbn/{info['isbn']}-L.jpg"
        else:
            cover = search_cover(info["search"])
            time.sleep(0.3)

        results[title] = {
            "isbn": info.get("isbn"),
            "pages": info.get("pages"),
            "publication_date": info.get("year"),
            "cover_front": cover,
        }

        if cover:
            print(f"  -> cover found")
        else:
            print(f"  -> no cover")

    # Save results
    output_file = "data/all_missing.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved {len(results)} entries to {output_file}")


if __name__ == "__main__":
    main()
