"""Fetch publisher data from Open Library API and Google Books API for all books."""
import json
import urllib.request
import urllib.parse
import time
import sys
import os

# Known publishers for books where API may not find them
KNOWN_PUBLISHERS = {
    "Binding 13": "Piatkus",
    "Little Women": "Roberts Brothers",
    "The Perks of Being a Wallflower": "Gallery Books",
    "Iene miene mutte": "A.W. Bruna",
    "Girl in Pieces": "Delacorte Press",
    "Juniper": "Random House",
    "De heksen": "De Fontein",
    "Het Pumpkin Spice Café": "Boekerij",
    "It Girl: Team Awkward": "Egmont",
    "FunJungle: Gekidnapt!": "Simon & Schuster",
    "Percy Jackson en de Olympiërs: De bliksemschicht dief": "Uitgeverij Kluitman",
    "De magische apotheek": "Arena Verlag",
    "De trein van vier over twaalf": "L'école des loisirs",
    "Warrior Cats: De wildernis in": "Baeckens Books",
    "1991": "Uitgeverij Vrijdag",
    "Echo uit de diepte": "Scholastic",
    "Films die nergens draaien": "Clavis",
    "Code Rood": "Clavis",
    "De Grijze Jager: De ruïnes van Doorn": "Gottmer",
    "Woodwalkers": "Arena Verlag",
    "Harry Potter en de Steen der Wijzen": "De Harmonie",
    "Geen beste dag voor voodoo": "Sourcebooks",
    "Dumplin'": "Balzer + Bray",
    "Supernerd of Topmodel": "Scholastic",
    "X-Scape": "Uitgeverij Manteau",
    "Sunrise on the Reaping": "Scholastic",
    "De Zeven Zussen": "Xander Uitgevers",
    "Mythos": "Penguin Books",
    "Helden": "Penguin Books",
    "Surrounded by Narcissists": "St. Martin's Press",
    "Dir-Yak Omnibus I": "Oog & Blik",
    "The Hunger Games": "Scholastic",
    "De laatste dochter": "Zomer & Keuning",
    "Five Survive": "Electric Monkey",
    "Percy Jackson en de Olympiërs": "Uitgeverij Kluitman",
    "The Cruel Prince": "Little, Brown",
    "Once Upon a Broken Heart": "Flatiron Books",
    "Obsidian (Lux serie)": "Entangled Teen",
    "Talon": "HarperCollins",
    "From Blood and Ash": "Blue Box Press",
    "Shatter Me (Alizeh serie)": "HarperCollins",
    "When It's Real": "HQN Books",
    "De Hongerspelen": "Van Goor",
    "Schaduw van de Vos": "HarperCollins",
    "De Kinderen van Orpheus": "Uitgeverij Prometheus",
    "Zeis": "Simon & Schuster",
    "You'd Be Home Now": "Delacorte Press",
    "Royals": "HQN Books",
    "No Exit": "Leopold",
    "Doodleuk": "Uitgeverij Moon",
    "The Maze Runner": "Delacorte Press",
    "If He Had Been with Me": "Sourcebooks Fire",
    "Gebroken": "Uitgeverij Unieboek | Het Spectrum",
    "I Wish You Would": "Simon & Schuster",
    "Een vloek zo eenzaam": "Blossom Books",
    "Powerless": "Simon & Schuster",
    "Thieves' Gambit": "Simon & Schuster",
    "De duistere profetie": "HarperCollins",
    "Check & Mate": "Berkley",
    "The Fault in Our Stars": "Dutton Books",
    "Kleine Gelukjes": "Xander Uitgevers",
    "Schaduwliefde": "Philomel Books",
    "IJzerkop": "Querido",
    "One Golden Summer": "Viking",
    "The Maidens": "Celadon Books",
    "Say You'll Remember Me": "Berkley",
    "Heart Bones": "Atria Books",
    "How to Kill Men and Get Away with It": "HarperCollins",
    "Better Than the Movies": "Simon & Schuster",
    "Mr Wrong Number": "Berkley",
    "The Housemaid": "Bookouture",
    "The Seven Husbands of Evelyn Hugo": "Atria Books",
    "The Perfect Marriage": "Grand Central Publishing",
    "A Thousand Boy Kisses": "self-published",
    "The Murder After the Night Before": "HarperCollins",
    "When in Rome": "Dell",
    "Malibu Rising": "Ballantine Books",
    "The Reappearance of Rachel Price": "Electric Monkey",
    "A Good Girl's Guide to Murder": "Electric Monkey",
    "Five Survive": "Electric Monkey",
    "Letters to the Lost": "Bloomsbury YA",
    "Before We Were Strangers": "Atria Books",
    "If He Had Been with Me": "Sourcebooks Fire",
    "Anna and the French Kiss": "Dutton Books",
    "The Girl on the Train": "Riverhead Books",
    "Until Friday Night": "Simon Pulse",
    "The Way I Used to Be": "Margaret K. McElderry Books",
    "Throttled": "Bloom Books",
    "Regretting You": "Atria Books",
    "November 9": "Atria Books",
    "Every Last Word": "Hyperion",
    "Heartstopper Volume 1": "Hodder Children's Books",
    "Solitaire": "HarperCollins",
    "Radio Silence": "HarperCollins",
    "I Was Born for This": "HarperCollins",
    "Loveless": "HarperCollins",
    "Red, White & Royal Blue": "St. Martin's Griffin",
    "Lang leve Jane": "HarperTeen",
    "Lily": "Uitgeverij Vrijdag",
    "Storm": "Uitgeverij Vrijdag",
    "Maxton Hall College": "LYX Verlag",
    "CTRL-A": "Lannoo",
    "Dit mag niemand weten": "Kluitman",
    "De roep van het hart": "HarperCollins",
    "People We Meet on Vacation": "Berkley",
    "The Bodyguard": "St. Martin's Griffin",
    "A Thousand Broken Pieces": "self-published",
    "Picking Daisies on a Sunday": "self-published",
    "Moordgids voor lieve meisjes": "Uitgeverij Moon",
    "Onderstroom": "Manteau",
    "Een lied voor Achilles": "Bloomsbury",
    "De kleuren van magie": "Tor Books",
    "List & Leugens": "Blossom Books",
    "Zeis": "Simon & Schuster",
    "Het grote misschien": "Lemniscaat",
    "Aristoteles & Dante ontdekken de geheimen van het universum": "Simon & Schuster",
    "Op het einde gaan ze allebei dood": "Clavis",
    "Shakespeare kent me beter dan mijn lief": "De Bezige Bij",
    "5 stappen van jou": "Simon & Schuster",
    "Het parfum": "Diogenes Verlag",
}


