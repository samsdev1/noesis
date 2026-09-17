"""
Adds a lemma to every Greek word token across all processed texts, and
builds a corpus-wide concordance (lemma -> every occurrence, across all
texts) so that hovering a word can show "this lemma also appears in..."
even as more texts get added later.

Usage:
    python lemmatize.py
Reads/writes data/processed/*.json in place (adds "tokens" per line),
and writes data/processed/concordance.json.
"""
import json
import glob
import os
import re

from cltk.core.data_types import Pipeline
from cltk.languages.utils import get_lang
from cltk.dependency.processes import GreekSpacyProcess
from cltk.alphabet.processes import GreekNormalizeProcess
from cltk.nlp import NLP

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

custom_pipeline = Pipeline(
    language=get_lang("grc"),
    processes=[GreekNormalizeProcess, GreekSpacyProcess],
    description="lemma-only pipeline",
)
nlp = NLP(language="grc", custom_pipeline=custom_pipeline, suppress_banner=True)

WORD_RE = re.compile(r"[Ͱ-Ͽἀ-῿]+(?:['’ʼ][Ͱ-Ͽἀ-῿]*)?", re.UNICODE)
SEGMENT_RE = re.compile(r"[Ͱ-Ͽἀ-῿]+(?:['’ʼ][Ͱ-Ͽἀ-῿]*)?|[^Ͱ-Ͽἀ-῿]+", re.UNICODE)


def lemmatize_line(text):
    """Returns an ordered list of segments reconstructing the exact original
    text: {"type": "word", "text": ..., "lemma": ..., "pos": ...} for Greek
    words, and {"type": "sep", "text": ...} for whitespace/punctuation between
    them. CLTK's word list (filtered to real words) is zipped positionally
    against a regex segmentation of the original string, since spaCy doesn't
    guarantee exact whitespace round-tripping.
    """
    doc = nlp.analyze(text=text)
    cltk_words = [w for w in doc.words if w.string and WORD_RE.fullmatch(w.string)]

    segments = []
    word_i = 0
    for m in SEGMENT_RE.finditer(text):
        chunk = m.group()
        if WORD_RE.fullmatch(chunk):
            if word_i < len(cltk_words):
                w = cltk_words[word_i]
                pos_str = w.pos.name if w.pos else ""
                segments.append({"type": "word", "text": chunk, "lemma": w.lemma or chunk, "pos": pos_str})
                word_i += 1
            else:
                segments.append({"type": "word", "text": chunk, "lemma": chunk, "pos": ""})
        else:
            segments.append({"type": "sep", "text": chunk})
    return segments


def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    title = data["title"]
    total_lines = 0
    for book in data["books"]:
        for card in book["cards"]:
            for line in card["greek_lines"]:
                line["segments"] = lemmatize_line(line["text"])
                total_lines += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Lemmatized {title}: {total_lines} lines")
    return data


def build_concordance(all_data):
    """lemma -> list of {work, book, card, line, surface}"""
    concordance = {}
    for data in all_data:
        title = data["title"]
        urn = data["urn"]
        for book in data["books"]:
            for card in book["cards"]:
                for line in card["greek_lines"]:
                    for seg in line.get("segments", []):
                        if seg["type"] != "word":
                            continue
                        lemma = seg["lemma"]
                        concordance.setdefault(lemma, []).append({
                            "work": title,
                            "urn": urn,
                            "book": book["book"],
                            "card": card["card"],
                            "line": line["n"],
                            "surface": seg["text"],
                        })
    return concordance


def main():
    exclude = ("concordance", "lsj_index")
    files = [f for f in glob.glob(os.path.join(PROCESSED_DIR, "*.json")) if not any(x in f for x in exclude)]
    all_data = []
    for path in files:
        all_data.append(process_file(path))

    concordance = build_concordance(all_data)
    out_path = os.path.join(PROCESSED_DIR, "concordance.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(concordance, f, ensure_ascii=False, indent=2)

    print(f"Concordance: {len(concordance)} unique lemmas, "
          f"{sum(len(v) for v in concordance.values())} total occurrences")


if __name__ == "__main__":
    main()
