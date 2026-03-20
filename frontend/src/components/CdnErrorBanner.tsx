"use client";

import { useState } from "react";

export default function CdnErrorBanner() {
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return null;

  return (
    <div
      role="alert"
      className="flex items-start gap-3 rounded-xl px-4 py-3 text-sm"
      style={{
        background: "var(--accent-soft)",
        border: "1px solid color-mix(in srgb, var(--accent) 30%, transparent)",
      }}
    >
      {/* Icon */}
      <svg
        className="mt-0.5 h-4 w-4 shrink-0"
        style={{ color: "var(--accent)" }}
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={2}
        aria-hidden
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
        />
      </svg>

      {/* Message */}
      <p style={{ color: "var(--accent)" }}>
        <span className="font-semibold">Données non disponibles.</span>{" "}
        <span style={{ color: "color-mix(in srgb, var(--accent) 80%, var(--foreground))" }}>
          Impossible de contacter le serveur. Les événements affichés sont des données d&apos;exemple.
        </span>
      </p>

      {/* Dismiss */}
      <button
        onClick={() => setDismissed(true)}
        aria-label="Fermer"
        className="ml-auto shrink-0 rounded p-0.5 transition-opacity hover:opacity-60"
        style={{ color: "var(--accent)" }}
      >
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden>
          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}
