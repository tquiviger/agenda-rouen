"use client";

import { formatDateRange } from "@/lib/filters";
import { CATEGORY_CONFIG, type Event } from "@/lib/types";

interface Props {
  event: Event;
  onClick: () => void;
}

export default function EventCard({ event, onClick }: Props) {
  const cat = CATEGORY_CONFIG[event.category];

  return (
    <button
      onClick={onClick}
      className="group flex flex-col overflow-hidden rounded-2xl bg-white shadow-sm border border-gray-100 transition-all hover:shadow-lg hover:-translate-y-1 active:scale-[0.98] text-left w-full"
    >
      {/* Image or colored header */}
      {event.image_url ? (
        <div className="relative h-36 sm:h-44 overflow-hidden">
          <img
            src={event.image_url}
            alt={event.title}
            className="h-full w-full object-cover transition-transform group-hover:scale-105"
          />
          <div className="absolute top-3 left-3">
            <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold ${cat.bg} ${cat.color} backdrop-blur-sm`}>
              {cat.emoji} {cat.label}
            </span>
          </div>
        </div>
      ) : (
        <div className={`relative h-24 sm:h-28 ${cat.bg} flex items-center justify-center`}>
          <span className="text-4xl sm:text-5xl opacity-30">{cat.emoji}</span>
          <div className="absolute top-3 left-3">
            <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold bg-white/80 ${cat.color}`}>
              {cat.emoji} {cat.label}
            </span>
          </div>
        </div>
      )}

      {/* Content */}
      <div className="flex flex-1 flex-col gap-1.5 p-3 sm:p-4">
        <h3 className="text-sm sm:text-base font-bold text-gray-900 line-clamp-2 leading-snug">
          {event.title}
        </h3>

        {/* Date */}
        <div className="flex items-center gap-1.5 text-xs sm:text-sm text-gray-500">
          <svg className="h-3.5 w-3.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <span>{formatDateRange(event.date_start, event.date_end)}</span>
          {event.time && (
            <span className="font-medium text-gray-700">{event.time}</span>
          )}
        </div>

        {/* Location */}
        {event.location && (
          <div className="flex items-center gap-1.5 text-xs sm:text-sm text-gray-500">
            <svg className="h-3.5 w-3.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span className="line-clamp-1">{event.location}</span>
          </div>
        )}

        {/* Description */}
        {event.description && (
          <p className="text-xs sm:text-sm text-gray-400 line-clamp-2 mt-auto">
            {event.description}
          </p>
        )}

        {/* Tags */}
        {event.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-1">
            {event.tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="rounded-md bg-gray-50 px-1.5 py-0.5 text-[10px] sm:text-xs text-gray-400 border border-gray-100"
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
