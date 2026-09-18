"""
Builds approximate word-level Greek-English correspondence within each card,
using the LSJ glosses we already have as the bridge: for each Greek content
word (noun/verb/adjective/adverb/pronoun/numeral), look for one of its gloss
terms appearing in that card's English translation, in roughly the same
left-to-right order (translations mostly preserve clause order). This is a
heuristic, not real alignment data -- but it's a large improvement over
highlighting the entire paragraph, and it's honest about what we actually
have (a dictionary, not a parallel treebank).

Usage:
    python align_cards.py
Reads/writes data/processed/*.json in place, adding "english_segments" to
each card (same word/sep segment structure as Greek lines, so the frontend
can render both uniformly).
"""
import glob
import json
import os
import re

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

CONTENT_POS = {"noun", "verb", "adjective", "adverb", "pronoun", "numeral", "interjection"}

STOPWORDS = {
    "the", "a", "an", "of", "to", "in", "on", "and", "or", "but", "for", "with",
    "is", "was", "were", "be", "been", "being", "are", "am", "as", "at", "by",
    "from", "that", "this", "these", "those", "it", "its", "his", "her", "their",
    "them", "he", "she", "they", "you", "i", "we", "us", "our", "your", "my",
    "who", "which", "what", "not", "no", "so", "let", "yet", "still",
    "then", "than", "if", "when", "while", "will", "would", "shall", "should",
    "may", "might", "must", "can", "could", "do", "did", "does", "up", "down",
    "out", "on", "off", "over", "again", "there", "here", "thus", "now",
    "one", "two", "also", "own", "such", "some", "any", "all", "both", "each",
}

MIN_CANDIDATE_LEN = 4

ENG_TOKEN_RE = re.compile(r"[A-Za-z']+|[^A-Za-z']+")


def gloss_candidates(gloss):
    """Split an LSJ gloss into ordered candidate terms, filtered to useful ones."""
    if not gloss:
        return []
    parts = re.split(r"[;,]", gloss)
    candidates = []
    for p in parts:
        p = p.strip().lower()
        # keep short phrases (<=3 words) as-is, since some glosses are multi-word idioms
        words = p.split()
        if not (1 <= len(words) <= 3 and p):
            continue
        # single-word candidates must be long enough and not a stopword to
        # avoid promiscuous false matches (e.g. "let", "are")
        if len(words) == 1 and (len(words[0]) < MIN_CANDIDATE_LEN or words[0] in STOPWORDS):
            continue
        candidates.append(p)
    return candidates


def tokenize_english(text):
    """Returns list of (text, is_word) preserving exact original text on join."""
    return [(m.group(), m.group().strip().isalpha() or "'" in m.group()) for m in ENG_TOKEN_RE.finditer(text)]


def align_card(card, lsj):
    eng_tokens = tokenize_english(card["english"])
    claimed = [False] * len(eng_tokens)
    word_alignment = [None] * len(eng_tokens)  # lemma assigned to each token index, if any

    greek_words = []
    for line in card["greek_lines"]:
        for seg in line.get("segments", []):
            if seg["type"] == "word":
                greek_words.append(seg)

    search_cursor = 0  # monotonic-ish: prefer matches at/after this position
    for gw in greek_words:
        if gw["pos"] not in CONTENT_POS:
            continue
        gloss = lsj.get(gw["lemma"])
        candidates = gloss_candidates(gloss)
        if not candidates:
            continue

        match_idx = None
        # Pass 1: search from search_cursor forward for an exact (unclaimed) match.
        for cand in candidates:
            cand_words = cand.split()
            n = len(cand_words)
            for start in list(range(search_cursor, len(eng_tokens))) + list(range(0, search_cursor)):
                if claimed[start] or not eng_tokens[start][1]:
                    continue
                window_words = []
                idxs = []
                j = start
                while j < len(eng_tokens) and len(window_words) < n:
                    if eng_tokens[j][1]:
                        window_words.append(eng_tokens[j][0].lower().strip("'"))
                        idxs.append(j)
                    j += 1
                if len(window_words) == n and window_words == cand_words:
                    match_idx = idxs
                    break
            if match_idx:
                break

        if match_idx:
            for idx in match_idx:
                claimed[idx] = True
                word_alignment[idx] = gw["lemma"]
            search_cursor = max(match_idx) + 1

    # Rebuild english_segments preserving exact original text, tagging aligned words.
    segments = []
    for i, (text, is_word) in enumerate(eng_tokens):
        if is_word and text.lower().strip("'") not in STOPWORDS and word_alignment[i]:
            segments.append({"type": "word", "text": text, "alignedLemma": word_alignment[i]})
        else:
            segments.append({"type": "sep", "text": text})
    return segments


def process_file(path, lsj):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    aligned_count = 0
    total_count = 0
    for book in data["books"]:
        for card in book["cards"]:
            if not card["english"]:
                continue
            card["english_segments"] = align_card(card, lsj)
            total_count += 1
            if any(s["type"] == "word" and "alignedLemma" in s for s in card["english_segments"]):
                aligned_count += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Aligned {data['title']}: {aligned_count}/{total_count} cards have at least one word match")


def main():
    lsj_path = os.path.join(PROCESSED_DIR, "lsj_index.json")
    with open(lsj_path, "r", encoding="utf-8") as f:
        lsj = json.load(f)

    exclude = ("concordance", "lsj_index")
    files = [f for f in glob.glob(os.path.join(PROCESSED_DIR, "*.json")) if not any(x in f for x in exclude)]
    for path in files:
        process_file(path, lsj)


if __name__ == "__main__":
    main()
