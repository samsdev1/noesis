"use client";

import { useEffect } from "react";

/**
 * On mount, checks the URL for ?flashLemma=...&flashLine=WORK:LINE (set by
 * occurrence links in the LSJ popup). If present, scrolls that specific word
 * instance to the center of the viewport and briefly flashes it, then cleans
 * the query string so a refresh doesn't re-trigger it.
 */
export default function FlashHandler() {
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const lemma = params.get("flashLemma");
    const line = params.get("flashLine");
    if (!lemma || !line) return;

    const el = document.querySelector<HTMLElement>(
      `[data-lemma="${CSS.escape(lemma)}"][data-line="${CSS.escape(line)}"]`
    );
    if (!el) return;

    // Runs after a short delay so it overrides the browser's own native
    // scroll to the #card-N hash fragment (which otherwise wins if it
    // fires after this effect and lands on the top of a multi-line card
    // rather than the specific word).
    const timer = setTimeout(() => {
      el.scrollIntoView({ behavior: "smooth", block: "center" });
      el.classList.add("flash-word");
      const cleanup = () => el.classList.remove("flash-word");
      el.addEventListener("animationend", cleanup, { once: true });
    }, 400);

    const url = new URL(window.location.href);
    url.searchParams.delete("flashLemma");
    url.searchParams.delete("flashLine");
    window.history.replaceState({}, "", url);

    return () => clearTimeout(timer);
  }, []);

  return null;
}