def search_google_books_publisher(title, author):
    """Search Google Books API for publisher."""
    query = f"{title} {author}"
    params = urllib.parse.urlencode({"q": query, "maxResults": 3})
    url = f"https://www.googleapis.com/books/v1/volumes?{params}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BookshelfProject/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if data.get("items"):
            for item in data["items"]:
                vol = item.get("volumeInfo", {})
                publisher = vol.get("publisher", "")
                if publisher:
                    return publisher
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)

    return None


def main():
    data_dir = os.path.dirname(os.path.abspath(__file__))
    publishers = {}

    # Collect all books
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
    api_found = 0

    for i, book in enumerate(all_books):
        title = book["title"]

        # Check known publishers first
        if title in KNOWN_PUBLISHERS:
            publishers[title] = KNOWN_PUBLISHERS[title]
            print(f"[{i+1}/{total}] {title} -> {KNOWN_PUBLISHERS[title]} (known)")
            continue

        # Try Google Books API
        print(f"[{i+1}/{total}] {title} - searching...")
        pub = search_google_books_publisher(title, book["author"])
        time.sleep(0.3)

        if pub:
            publishers[title] = pub
            api_found += 1
            print(f"  -> {pub}")
        else:
            print(f"  -> NOT FOUND")

    # Save
    output_file = os.path.join(data_dir, "publishers.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(publishers, f, ensure_ascii=False, indent=2)

    print(f"\nDone! Known: {len(KNOWN_PUBLISHERS)}, API: {api_found}, Total: {len(publishers)}")


if __name__ == "__main__":
    main()
