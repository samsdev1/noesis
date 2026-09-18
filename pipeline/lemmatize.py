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

# CLTK's lemmatizer frequently fails to resolve elided function words --
# it just echoes the elided surface form back as its own "lemma" (e.g.
# "δʼ" -> "δʼ" instead of "δέ"), which then can't match anything in LSJ
# or the concordance. These are a closed, well-known set in Greek, so a
# direct table is more reliable here than trying to get the NLP model to
# handle them. Covers elision before both smooth and rough breathing
# (the latter aspirates a preceding stop: κατά -> καθʼ, ἐπί -> ἐφʼ, etc).
ELISION_MAP = {
    "δʼ": "δέ", "δ'": "δέ", "δ’": "δέ",
    "τʼ": "τε", "τ'": "τε", "τ’": "τε",
    "θʼ": "τε", "θ'": "τε", "θ’": "τε",
    "γʼ": "γε", "γ'": "γε", "γ’": "γε",
    "μʼ": "ἐγώ", "μ'": "ἐγώ", "μ’": "ἐγώ",
    "σʼ": "σύ", "σ'": "σύ", "σ’": "σύ",
    "ῥʼ": "ἄρα", "ῥ'": "ἄρα", "ῥ’": "ἄρα",
    "ἄρʼ": "ἄρα", "ἄρ'": "ἄρα", "ἄρ’": "ἄρα",
    "ἀλλʼ": "ἀλλά", "ἀλλ'": "ἀλλά", "ἀλλ’": "ἀλλά",
    "οὐδʼ": "οὐδέ", "οὐδ'": "οὐδέ", "οὐδ’": "οὐδέ",
    "μηδʼ": "μηδέ", "μηδ'": "μηδέ", "μηδ’": "μηδέ",
    "ἐπʼ": "ἐπί", "ἐπ'": "ἐπί", "ἐπ’": "ἐπί",
    "ἐφʼ": "ἐπί", "ἐφ'": "ἐπί", "ἐφ’": "ἐπί",
    "ἀπʼ": "ἀπό", "ἀπ'": "ἀπό", "ἀπ’": "ἀπό",
    "ἀφʼ": "ἀπό", "ἀφ'": "ἀπό", "ἀφ’": "ἀπό",
    "ὑπʼ": "ὑπό", "ὑπ'": "ὑπό", "ὑπ’": "ὑπό",
    "ὑφʼ": "ὑπό", "ὑφ'": "ὑπό", "ὑφ’": "ὑπό",
    "καταʼ": "κατά", "κατʼ": "κατά", "κατ'": "κατά", "κατ’": "κατά",
    "καθʼ": "κατά", "καθ'": "κατά", "καθ’": "κατά",
    "μεταʼ": "μετά", "μετʼ": "μετά", "μετ'": "μετά", "μετ’": "μετά",
    "μεθʼ": "μετά", "μεθ'": "μετά", "μεθ’": "μετά",
    "παρʼ": "παρά", "παρ'": "παρά", "παρ’": "παρά",
    "ἀνʼ": "ἀνά", "ἀν'": "ἀνά", "ἀν’": "ἀνά",
}


def resolve_elision(lemma, surface):
    """Falls back to a known table when CLTK returns the elided surface
    form unchanged as the lemma."""
    if lemma == surface and surface in ELISION_MAP:
        return ELISION_MAP[surface]
    return lemma


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
                lemma = resolve_elision(w.lemma or chunk, chunk)
                segments.append({"type": "word", "text": chunk, "lemma": lemma, "pos": pos_str})
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
