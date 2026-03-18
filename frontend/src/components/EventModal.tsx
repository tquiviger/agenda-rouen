"use client";

import { useEffect } from "react";
import { formatDateRange } from "@/lib/filters";
import { CATEGORY_CONFIG, type Event } from "@/lib/types";

interface Props {
  event: Event | null;
  onClose: () => void;
}

export default function EventModal({ event, onClose }: Props) {
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

  const cat = CATEGORY_CONFIG[event.category];

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal — bottom sheet on mobile, centered card on desktop */}
      <div className="relative z-10 w-full sm:max-w-lg max-h-[85vh] overflow-y-auto bg-white rounded-t-2xl sm:rounded-2xl shadow-2xl animate-slide-up">
        {/* Image header */}
        {event.image_url ? (
          <div className="relative h-44 sm:h-56 overflow-hidden rounded-t-2xl">
            <img
              src={event.image_url}
              alt={event.title}
              className="h-full w-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent" />
          </div>
        ) : (
          <div className={`relative h-24 sm:h-32 ${cat.bg} rounded-t-2xl flex items-center justify-center`}>
            <span className="text-5xl sm:text-7xl opacity-20">{cat.emoji}</span>
          </div>
        )}

        {/* Drag handle (mobile only) */}
        <div className="flex justify-center pt-2 sm:hidden">
          <div className="h-1 w-10 rounded-full bg-gray-300" />
        </div>

        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-3 right-3 rounded-full bg-white/90 p-2 shadow-md hover:bg-white transition-colors"
        >
          <svg className="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Content */}
        <div className="p-5 sm:p-6 space-y-3">
          {/* Category badge */}
          <span className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs sm:text-sm font-semibold ${cat.bg} ${cat.color}`}>
            {cat.emoji} {cat.label}
          </span>

          {/* Title */}
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 leading-tight">
            {event.title}
          </h2>

          {/* Date & time */}
          <div className="flex items-center gap-3 text-sm text-gray-600">
            <svg className="h-5 w-5 text-orange-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <div>
              <div className="font-medium">{formatDateRange(event.date_start, event.date_end)}</div>
              {event.time && <div className="text-xs text-gray-400">{event.time}</div>}
            </div>
          </div>

          {/* Location */}
          {event.location && (
            <div className="flex items-start gap-3 text-sm text-gray-600">
              <svg className="h-5 w-5 mt-0.5 text-cyan-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <div>
                <div className="font-medium">{event.location}</div>
                {event.address && event.address !== event.location && (
                  <div className="text-xs text-gray-400">{event.address}</div>
                )}
              </div>
            </div>
          )}

          {/* Description */}
          {event.description && (
            <p className="text-sm text-gray-600 leading-relaxed">{event.description}</p>
          )}

          {/* Tags */}
          {event.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {event.tags.map((tag) => (
                <span
                  key={tag}
                  className="rounded-lg bg-gray-100 px-2.5 py-1 text-xs text-gray-500"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}

          {/* Source link */}
          {event.urls.length > 0 && (
            <div className="pt-3 border-t border-gray-100">
              <a
                href={event.urls[0]}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 rounded-xl bg-orange-500 px-5 py-3 text-sm font-semibold text-white hover:bg-orange-600 active:bg-orange-700 transition-colors w-full justify-center"
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
