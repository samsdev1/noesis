"use client";

import { createContext, useContext, useEffect, useState } from "react";

type ReaderContextValue = {
  activeWordId: string | null;
  openWord: (id: string) => void;
  closeWord: () => void;
};

const ReaderContext = createContext<ReaderContextValue | null>(null);

export function ReaderProvider({ children }: { children: React.ReactNode }) {
  const [activeWordId, setActiveWordId] = useState<string | null>(null);

  useEffect(() => {
    function handleDocClick(e: MouseEvent) {
      const target = e.target as HTMLElement;
      if (!target.closest("[data-word-popup]")) {
        setActiveWordId(null);
      }
    }
    document.addEventListener("mousedown", handleDocClick);
    return () => document.removeEventListener("mousedown", handleDocClick);
  }, []);

  return (
    <ReaderContext.Provider
      value={{
        activeWordId,
        openWord: (id) => setActiveWordId((cur) => (cur === id ? null : id)),
        closeWord: () => setActiveWordId(null),
      }}
    >
      {children}
    </ReaderContext.Provider>
  );
}

export function useReader() {
  const ctx = useContext(ReaderContext);
  if (!ctx) throw new Error("useReader must be used within ReaderProvider");
  return ctx;
}
