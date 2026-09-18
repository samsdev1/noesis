"use client";

import { useState } from "react";
import Link from "next/link";
import { useReader } from "./ReaderContext";

type LemmaData = {
  lemma: string;
  gloss: string | null;
  occurrenceCount: number;
  occurrences: {
    work: string;
    book: string;
    card: string;
    line: string;
    surface: string;
  }[];
};

const cache = new Map<string, LemmaData>();

function slugify(title: string) {
  return title.toLowerCase().replace(/\s+/g, "-");
}

export default function WordSpan({
  text,
  lemma,
  pos,
  card,
  currentWork,
  currentLine,
  wordId,
}: {
  text: string;
  lemma: string;
  pos: string;
  card: string;
  currentWork: string;
  currentLine: string;
  wordId: string;
}) {
  const { activeWordId, openWord, hovered, setHovered } = useReader();
  const [data, setData] = useState<LemmaData | null>(cache.get(lemma) ?? null);
  const [loading, setLoading] = useState(false);

  const isOpen = activeWordId === wordId;
  const isMatched = !isOpen && hovered?.card === card && hovered?.lemma === lemma;

  async function handleClick() {
    openWord(wordId);
    if (cache.has(lemma)) {
      setData(cache.get(lemma)!);
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`/api/lemma/${encodeURIComponent(lemma)}`);
      const json: LemmaData = await res.json();
      cache.set(lemma, json);
      setData(json);
    } finally {
      setLoading(false);
    }
  }

  const otherOccurrences = (data?.occurrences ?? []).filter(
    (o) => !(o.work === currentWork && o.line === currentLine)
  );

  return (
    <span
      data-word-popup
      data-lemma={lemma}
      data-line={`${currentWork}:${currentLine}`}
      className={`relative cursor-pointer scroll-mt-32 rounded transition-colors ${
        isOpen
          ? "bg-amber-200 dark:bg-amber-900"
          : isMatched
            ? "bg-amber-100 dark:bg-amber-950"
            : "hover:bg-neutral-100 dark:hover:bg-neutral-800"
      }`}
      onMouseEnter={() => setHovered({ card, lemma })}
      onMouseLeave={() => setHovered(null)}
      onClick={handleClick}
    >
      {text}
      {isOpen && (
        <span className="absolute left-1/2 top-full z-50 mt-2 w-72 -translate-x-1/2 rounded-lg border border-neutral-200 bg-white p-3 text-left text-sm font-sans normal-case leading-normal text-neutral-800 shadow-lg dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-200">
          <div className="flex items-baseline justify-between gap-2">
            <span className="font-serif text-base font-semibold">{lemma}</span>
            {pos && <span className="text-xs uppercase text-neutral-400">{pos}</span>}
          </div>

          {loading && <p className="mt-1 text-xs text-neutral-400">Loading&hellip;</p>}

          {!loading && data && (
            <>
              {data.gloss ? (
                <p className="mt-1 text-neutral-600 dark:text-neutral-300">{data.gloss}</p>
              ) : (
                <p className="mt-1 italic text-neutral-400">No LSJ entry found for this lemma.</p>
              )}

              <p className="mt-2 text-xs font-medium text-neutral-500">
                {data.occurrenceCount} occurrence{data.occurrenceCount === 1 ? "" : "s"} in corpus
              </p>

              {otherOccurrences.length > 0 && (
                <ul className="mt-1 space-y-0.5 border-t border-neutral-100 pt-1 dark:border-neutral-800">
                  {otherOccurrences.slice(0, 6).map((o, i) => (
                    <li key={i}>
                      <Link
                        href={`/read/${slugify(o.work)}/${o.book}?flashLemma=${encodeURIComponent(
                          lemma
                        )}&flashLine=${encodeURIComponent(`${o.work}:${o.line}`)}#card-${o.card}`}
                        className="text-xs text-blue-600 hover:underline dark:text-blue-400"
                      >
                        {o.work} {o.work === "Iliad" || o.work === "Odyssey" ? `${o.book}.` : ""}
                        {o.line}
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </>
          )}
        </span>
      )}
    </span>
  );
}
