import json

# Manually curated book lists per grade, cleaned from the Excel data
# Format: {"title": "...", "author": "..."}

graad_1 = [
    {"title": "Binding 13", "author": "Chloe Walsh"},
    {"title": "Little Women", "author": "Louisa May Alcott"},
    {"title": "The Perks of Being a Wallflower", "author": "Stephen Chbosky"},
    {"title": "Iene miene mutte", "author": "M.J. Arlidge"},
    {"title": "Girl in Pieces", "author": "Kathleen Glasgow"},
    {"title": "Juniper", "author": "Monica Furlong"},
    {"title": "De heksen", "author": "Roald Dahl"},
    {"title": "Het Pumpkin Spice Café", "author": "Steffie Kramer"},
    {"title": "It Girl: Team Awkward", "author": "Katy Birchall"},
    {"title": "FunJungle: Gekidnapt!", "author": "Stuart Gibbs"},
    {"title": "Percy Jackson en de Olympiërs: De bliksemschicht dief", "author": "Rick Riordan"},
    {"title": "De magische apotheek", "author": "Anna Ruhe"},
    {"title": "De trein van vier over twaalf", "author": "Malika Ferdjoukh"},
    {"title": "Warrior Cats: De wildernis in", "author": "Erin Hunter"},
    {"title": "1991", "author": "Aske Mortier"},
    {"title": "Echo uit de diepte", "author": "Pam Muñoz Ryan"},
    {"title": "Films die nergens draaien", "author": "Dirk Bracke"},
    {"title": "Code Rood", "author": "Dirk Bracke"},
    {"title": "De Grijze Jager: De ruïnes van Doorn", "author": "John Flanagan"},
    {"title": "Woodwalkers", "author": "Katja Brandis"},
    {"title": "Harry Potter en de Steen der Wijzen", "author": "J.K. Rowling"},
    {"title": "Geen beste dag voor voodoo", "author": "Jeff Strand"},
    {"title": "Dumplin'", "author": "Julie Murphy"},
    {"title": "Supernerd of Topmodel", "author": "Crystal Velasquez"},
    {"title": "X-Scape", "author": "Michael Sels"},
    {"title": "Sunrise on the Reaping", "author": "Suzanne Collins"},
    {"title": "De Zeven Zussen", "author": "Lucinda Riley"},
    {"title": "Mythos", "author": "Stephen Fry"},
    {"title": "Helden", "author": "Stephen Fry"},
    {"title": "Surrounded by Narcissists", "author": "Thomas Erikson"},
    {"title": "Dir-Yak Omnibus I", "author": "Aimée de Jongh"},
    {"title": "Geen beste dag voor voodoo", "author": "Jeff Strand"},
]

graad_2 = [
    {"title": "The Hunger Games", "author": "Suzanne Collins"},
    {"title": "De laatste dochter", "author": "R.S.E. Gommer"},
    {"title": "X-Scape", "author": "Michael Sels"},
    {"title": "Five Survive", "author": "Holly Jackson"},
    {"title": "Percy Jackson en de Olympiërs", "author": "Rick Riordan"},
    {"title": "The Cruel Prince", "author": "Holly Black"},
    {"title": "Once Upon a Broken Heart", "author": "Stephanie Garber"},
    {"title": "Obsidian (Lux serie)", "author": "Jennifer L. Armentrout"},
    {"title": "Talon", "author": "Julie Kagawa"},
    {"title": "From Blood and Ash", "author": "Jennifer L. Armentrout"},
    {"title": "Shatter Me (Alizeh serie)", "author": "Tahereh Mafi"},
    {"title": "When It's Real", "author": "Erin Watt"},
    {"title": "De Hongerspelen", "author": "Suzanne Collins"},
    {"title": "Schaduw van de Vos", "author": "Julie Kagawa"},
    {"title": "De Kinderen van Orpheus", "author": "Petra Doom"},
    {"title": "Zeis", "author": "Neal Shusterman"},
    {"title": "You'd Be Home Now", "author": "Kathleen Glasgow"},
    {"title": "Royals", "author": "Erin Watt"},
    {"title": "No Exit", "author": "Maren Stoffels"},
    {"title": "Doodleuk", "author": "Holly Jackson"},
    {"title": "The Maze Runner", "author": "James Dashner"},
    {"title": "If He Had Been with Me", "author": "Laura Nowlin"},
    {"title": "Gebroken", "author": "Mel Wallis de Vries"},
    {"title": "I Wish You Would", "author": "Eva Des Lauriers"},
    {"title": "Een vloek zo eenzaam", "author": "Brigid Kemmerer"},
    {"title": "Powerless", "author": "Lauren Roberts"},
    {"title": "Thieves' Gambit", "author": "Kayvion Lewis"},
    {"title": "De duistere profetie", "author": "Tahereh Mafi"},
    {"title": "Check & Mate", "author": "Ali Hazelwood"},
    {"title": "The Fault in Our Stars", "author": "John Green"},
]

