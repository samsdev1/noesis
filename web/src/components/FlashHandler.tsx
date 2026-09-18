"use client";

import { useEffect } from "react";
import { useSearchParams, usePathname, useRouter } from "next/navigation";

/**
 * Checks the URL for ?flashLemma=...&flashLine=WORK:LINE (set by occurrence
 * links in the LSJ popup). When present, scrolls that specific word instance
 * to the center of the viewport and briefly flashes it, then cleans the
 * query string.
 *
 * Occurrence links carry no #card-N hash fragment -- an earlier version did,
 * and the browser's/Next's own native hash-scroll (jumps to the top of the
 * card, not the specific word) fired after this effect and silently
 * overrode it.
 *
 * Uses useSearchParams()/usePathname() (not a one-time window.location.search
 * read) specifically because /read/[work]/[book] is the *same* page
 * component across navigations between books -- React reconciles it as an
 * update rather than a remount, so a plain useState lazy initializer or a
 * ref-based "have I run yet" guard would only ever fire once for the
 * component's whole lifetime and silently do nothing on every subsequent
 * occurrence-link click. These hooks are the part of that same persistent
 * component instance that Next actually updates on navigation, so an effect
 * keyed on them re-fires correctly every time.
 */
export default function FlashHandler() {
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();

  const lemma = searchParams.get("flashLemma");
  const line = searchParams.get("flashLine");

  useEffect(() => {
    if (!lemma || !line) return;

    router.replace(pathname, { scroll: false });

    const timer = setTimeout(() => {
      const el = document.querySelector<HTMLElement>(
        `[data-lemma="${CSS.escape(lemma)}"][data-line="${CSS.escape(line)}"]`
      );
      if (!el) return;
      el.scrollIntoView({ behavior: "smooth", block: "center" });
      el.classList.add("flash-word");
      const cleanup = () => el.classList.remove("flash-word");
      el.addEventListener("animationend", cleanup, { once: true });
    }, 80);

    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lemma, line, pathname]);

  return null;
}
