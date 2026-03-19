"use client";

import { useState } from "react";
import { formatDateRange, getTimeBadge } from "@/lib/filters";
import { CATEGORY_CONFIG, type Event } from "@/lib/types";

interface Props {
  event: Event;
  featured?: boolean;
  index: number;
  onClick: () => void;
}

export default function EventCard({ event, featured = false, index, onClick }: Props) {
  const cat = CATEGORY_CONFIG[event.category];
  const [imgError, setImgError] = useState(false);
  const isValidUrl = event.image_url && !event.image_url.endsWith("/main/");
  const hasImage = isValidUrl && !imgError;
  const timeBadge = getTimeBadge(event.date_start);

  const delay = Math.min(index * 60, 600);
  const isFeatured = featured && hasImage;

  return (
    <button
      onClick={onClick}
      className={`animate-card group relative flex flex-col overflow-hidden rounded-2xl text-left w-full transition-all duration-300 hover:-translate-y-1 active:scale-[0.98] ${
        isFeatured ? "sm:col-span-2 sm:flex-row" : ""
      }`}
      style={{
        animationDelay: `${delay}ms`,
        background: "var(--surface)",
        border: "1px solid var(--border)",
      }}
    >
      {/* Image / Placeholder */}
      <div
        className={`relative overflow-hidden shrink-0 ${
          isFeatured
            ? "h-48 sm:h-auto sm:w-1/2"
            : "h-44"
        }`}
      >
        {hasImage ? (
          <>
            <img
              src={event.image_url}
              alt=""
              onError={() => setImgError(true)}
              className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
            {/* Gradient overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
          </>
        ) : (
          <div className={`h-full w-full bg-gradient-to-br ${cat.gradient} flex items-center justify-center`}>
            <span className="text-7xl opacity-20 transition-transform duration-500 group-hover:scale-110 group-hover:rotate-6">{cat.emoji}</span>
            <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
          </div>
        )}

        {/* Title overlay on image */}
        <div className="absolute bottom-0 left-0 right-0 p-3.5 sm:p-4">
          <h3 className={`font-display text-white leading-snug drop-shadow-lg ${
            isFeatured ? "text-xl sm:text-2xl" : "text-base sm:text-lg"
          } line-clamp-2`}>
            {event.title}
          </h3>
        </div>

        {/* Top badges row */}
        <div className="absolute top-3 left-3 right-3 flex items-start justify-between gap-2">
          {/* Category badge */}
          <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-[11px] font-semibold backdrop-blur-md ${cat.bg} ${cat.color} dark:${cat.darkBg} dark:${cat.darkColor}`}>
            {cat.emoji} {cat.label}
          </span>

          {/* Time proximity badge */}
          {timeBadge && (
            <span className="inline-flex items-center rounded-full bg-white/90 dark:bg-black/70 px-2.5 py-1 text-[11px] font-bold text-amber-600 dark:text-amber-400 backdrop-blur-md shadow-sm">
              {timeBadge}
            </span>
          )}
        </div>
      </div>

      {/* Content */}
      <div className={`flex flex-1 flex-col gap-1.5 p-3.5 sm:p-4 ${isFeatured ? "sm:justify-center" : ""}`}>
        {/* Date */}
        <div className="flex items-center gap-1.5 text-xs" style={{ color: "var(--muted-strong)" }}>
          <svg className="h-3.5 w-3.5 shrink-0" style={{ color: "var(--accent)" }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <span>{formatDateRange(event.date_start, event.date_end)}</span>
          {event.time && (
            <span className="font-semibold" style={{ color: "var(--foreground)" }}>{event.time}</span>
          )}
        </div>

        {/* Location */}
        {event.location && (
          <div className="flex items-center gap-1.5 text-xs" style={{ color: "var(--muted)" }}>
            <svg className="h-3.5 w-3.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span className="line-clamp-1">{event.location}</span>
          </div>
        )}

        {/* Description */}
        {event.description && (
          <p className="text-xs line-clamp-2 mt-0.5" style={{ color: "var(--muted)" }}>
            {event.description}
          </p>
        )}

        {/* Tags */}
        {event.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-1">
            {event.tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="rounded-md px-1.5 py-0.5 text-[10px]"
                style={{
                  background: "var(--border-subtle)",
                  color: "var(--muted)",
                }}
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </button>
  );
}
