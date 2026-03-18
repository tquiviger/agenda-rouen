"use client";

import { useState } from "react";
import CategoryFilter from "@/components/CategoryFilter";
import DateFilter from "@/components/DateFilter";
import EventCard from "@/components/EventCard";
import EventModal from "@/components/EventModal";
import Header from "@/components/Header";
import { filterEvents } from "@/lib/filters";
import { SAMPLE_EVENTS } from "@/lib/sample-events";
import type { Category, DateFilter as DateFilterType, Event } from "@/lib/types";

export default function Home() {
  const [dateFilter, setDateFilter] = useState<DateFilterType>("all");
  const [categoryFilter, setCategoryFilter] = useState<Category | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);

  const events = filterEvents(SAMPLE_EVENTS, dateFilter, categoryFilter);

  return (
    <div className="min-h-screen pb-12">
      {/* Gradient accent bar */}
      <div className="h-1.5 bg-gradient-to-r from-orange-400 via-cyan-400 to-orange-400" />

      <main className="mx-auto max-w-6xl px-4 sm:px-6">
        {/* Header */}
        <div className="pt-10 pb-8">
          <Header eventCount={events.length} />
        </div>

        {/* Filters */}
        <div className="sticky top-0 z-30 -mx-4 px-4 sm:-mx-6 sm:px-6 py-4 bg-stone-50/80 backdrop-blur-lg border-b border-gray-100">
          <div className="space-y-3">
            <DateFilter selected={dateFilter} onSelect={setDateFilter} />
            <CategoryFilter selected={categoryFilter} onSelect={setCategoryFilter} />
          </div>
        </div>

        {/* Event grid */}
        {events.length > 0 ? (
          <div className="grid gap-5 pt-6 sm:grid-cols-2 lg:grid-cols-3">
            {events.map((event) => (
              <EventCard
                key={event.id}
                event={event}
                onClick={() => setSelectedEvent(event)}
              />
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-24 text-center">
            <span className="text-6xl mb-4">🔍</span>
            <p className="text-xl font-semibold text-gray-500">
              Aucun événement trouvé
            </p>
            <p className="text-gray-400 mt-1">
              Essayez de changer les filtres
            </p>
          </div>
        )}
      </main>

      {/* Event detail modal */}
      <EventModal event={selectedEvent} onClose={() => setSelectedEvent(null)} />
    </div>
  );
}
