import Link from "next/link";
import { listWorks } from "@/lib/texts";

export default function Home() {
  const works = listWorks();

  return (
    <main className="mx-auto max-w-3xl px-6 py-16">
      <h1 className="text-3xl font-semibold tracking-tight text-neutral-900 dark:text-neutral-100">
        Noesis
      </h1>
      <p className="mt-2 text-neutral-600 dark:text-neutral-400">
        Canonical Greek texts, read Greek-and-English side by side.
      </p>

      <ul className="mt-10 divide-y divide-neutral-200 dark:divide-neutral-800">
        {works.map((w) => (
          <li key={w.slug} className="py-4">
            <Link
              href={`/read/${w.slug}`}
              className="text-lg font-medium text-neutral-900 hover:underline dark:text-neutral-100"
            >
              {w.title}
            </Link>
            <p className="text-sm text-neutral-500 dark:text-neutral-400">
              {w.author} &middot; {w.bookCount} {w.bookCount === 1 ? "book" : "books"}
            </p>
          </li>
        ))}
      </ul>
    </main>
  );
}
