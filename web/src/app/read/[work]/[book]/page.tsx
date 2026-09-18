import Link from "next/link";
import { notFound } from "next/navigation";
import { loadWork, WORK_SLUGS, WorkSlug } from "@/lib/texts";
import { ReaderProvider } from "@/components/ReaderContext";
import CardRow from "@/components/CardRow";
import FlashHandler from "@/components/FlashHandler";

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

      <ReaderProvider>
        <FlashHandler />
        <div className="mt-8 space-y-10">
          {book.cards.map((card) => (
            <CardRow key={card.card} card={card} workTitle={work.title} />
          ))}
        </div>
      </ReaderProvider>
    </main>
  );
}
