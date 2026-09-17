import Link from "next/link";
import { notFound } from "next/navigation";
import { loadWork, WORK_SLUGS, WorkSlug } from "@/lib/texts";
import WordSpan from "@/components/WordSpan";

export function generateStaticParams() {
  return WORK_SLUGS.flatMap((work) => {
    const data = loadWork(work);
    return data.books.map((b) => ({ work, book: b.book }));
  });
}

export default async function ReaderPage({
  params,
}: {
  params: Promise<{ work: string; book: string }>;
}) {
  const { work: workParam, book: bookParam } = await params;
  if (!WORK_SLUGS.includes(workParam as WorkSlug)) notFound();
  const work = loadWork(workParam as WorkSlug);
  const book = work.books.find((b) => b.book === bookParam);
  if (!book) notFound();

  const bookIndex = work.books.findIndex((b) => b.book === bookParam);
  const prevBook = bookIndex > 0 ? work.books[bookIndex - 1] : null;
  const nextBook = bookIndex < work.books.length - 1 ? work.books[bookIndex + 1] : null;

  return (
    <main className="mx-auto max-w-5xl px-6 py-12">
      <div className="flex items-center justify-between">
        <Link href={`/read/${workParam}`} className="text-sm text-neutral-500 hover:underline">
          &larr; {work.title}
        </Link>
        <div className="flex gap-4 text-sm">
          {prevBook && (
            <Link href={`/read/${workParam}/${prevBook.book}`} className="text-neutral-500 hover:underline">
              &larr; Book {prevBook.book}
            </Link>
          )}
          {nextBook && (
            <Link href={`/read/${workParam}/${nextBook.book}`} className="text-neutral-500 hover:underline">
              Book {nextBook.book} &rarr;
            </Link>
          )}
        </div>
      </div>

      <h1 className="mt-4 text-2xl font-semibold tracking-tight text-neutral-900 dark:text-neutral-100">
        {work.title}
        {work.books.length > 1 && <span className="text-neutral-500"> &middot; Book {book.book}</span>}
      </h1>

      <div className="mt-8 space-y-10">
        {book.cards.map((card) => (
          <div
            key={card.card}
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
                              currentWork={work.title}
                              currentLine={line.n}
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
              {card.english || (
                <span className="italic text-neutral-400">[translation gap]</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}
