"""
Parses Perseus/canonical-greekLit TEI-EpiDoc XML (Greek edition + English
translation pair) into structured JSON, grouped by book (if the work has
books) and then by "card" milestone -- the citable chunk shared between the
Greek line numbering and the English prose paragraphs. Card (and line)
numbering restarts at 1 within each book, so book context must be tracked
to avoid collisions.

Usage:
    python parse_tei.py <greek.xml> <english.xml> <output.json> --title "Iliad" --author "Homer" --urn "..."
"""
import argparse
import json
import xml.etree.ElementTree as ET

TEI_NS = "{http://www.tei-c.org/ns/1.0}"


def is_book_div(elem):
    tag = elem.tag.replace(TEI_NS, "")
    return tag == "div" and elem.get("type") == "textpart" and (elem.get("subtype") or "").lower() == "book"


def text_excluding_notes(elem):
    """Like elem.itertext() joined, but skips <note> subtrees (footnote markers/apparatus)."""
    parts = []
    if elem.text:
        parts.append(elem.text)
    for child in elem:
        tag = child.tag.replace(TEI_NS, "")
        if tag != "note":
            parts.append(text_excluding_notes(child))
        if child.tail:
            parts.append(child.tail)
    return "".join(parts)


def is_card_div(elem):
    tag = elem.tag.replace(TEI_NS, "")
    return tag == "div" and elem.get("type") == "textpart" and (elem.get("subtype") or "").lower() == "card"


def parse_greek(path):
    """Returns list of books: [{"book": "1", "cards": [{"n": "1", "lines": [...]}]}]
    If the work has no book divisions, returns a single synthetic book "1".
    """
    tree = ET.parse(path)
    root = tree.getroot()
    body = root.find(f".//{TEI_NS}body")

    books = []

    def parse_book(elem, book_n):
        cards = []
        current_card = None

        def walk(e):
            nonlocal current_card
            for child in e:
                tag = child.tag.replace(TEI_NS, "")
                if tag == "milestone" and child.get("unit") == "card":
                    current_card = {"n": child.get("n"), "lines": []}
                    cards.append(current_card)
                elif tag == "l":
                    if current_card is None:
                        current_card = {"n": child.get("n"), "lines": []}
                        cards.append(current_card)
                    text = text_excluding_notes(child).strip()
                    current_card["lines"].append({"n": child.get("n"), "text": text})
                else:
                    walk(child)

        walk(elem)
        return {"book": book_n, "cards": cards}

    book_divs = [c for c in body.iter() if is_book_div(c)]
    if book_divs:
        for i, bdiv in enumerate(book_divs, start=1):
            books.append(parse_book(bdiv, bdiv.get("n") or str(i)))
    else:
        books.append(parse_book(body, "1"))

    return books


def parse_english(path):
    """Returns dict: {"1": {"1": "text...", "29": "text..."}, "2": {...}}
    Outer key = book number, inner key = card number.
    """
    tree = ET.parse(path)
    root = tree.getroot()
    body = root.find(f".//{TEI_NS}body")

    all_books = {}

    def parse_book(elem, book_n):
        result = {}
        current_n = None
        buffer = []

        def flush():
            nonlocal buffer
            if current_n is not None:
                text = " ".join(" ".join(buffer).split())
                if text:
                    result[current_n] = (result.get(current_n, "") + " " + text).strip()
            buffer = []

        def walk(e):
            nonlocal current_n
            if e.text:
                buffer.append(e.text)
            for child in e:
                tag = child.tag.replace(TEI_NS, "")
                is_card_milestone = tag == "milestone" and child.get("unit") == "card"
                if is_card_milestone:
                    flush()
                    current_n = child.get("n")
                elif is_card_div(child):
                    flush()
                    current_n = child.get("n")
                    walk(child)
                elif is_book_div(child):
                    pass  # handled at outer level; skip nested book divs here
                elif tag == "note":
                    pass  # skip footnote marker/body text; keep only its .tail (handled below)
                else:
                    walk(child)
                if child.tail:
                    buffer.append(child.tail)

        walk(elem)
        flush()
        return result

    book_divs = [c for c in body.iter() if is_book_div(c)]
    if book_divs:
        for i, bdiv in enumerate(book_divs, start=1):
            all_books[bdiv.get("n") or str(i)] = parse_book(bdiv, bdiv.get("n") or str(i))
    else:
        all_books["1"] = parse_book(body, "1")

    return all_books


def merge(greek_books, english_by_book):
    merged_books = []
    for book in greek_books:
        english_by_card = english_by_book.get(book["book"], {})
        cards = []
        aligned = 0
        for card in book["cards"]:
            eng = english_by_card.get(card["n"], "")
            if eng:
                aligned += 1
            cards.append({
                "card": card["n"],
                "greek_lines": card["lines"],
                "english": eng,
            })
        merged_books.append({"book": book["book"], "cards": cards})
    return merged_books


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("greek_xml")
    ap.add_argument("english_xml")
    ap.add_argument("output_json")
    ap.add_argument("--title", required=True)
    ap.add_argument("--author", required=True)
    ap.add_argument("--urn", required=True)
    args = ap.parse_args()

    greek_books = parse_greek(args.greek_xml)
    english_by_book = parse_english(args.english_xml)
    merged_books = merge(greek_books, english_by_book)

    output = {
        "title": args.title,
        "author": args.author,
        "urn": args.urn,
        "books": merged_books,
    }

    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    total_cards = sum(len(b["cards"]) for b in merged_books)
    total_lines = sum(len(c["greek_lines"]) for b in merged_books for c in b["cards"])
    aligned_cards = sum(1 for b in merged_books for c in b["cards"] if c["english"])
    print(f"Parsed {args.title}: {len(merged_books)} books, {total_cards} cards, "
          f"{total_lines} lines, {aligned_cards}/{total_cards} cards with English text")


if __name__ == "__main__":
    main()
