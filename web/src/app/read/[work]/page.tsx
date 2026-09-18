import Link from "next/link";
import { notFound } from "next/navigation";
import { loadWork, WORK_SLUGS, WorkSlug } from "@/lib/texts";

export function generateStaticParams() {
  return WORK_SLUGS.map((work) => ({ work }));
}

export default async function WorkPage({ params }: { params: Promise<{ work: string }> }) {
  const { work: workParam } = await params;
  if (!WORK_SLUGS.includes(workParam as WorkSlug)) notFound();
  const work = loadWork(workParam as WorkSlug);

  return (
    <main className="mx-auto max-w-3xl px-6 py-16">
      <Link href="/" className="text-sm text-neutral-500 hover:underline">
        &larr; All texts
      </Link>
      <h1 className="mt-4 text-3xl font-semibold tracking-tight text-neutral-900 dark:text-neutral-100">
        {work.title}
      </h1>
      <p className="text-neutral-600 dark:text-neutral-400">{work.author}</p>

      <ul className="mt-8 grid grid-cols-3 gap-4 sm:grid-cols-4 md:grid-cols-6">
        {work.books.map((b) => (
          <li key={b.book}>
            <Link
              href={`/read/${workParam}/${b.book}`}
              className="flex h-24 items-center justify-center rounded-xl border border-neutral-700 bg-neutral-800/40 text-lg font-medium text-neutral-100 transition-colors hover:border-amber-400 hover:bg-neutral-800 hover:text-amber-200"
            >
              {work.books.length > 1 ? `Bk ${b.book}` : "Read"}
            </Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
