"""Merge data from batch files and all_missing.json into one comprehensive missing data file."""
import json
import os
import glob

data_dir = os.path.dirname(os.path.abspath(__file__))

# Load existing all_missing.json
all_missing = {}
main_file = os.path.join(data_dir, "all_missing.json")
if os.path.exists(main_file):
    with open(main_file, "r", encoding="utf-8") as f:
        all_missing = json.load(f)

# Load batch files and merge (batch data takes priority for bol.com covers)
for batch_file in sorted(glob.glob(os.path.join(data_dir, "missing_batch*.json"))):
    with open(batch_file, "r", encoding="utf-8") as f:
        batch = json.load(f)
    for entry in batch:
        title = entry["title"]
        if title not in all_missing:
            all_missing[title] = {}
        for key in ["isbn", "pages", "publication_date", "cover_front"]:
            val = entry.get(key)
            if val:
                # Prefer bol.com covers over openlibrary
                if key == "cover_front" and "bol.com" in str(val):
                    all_missing[title][key] = val
                elif not all_missing[title].get(key):
                    all_missing[title][key] = val

# Save merged result
with open(main_file, "w", encoding="utf-8") as f:
    json.dump(all_missing, f, ensure_ascii=False, indent=2)

# Count covers
covers = sum(1 for v in all_missing.values() if v.get("cover_front"))
print(f"Merged {len(all_missing)} books, {covers} with covers")
