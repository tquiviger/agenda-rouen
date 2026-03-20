"use client";

import { useEffect, useState } from "react";
import { useTheme } from "@/components/ThemeProvider";
import { formatDateRange, getTimeBadge } from "@/lib/filters";
import { CATEGORY_CONFIG, type Event } from "@/lib/types";

interface Props {
  event: Event | null;
  onClose: () => void;
}

export default function EventModal({ event, onClose }: Props) {
  const [imgError, setImgError] = useState(false);

  useEffect(() => {
    setImgError(false);
  }, [event]);

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [onClose]);

  useEffect(() => {
    if (event) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [event]);

  if (!event) return null;

  const { dark } = useTheme();
  const cat = CATEGORY_CONFIG[event.category];
  const isValidUrl = event.image_url && !event.image_url.endsWith("/main/");
  const hasImage = isValidUrl && !imgError;
  const timeBadge = getTimeBadge(event.date_start);

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 backdrop-blur-sm animate-backdrop"
        style={{ background: "rgba(0,0,0,0.5)" }}
        onClick={onClose}
      />

      {/* Modal */}
      <div
        className="relative z-10 w-full sm:max-w-lg max-h-[90vh] overflow-y-auto rounded-t-2xl sm:rounded-2xl shadow-2xl animate-slide-up"
        style={{ background: "var(--surface)" }}
      >
        {/* Image header */}
        {hasImage ? (
          <div className="relative h-48 sm:h-64 overflow-hidden rounded-t-2xl">
            <img
              src={event.image_url}
              alt=""
              onError={() => setImgError(true)}
              className="h-full w-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
            <h2 className="absolute bottom-4 left-5 right-12 font-display text-2xl sm:text-3xl text-white leading-tight drop-shadow-lg">
              {event.title}
            </h2>
          </div>
        ) : (
          <div className={`relative h-36 sm:h-44 bg-gradient-to-br ${cat.gradient} rounded-t-2xl flex items-center justify-center`}>
            <span className="text-6xl sm:text-8xl opacity-20">{cat.emoji}</span>
            <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent" />
            <h2 className="absolute bottom-4 left-5 right-12 font-display text-2xl sm:text-3xl text-white leading-tight drop-shadow-lg">
              {event.title}
            </h2>
          </div>
        )}

        {/* Drag handle (mobile only) */}
        <div className="flex justify-center pt-2 sm:hidden">
          <div className="h-1 w-10 rounded-full" style={{ background: "var(--border)" }} />
        </div>

        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-3 right-3 rounded-full p-2 shadow-md transition-colors backdrop-blur-md"
          style={{ background: "rgba(255,255,255,0.9)" }}
        >
          <svg className="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Content */}
        <div className="p-5 sm:p-6 space-y-3">
          {/* Badges row */}
          <div className="flex items-center gap-2 flex-wrap">
            <span
              className="inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs sm:text-sm font-semibold"
              style={{ backgroundColor: dark ? cat.darkBg : cat.bg, color: dark ? cat.darkColor : cat.color }}
            >
              {cat.emoji} {cat.label}
            </span>
            {timeBadge && (
              <span className="inline-flex items-center rounded-full px-3 py-1 text-xs font-bold text-amber-600 dark:text-amber-400" style={{ background: "var(--accent-soft)" }}>
                {timeBadge}
              </span>
            )}
          </div>

          {/* Date & time */}
          <div className="flex items-center gap-3 text-sm" style={{ color: "var(--muted-strong)" }}>
            <svg className="h-5 w-5 shrink-0" style={{ color: "var(--accent)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <div>
              <div className="font-medium" style={{ color: "var(--foreground)" }}>{formatDateRange(event.date_start, event.date_end)}</div>
              {event.time && <div className="text-xs" style={{ color: "var(--muted)" }}>{event.time}</div>}
            </div>
          </div>

          {/* Location */}
          {event.location && (
            <div className="flex items-start gap-3 text-sm" style={{ color: "var(--muted-strong)" }}>
              <svg className="h-5 w-5 mt-0.5 shrink-0 text-cyan-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <div>
                <div className="font-medium" style={{ color: "var(--foreground)" }}>{event.location}</div>
                {event.address && event.address !== event.location && (
                  <div className="text-xs" style={{ color: "var(--muted)" }}>{event.address}</div>
                )}
              </div>
            </div>
          )}

          {/* Description */}
          {event.description && (
            <p className="text-sm leading-relaxed" style={{ color: "var(--muted-strong)" }}>{event.description}</p>
          )}

          {/* Tags */}
          {event.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {event.tags.map((tag) => (
                <span
                  key={tag}
                  className="rounded-lg px-2.5 py-1 text-xs"
                  style={{ background: "var(--border-subtle)", color: "var(--muted)" }}
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}

          {/* Source link */}
          {event.urls.length > 0 && (
            <div className="pt-3" style={{ borderTop: "1px solid var(--border)" }}>
              <a
                href={event.urls[0]}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 rounded-xl px-5 py-3 text-sm font-semibold text-white hover:opacity-90 active:opacity-80 transition-opacity w-full justify-center"
                style={{ background: "var(--accent)" }}
              >
                Voir sur le site source
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
