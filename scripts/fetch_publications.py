"""
Fetch publications from Semantic Scholar and write to data/publications.json.
Uses the free public Semantic Scholar API — no key required.
Run from the repo root:  python scripts/fetch_publications.py
"""
import json
import time
import urllib.request
import urllib.error
from datetime import date
from pathlib import Path

SEMANTIC_SCHOLAR_AUTHOR_ID = "2216860"
OUTPUT = Path(__file__).parent.parent / "data" / "publications.json"

FIELDS = "title,authors,year,venue,citationCount,externalIds,openAccessPdf"


def fetch_all():
    items, offset, limit = [], 0, 100
    while True:
        url = (
            f"https://api.semanticscholar.org/graph/v1/author/"
            f"{SEMANTIC_SCHOLAR_AUTHOR_ID}/papers"
            f"?fields={FIELDS}&limit={limit}&offset={offset}"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "academic-website/1.0"})
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print("  Rate limited — waiting 10 s …")
                time.sleep(10)
                continue
            raise
        batch = data.get("data", [])
        items.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
    return items


def paper_url(paper):
    if paper.get("openAccessPdf") and paper["openAccessPdf"].get("url"):
        return paper["openAccessPdf"]["url"]
    ext = paper.get("externalIds") or {}
    if ext.get("DOI"):
        return f"https://doi.org/{ext['DOI']}"
    if ext.get("ArXiv"):
        return f"https://arxiv.org/abs/{ext['ArXiv']}"
    return ""


def parse(paper):
    authors = ", ".join(a.get("name", "") for a in paper.get("authors", []))
    return {
        "title":     (paper.get("title") or "").strip(),
        "authors":   authors,
        "venue":     paper.get("venue") or "",
        "year":      str(paper.get("year") or ""),
        "citations": paper.get("citationCount") or 0,
        "url":       paper_url(paper),
    }


def fetch():
    print(f"Fetching papers for Semantic Scholar author {SEMANTIC_SCHOLAR_AUTHOR_ID} …")
    raw = fetch_all()
    print(f"  Retrieved {len(raw)} papers")

    pubs = [parse(p) for p in raw if p.get("title")]
    pubs.sort(
        key=lambda p: (int(p["year"]) if p["year"].isdigit() else 0, p["citations"]),
        reverse=True,
    )

    for i, p in enumerate(pubs):
        print(f"  [{i+1:2d}] {p['year']}  {p['title'][:70]}")

    payload = {
        "last_updated": str(date.today()),
        "semantic_scholar_author_id": SEMANTIC_SCHOLAR_AUTHOR_ID,
        "publications": pubs,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"\nSaved {len(pubs)} publications → {OUTPUT}")


if __name__ == "__main__":
    fetch()
