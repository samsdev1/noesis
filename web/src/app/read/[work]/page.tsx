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

      <ul className="mt-8 grid grid-cols-4 gap-3 sm:grid-cols-6">
        {work.books.map((b) => (
          <li key={b.book}>
            <Link
              href={`/read/${workParam}/${b.book}`}
              className="flex h-12 items-center justify-center rounded-md border border-neutral-200 text-sm font-medium text-neutral-800 hover:border-neutral-400 dark:border-neutral-800 dark:text-neutral-200 dark:hover:border-neutral-600"
            >
              {work.books.length > 1 ? `Bk ${b.book}` : "Read"}
            </Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
