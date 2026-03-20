"use client";

import { useTheme } from "@/components/ThemeProvider";

export default function Header({ eventCount }: { eventCount: number }) {
  const { dark, toggle } = useTheme();

  return (
    <header className="relative flex flex-col items-center py-8 sm:py-12">

      {/* Theme toggle — absolute top-right */}
      <button
        onClick={toggle}
        aria-label="Changer de thème"
        className="absolute right-0 top-0 rounded-full p-2.5 transition-colors"
        style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
      >
        {dark ? (
          <svg className="h-5 w-5" style={{ color: "var(--accent)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        ) : (
          <svg className="h-5 w-5" style={{ color: "var(--muted-strong)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
          </svg>
        )}
      </button>

      {/* Wordmark */}
      <div className="flex flex-col items-center gap-1 select-none">
        {/* "AGENDA" — small tracked label in accent */}
        <span
          className="font-sans text-xs sm:text-sm font-semibold tracking-[0.35em] uppercase"
          style={{ color: "var(--accent)" }}
        >
          Agenda
        </span>

        {/* Decorative rule */}
        <div className="flex items-center gap-3 w-full">
          <span className="flex-1 h-px" style={{ background: "var(--border)" }} />
          <svg width="10" height="10" viewBox="0 0 10 10" fill="none" aria-hidden>
            <rect x="5" y="0.5" width="6.36" height="6.36" transform="rotate(45 5 5)" fill="var(--accent)" opacity="0.7" />
          </svg>
          <span className="flex-1 h-px" style={{ background: "var(--border)" }} />
        </div>

        {/* "ROUEN" — large serif wordmark */}
        <h1
          className="font-display leading-none tracking-tight text-6xl sm:text-8xl"
          style={{ color: "var(--foreground)" }}
        >
          Rouen
        </h1>

        {/* Event count subtitle */}
        <p
          className="mt-2 font-sans text-xs sm:text-sm tracking-[0.15em] uppercase"
          style={{ color: "var(--muted)" }}
        >
          {eventCount} événement{eventCount !== 1 ? "s" : ""} à découvrir
        </p>
      </div>
    </header>
  );
}
