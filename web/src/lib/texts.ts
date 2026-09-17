import fs from "fs";
import path from "path";

export type Line = { n: string; text: string };
export type Card = { card: string; greek_lines: Line[]; english: string };
export type Book = { book: string; cards: Card[] };
export type Work = { title: string; author: string; urn: string; books: Book[] };

const CONTENT_DIR = path.join(process.cwd(), "src", "content");

export const WORK_SLUGS = ["iliad", "odyssey", "theogony", "works-and-days"] as const;
export type WorkSlug = (typeof WORK_SLUGS)[number];

export function loadWork(slug: WorkSlug): Work {
  const filePath = path.join(CONTENT_DIR, `${slug}.json`);
  const raw = fs.readFileSync(filePath, "utf-8");
  return JSON.parse(raw) as Work;
}

export function listWorks(): { slug: WorkSlug; title: string; author: string; bookCount: number }[] {
  return WORK_SLUGS.map((slug) => {
    const work = loadWork(slug);
    return { slug, title: work.title, author: work.author, bookCount: work.books.length };
  });
}
