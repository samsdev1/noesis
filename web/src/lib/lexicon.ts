import fs from "fs";
import path from "path";

export type Occurrence = {
  work: string;
  urn: string;
  book: string;
  card: string;
  line: string;
  surface: string;
};

const PROCESSED_DIR = path.join(process.cwd(), "..", "data", "processed");

let lsjCache: Record<string, string> | null = null;
let concordanceCache: Record<string, Occurrence[]> | null = null;

function loadLsj(): Record<string, string> {
  if (!lsjCache) {
    const raw = fs.readFileSync(path.join(PROCESSED_DIR, "lsj_index.json"), "utf-8");
    lsjCache = JSON.parse(raw);
  }
  return lsjCache!;
}

function loadConcordance(): Record<string, Occurrence[]> {
  if (!concordanceCache) {
    const raw = fs.readFileSync(path.join(PROCESSED_DIR, "concordance.json"), "utf-8");
    concordanceCache = JSON.parse(raw);
  }
  return concordanceCache!;
}

export function lookupLemma(lemma: string) {
  const lsj = loadLsj();
  const concordance = loadConcordance();
  const occurrences = concordance[lemma] || [];
  return {
    lemma,
    gloss: lsj[lemma] || null,
    occurrenceCount: occurrences.length,
    occurrences: occurrences.slice(0, 12),
  };
}
