"use client";

import { useState, useMemo } from "react";
import CategoryFilter from "@/components/CategoryFilter";
import CdnErrorBanner from "@/components/CdnErrorBanner";
import DateFilter from "@/components/DateFilter";
import EventCard from "@/components/EventCard";
import EventModal from "@/components/EventModal";
import Header from "@/components/Header";
import SearchBar from "@/components/SearchBar";
import { filterEvents, searchEvents, countByCategory } from "@/lib/filters";
import type { Category, DateFilter as DateFilterType, Event } from "@/lib/types";

interface EventListProps {
  events: Event[];
  cdnError?: boolean;
}

export default function EventList({ events, cdnError = false }: EventListProps) {
  const [dateFilter, setDateFilter] = useState<DateFilterType>("all");
  const [categoryFilter, setCategoryFilter] = useState<Category | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    const dated = filterEvents(events, dateFilter, categoryFilter);
    return searchEvents(dated, query);
  }, [events, dateFilter, categoryFilter, query]);

  const categoryCounts = useMemo(() => countByCategory(
    filterEvents(events, dateFilter, null)
  ), [events, dateFilter]);

  return (
    <>
      <main className="mx-auto max-w-6xl px-4 sm:px-6">
        {/* Header */}
        <div className="pt-8 pb-6">
          <Header eventCount={filtered.length} />
        </div>

        {/* CDN error banner */}
        {cdnError && (
          <div className="pb-4">
            <CdnErrorBanner />
          </div>
        )}

        {/* Filters */}
        <div
          className="sticky top-0 z-30 -mx-4 px-4 sm:-mx-6 sm:px-6 py-3 backdrop-blur-xl"
          style={{
            background: "var(--surface-glass)",
            borderBottom: "1px solid var(--border-subtle)",
          }}
        >
          <div className="space-y-3">
            <SearchBar value={query} onChange={setQuery} />
            <DateFilter selected={dateFilter} onSelect={setDateFilter} />
            <CategoryFilter
              selected={categoryFilter}
              onSelect={setCategoryFilter}
              counts={categoryCounts}
            />
          </div>
        </div>

        {/* Event grid — bento layout */}
        {filtered.length > 0 ? (
          <div className="grid gap-4 pt-6 pb-12 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((event, i) => (
              <EventCard
                key={event.id}
                event={event}
                index={i}
                onClick={() => setSelectedEvent(event)}
              />
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-24 text-center">
            <span className="text-6xl mb-4">🔍</span>
            <p className="text-xl font-semibold" style={{ color: "var(--muted-strong)" }}>
              Aucun événement trouvé
            </p>
            <p className="mt-1" style={{ color: "var(--muted)" }}>
              Essayez de changer les filtres
            </p>
          </div>
        )}
      </main>

      {/* Event detail modal */}
      <EventModal event={selectedEvent} onClose={() => setSelectedEvent(null)} />
    </>
  );
}
