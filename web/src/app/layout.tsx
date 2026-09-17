import type { Metadata } from "next";
import { Geist, Geist_Mono, Noto_Serif } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// Noto Serif has full polytonic Greek coverage (base Greek + Greek Extended
// blocks), which the default serif fallback renders inconsistently for
// precomposed accented vowels.
const notoSerif = Noto_Serif({
  variable: "--font-noto-serif",
  subsets: ["latin", "greek", "greek-ext"],
  weight: ["400", "600"],
});

export const metadata: Metadata = {
  title: "Noesis",
  description: "Canonical Greek texts, read Greek-and-English side by side.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} ${notoSerif.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
