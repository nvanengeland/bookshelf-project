"""Fetch book details from Open Library API for all books."""
import json
import urllib.request
import urllib.parse
import time
import sys
import os

def search_book(title, author):
    """Search Open Library for a book and return metadata."""
    query = f"{title} {author}"
    params = urllib.parse.urlencode({
        "q": query,
        "limit": 3,
        "fields": "key,title,author_name,isbn,number_of_pages_median,first_publish_year,subject,language,cover_i"
    })
    url = f"https://openlibrary.org/search.json?{params}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BookshelfProject/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if data.get("docs"):
            doc = data["docs"][0]

            # Get ISBN (prefer ISBN-13)
            isbn = None
            if doc.get("isbn"):
                for i in doc["isbn"]:
                    if len(i) == 13:
                        isbn = i
                        break
                if not isbn:
                    isbn = doc["isbn"][0]

            # Cover URL from cover_i
            cover_front = None
            cover_back = None
            if doc.get("cover_i"):
                cover_front = f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-L.jpg"
            elif isbn:
                cover_front = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"

            # Languages
            langs = doc.get("language", [])

            # Subjects for genre
            subjects = doc.get("subject", [])[:10]

            return {
                "isbn": isbn,
                "pages": doc.get("number_of_pages_median"),
                "first_published": doc.get("first_publish_year"),
                "cover_front": cover_front,
                "subjects": subjects,
                "languages": langs,
                "ol_title": doc.get("title"),
                "ol_author": doc.get("author_name", [None])[0],
            }
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)

    return None


def enrich_book(book, ol_data):
    """Combine raw book data with Open Library data and knowledge-based defaults."""
    result = {
        "title": book["title"],
        "author": book["author"],
        "isbn": None,
        "cover_front": None,
        "cover_back": None,
        "synopsis": "",
        "pages": None,
        "genre": "",
        "age_category": "",
        "publication_date": None,
        "original_language": "",
    }

    if ol_data:
        result["isbn"] = ol_data.get("isbn")
        result["cover_front"] = ol_data.get("cover_front")
        result["pages"] = ol_data.get("pages")
        result["publication_date"] = ol_data.get("first_published")

        # Determine genre from subjects
        subjects = [s.lower() for s in ol_data.get("subjects", [])]
        genre_map = {
            "romance": "Romantiek",
            "love": "Romantiek",
            "thriller": "Thriller",
            "mystery": "Mystery",
            "fantasy": "Fantasy",
            "science fiction": "Science Fiction",
            "horror": "Horror",
            "young adult": "Young Adult",
            "juvenile": "Jeugd",
            "children": "Kinderboek",
            "historical": "Historisch",
            "adventure": "Avontuur",
            "humor": "Humor",
            "graphic novel": "Graphic Novel",
            "comics": "Strip",
            "psychology": "Psychologie",
            "mythology": "Mythologie",
            "literary fiction": "Literaire fictie",
        }
        genres = []
        for subj in subjects:
            for key, val in genre_map.items():
                if key in subj and val not in genres:
                    genres.append(val)
        result["genre"] = ", ".join(genres[:3]) if genres else "Fictie"

        # Language
        lang_map = {"eng": "Engels", "dut": "Nederlands", "fre": "Frans", "ger": "Duits", "spa": "Spaans"}
        langs = ol_data.get("languages", [])
        if langs:
            result["original_language"] = lang_map.get(langs[0], langs[0])

    return result


def process_grade(grade_file, output_file):
    """Process all books in a grade file."""
    with open(grade_file, "r", encoding="utf-8") as f:
        books = json.load(f)

    results = []
    total = len(books)

    for i, book in enumerate(books):
        print(f"  [{i+1}/{total}] {book['title']} - {book['author']}")
        ol_data = search_book(book["title"], book["author"])
        enriched = enrich_book(book, ol_data)
        results.append(enriched)

        if ol_data:
            isbn_str = ol_data.get('isbn', 'none')
            pages_str = ol_data.get('pages', '?')
            print(f"    -> ISBN: {isbn_str}, Pages: {pages_str}")
        else:
            print(f"    -> Not found in Open Library")

        time.sleep(0.3)  # Rate limit

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"  Saved {len(results)} books to {output_file}")
    return results


if __name__ == "__main__":
    grade = sys.argv[1] if len(sys.argv) > 1 else "graad_1"
    data_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(data_dir, f"{grade}_raw.json")
    output_file = os.path.join(data_dir, f"{grade}_enriched.json")

    print(f"Processing {grade}...")
    process_grade(input_file, output_file)
    print("Done!")
