"""
Parses the full LSJ (Liddell-Scott-Jones) Greek-English Lexicon from
PerseusDL/lexica into a lemma -> gloss lookup table. LSJ headwords are
encoded in Beta Code (ASCII transliteration), converted here to Unicode
Greek so they can be matched directly against CLTK lemmas.

Usage:
    python parse_lsj.py
Reads data/lsj/*.xml, writes data/processed/lsj_index.json
"""
import glob
import json
import os
import re
import xml.etree.ElementTree as ET

import beta_code

LSJ_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "lsj")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "lsj_index.json")

MAX_GLOSS_LEN = 300


def text_of(elem):
    return "".join(elem.itertext())


def extract_gloss(entry_elem):
    """Join the <tr> (translation) elements' text as a short gloss.
    Multiple <sense> blocks often repeat the same core translation
    (e.g. "wrath" under senses A, A.I, A.II), so de-duplicate while
    preserving first-seen order.
    """
    trs = entry_elem.findall(".//tr")
    seen = set()
    parts = []
    for tr in trs:
        t = text_of(tr).strip().rstrip(",;")
        if t and t.lower() not in seen:
            seen.add(t.lower())
            parts.append(t)
    gloss = "; ".join(parts)
    gloss = re.sub(r"\s+", " ", gloss).strip()
    if len(gloss) > MAX_GLOSS_LEN:
        gloss = gloss[:MAX_GLOSS_LEN].rsplit(" ", 1)[0] + "..."
    return gloss


def to_unicode(beta):
    beta = beta.strip()
    # LSJ disambiguates homonyms with a trailing digit on the key, e.g.
    # "e)/xw1" / "e)/xw2" for the two unrelated verbs both spelled ἔχω.
    # Left in place, the digit corrupts the Beta Code conversion and the
    # resulting key never matches the real lemma. Strip it before
    # converting; homonym glosses are merged by the caller regardless.
    beta = re.sub(r"\d+$", "", beta)
    # strip trailing punctuation/annotation noise sometimes present in `key`
    beta = re.sub(r"[.,;]+$", "", beta)
    try:
        return beta_code.beta_code_to_greek(beta)
    except Exception:
        return None


def parse_file(path):
    entries = {}
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        print(f"  PARSE ERROR in {os.path.basename(path)}: {e}")
        return entries

    root = tree.getroot()
    for entry in root.iter("entryFree"):
        key = entry.get("key")
        if not key:
            orth = entry.find("orth")
            if orth is None:
                continue
            key = text_of(orth)
        headword = to_unicode(key)
        if not headword:
            continue
        gloss = extract_gloss(entry)
        if not gloss:
            continue
        # Multiple entries can share a headword (homonyms); keep the longest gloss.
        if headword not in entries or len(gloss) > len(entries[headword]):
            entries[headword] = gloss
    return entries


def main():
    files = sorted(glob.glob(os.path.join(LSJ_DIR, "*.xml")))
    all_entries = {}
    for path in files:
        entries = parse_file(path)
        all_entries.update(entries)
        print(f"{os.path.basename(path)}: {len(entries)} entries (running total: {len(all_entries)})")

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=1)

    print(f"\nTotal LSJ headwords indexed: {len(all_entries)}")


if __name__ == "__main__":
    main()