graad_3 = [
    {"title": "Kleine Gelukjes", "author": "Audrey Adelin"},
    {"title": "Schaduwliefde", "author": "Ruta Sepetys"},
    {"title": "IJzerkop", "author": "Jean-Claude Van Rijckeghem"},
    {"title": "One Golden Summer", "author": "Carley Fortune"},
    {"title": "The Maidens", "author": "Alex Michaelides"},
    {"title": "Say You'll Remember Me", "author": "Abby Jimenez"},
    {"title": "Heart Bones", "author": "Colleen Hoover"},
    {"title": "How to Kill Men and Get Away with It", "author": "Katy Brent"},
    {"title": "Better Than the Movies", "author": "Lynn Painter"},
    {"title": "Mr Wrong Number", "author": "Lynn Painter"},
    {"title": "The Housemaid", "author": "Freida McFadden"},
    {"title": "The Seven Husbands of Evelyn Hugo", "author": "Taylor Jenkins Reid"},
    {"title": "The Perfect Marriage", "author": "Jeneva Rose"},
    {"title": "A Thousand Boy Kisses", "author": "Tillie Cole"},
    {"title": "The Murder After the Night Before", "author": "Katy Brent"},
    {"title": "When in Rome", "author": "Sarah Adams"},
    {"title": "Malibu Rising", "author": "Taylor Jenkins Reid"},
    {"title": "The Reappearance of Rachel Price", "author": "Holly Jackson"},
    {"title": "A Good Girl's Guide to Murder", "author": "Holly Jackson"},
    {"title": "Five Survive", "author": "Holly Jackson"},
    {"title": "Letters to the Lost", "author": "Brigid Kemmerer"},
    {"title": "Before We Were Strangers", "author": "Renée Carlino"},
    {"title": "If He Had Been with Me", "author": "Laura Nowlin"},
    {"title": "Anna and the French Kiss", "author": "Stephanie Perkins"},
    {"title": "The Girl on the Train", "author": "Paula Hawkins"},
    {"title": "Binding 13", "author": "Chloe Walsh"},
    {"title": "Until Friday Night", "author": "Abbi Glines"},
    {"title": "The Way I Used to Be", "author": "Amber Smith"},
    {"title": "Throttled", "author": "Lauren Asher"},
    {"title": "Regretting You", "author": "Colleen Hoover"},
    {"title": "November 9", "author": "Colleen Hoover"},
    {"title": "Every Last Word", "author": "Tamara Ireland Stone"},
    {"title": "Heartstopper Volume 1", "author": "Alice Oseman"},
    {"title": "Solitaire", "author": "Alice Oseman"},
    {"title": "Radio Silence", "author": "Alice Oseman"},
    {"title": "I Was Born for This", "author": "Alice Oseman"},
    {"title": "Loveless", "author": "Alice Oseman"},
    {"title": "Red, White & Royal Blue", "author": "Casey McQuiston"},
    {"title": "Lang leve Jane", "author": "Cynthia Hand"},
    {"title": "Lily", "author": "Tom de Cock"},
    {"title": "Storm", "author": "Tom de Cock"},
    {"title": "Maxton Hall College", "author": "Mona Kasten"},
    {"title": "CTRL-A", "author": "Juultje van den Nieuwhof"},
    {"title": "Dit mag niemand weten", "author": "Martine Kamphuis"},
    {"title": "De roep van het hart", "author": "Kiera Cass"},
    {"title": "People We Meet on Vacation", "author": "Emily Henry"},
    {"title": "The Bodyguard", "author": "Katherine Center"},
    {"title": "A Thousand Broken Pieces", "author": "Tillie Cole"},
    {"title": "Picking Daisies on a Sunday", "author": "Ella Miles"},
    {"title": "Moordgids voor lieve meisjes", "author": "Holly Jackson"},
    {"title": "Onderstroom", "author": "Goedele Ghijsen"},
    {"title": "Een lied voor Achilles", "author": "Madeline Miller"},
    {"title": "De kleuren van magie", "author": "V.E. Schwab"},
    {"title": "List & Leugens", "author": "Leigh Bardugo"},
    {"title": "Zeis", "author": "Neal Shusterman"},
    {"title": "Het grote misschien", "author": "John Green"},
    {"title": "Aristoteles & Dante ontdekken de geheimen van het universum", "author": "Benjamin Alire Sáenz"},
    {"title": "Op het einde gaan ze allebei dood", "author": "Adam Silvera"},
    {"title": "Shakespeare kent me beter dan mijn lief", "author": "Coen Simon"},
    {"title": "5 stappen van jou", "author": "Rachael Lippincott"},
    {"title": "Het parfum", "author": "Patrick Süskind"},
]

# Remove duplicates by title
def dedup(books):
    seen = set()
    result = []
    for b in books:
        key = b["title"].lower()
        if key not in seen:
            seen.add(key)
            result.append(b)
    return result

data = {
    "graad_1": dedup(graad_1),
    "graad_2": dedup(graad_2),
    "graad_3": dedup(graad_3),
}

for g, books in data.items():
    print(f"{g}: {len(books)} boeken")
    with open(f"data/{g}_raw.json", "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

print("\nDone!")
