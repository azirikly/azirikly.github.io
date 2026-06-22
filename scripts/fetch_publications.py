"""
Fetch publications from Zotero "My Publications" and write to data/publications.json.
Uses the public Zotero API — no API key required.
Run from the repo root:  python scripts/fetch_publications.py
"""
import json
import urllib.request
import urllib.parse
from datetime import date
from pathlib import Path

ZOTERO_USER_ID = "20831485"
OUTPUT = Path(__file__).parent.parent / "data" / "publications.json"

ITEM_TYPE_MAP = {
    "journalArticle":      "journal",
    "conferencePaper":     "conference",
    "preprint":            "preprint",
    "book":                "book",
    "bookSection":         "book-chapter",
    "report":              "report",
    "thesis":              "thesis",
    "manuscript":          "preprint",
    "presentation":        "talk",
}


def fetch_all_items():
    items, start, limit = [], 0, 100
    while True:
        params = urllib.parse.urlencode({
            "format": "json",
            "v": "3",
            "limit": limit,
            "start": start,
        })
        url = f"https://api.zotero.org/users/{ZOTERO_USER_ID}/publications/items?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "academic-website/1.0"})
        with urllib.request.urlopen(req) as resp:
            batch = json.loads(resp.read())
        if not batch:
            break
        items.extend(batch)
        if len(batch) < limit:
            break
        start += limit
    return items


def parse_item(raw):
    data = raw.get("data", {})
    bib  = data

    creators = bib.get("creators", [])
    author_parts = []
    for c in creators:
        if c.get("name"):
            author_parts.append(c["name"])
        else:
            first = c.get("firstName", "")
            last  = c.get("lastName", "")
            author_parts.append(f"{first} {last}".strip() if first else last)
    authors = ", ".join(author_parts)

    venue = (
        bib.get("publicationTitle")
        or bib.get("conferenceName")
        or bib.get("publisher")
        or bib.get("bookTitle")
        or ""
    )

    year = ""
    raw_date = bib.get("date", "")
    if raw_date:
        year = raw_date[:4]

    url = bib.get("url", "")

    item_type = ITEM_TYPE_MAP.get(bib.get("itemType", ""), "other")

    return {
        "title":   bib.get("title", "").strip(),
        "authors": authors,
        "venue":   venue.strip(),
        "year":    year,
        "type":    item_type,
        "url":     url,
    }


def fetch():
    print(f"Fetching Zotero My Publications for user {ZOTERO_USER_ID} …")
    raw_items = fetch_all_items()
    print(f"  Retrieved {len(raw_items)} items")

    publications = [parse_item(r) for r in raw_items]
    publications = [p for p in publications if p["title"]]
    publications.sort(
        key=lambda p: int(p["year"]) if p["year"].isdigit() else 0,
        reverse=True,
    )

    for i, p in enumerate(publications):
        print(f"  [{i+1}] {p['year']}  {p['title'][:70]}")

    payload = {
        "last_updated":  str(date.today()),
        "zotero_user_id": ZOTERO_USER_ID,
        "publications":  publications,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"\nSaved {len(publications)} publications → {OUTPUT}")


if __name__ == "__main__":
    fetch()
