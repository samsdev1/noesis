"use client";

import WordSpan from "./WordSpan";
import type { Card } from "@/lib/texts";

function highlight(hlKey: string, on: boolean) {
  document
    .querySelectorAll(`[data-hl-key="${CSS.escape(hlKey)}"]`)
    .forEach((el) => el.classList.toggle("word-highlight", on));
}

export default function CardRow({ card, workTitle }: { card: Card; workTitle: string }) {
  return (
    <div
      id={`card-${card.card}`}
      className="grid grid-cols-1 gap-4 border-b border-neutral-100 pb-8 last:border-0 md:grid-cols-2 md:gap-8 dark:border-neutral-900"
    >
      <div
        className="text-[1.15rem] leading-8 text-neutral-900 dark:text-neutral-100"
        style={{ fontFamily: "var(--font-noto-serif)" }}
      >
        {card.greek_lines.map((line) => (
          <div key={line.n} className="flex gap-3">
            <span className="w-8 shrink-0 select-none text-right text-xs text-neutral-400 pt-1.5">
              {line.n}
            </span>
            <span>
              {line.segments
                ? line.segments.map((seg, i) =>
                    seg.type === "word" ? (
                      <WordSpan
                        key={i}
                        text={seg.text}
                        lemma={seg.lemma}
                        pos={seg.pos}
                        card={card.card}
                        currentWork={workTitle}
                        currentLine={line.n}
                        wordId={`${workTitle}-${card.card}-${line.n}-${i}`}
                      />
                    ) : (
                      <span key={i}>{seg.text}</span>
                    )
                  )
                : line.text}
            </span>
          </div>
        ))}
      </div>
      <div className="text-[1.05rem] leading-8 text-neutral-700 dark:text-neutral-300">
        {card.english_segments ? (
          card.english_segments.map((seg, i) => {
            const alignable = seg.type === "word" && !!seg.alignedLemma;
            const hlKey = alignable ? `${card.card}:${seg.alignedLemma}` : "";
            return (
              <span
                key={i}
                data-hl-key={alignable ? hlKey : undefined}
                className={`rounded transition-colors ${alignable ? "cursor-pointer hover:bg-neutral-800" : ""}`}
                onMouseEnter={alignable ? () => highlight(hlKey, true) : undefined}
                onMouseLeave={alignable ? () => highlight(hlKey, false) : undefined}
              >
                {seg.text}
              </span>
            );
          })
        ) : card.english ? (
          card.english
        ) : (
          <span className="italic text-neutral-400">[translation gap]</span>
        )}
      </div>
    </div>
  );
}
