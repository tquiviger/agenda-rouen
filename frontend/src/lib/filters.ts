import type { Category, DateFilter, Event } from "./types";

export function filterEvents(
  events: Event[],
  dateFilter: DateFilter,
  categoryFilter: Category | null,
): Event[] {
  let filtered = events;

  if (categoryFilter) {
    filtered = filtered.filter((e) => e.category === categoryFilter);
  }

  if (dateFilter !== "all") {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    filtered = filtered.filter((e) => {
      const start = new Date(e.date_start + "T00:00:00");
      const end = e.date_end ? new Date(e.date_end + "T00:00:00") : start;

      switch (dateFilter) {
        case "today":
          return start <= today && end >= today;
        case "week": {
          const weekEnd = new Date(today);
          weekEnd.setDate(weekEnd.getDate() + 7);
          return start <= weekEnd && end >= today;
        }
        case "weekend": {
          const saturday = new Date(today);
          saturday.setDate(saturday.getDate() + ((6 - saturday.getDay() + 7) % 7 || 7));
          const sunday = new Date(saturday);
          sunday.setDate(sunday.getDate() + 1);
          return start <= sunday && end >= saturday;
        }
      }
    });
  }

  // Sort by date_start ascending (spread to avoid mutating the input array)
  return [...filtered].sort(
    (a, b) => new Date(a.date_start + "T00:00:00").getTime() - new Date(b.date_start + "T00:00:00").getTime(),
  );
}

export function formatDate(dateStr: string): string {
  const date = new Date(dateStr + "T00:00:00");
  return date.toLocaleDateString("fr-FR", {
    weekday: "short",
    day: "numeric",
    month: "long",
  });
}

export function formatDateRange(start: string, end: string | null): string {
  if (!end || end === start) {
    return formatDate(start);
  }
  return `${formatDate(start)} → ${formatDate(end)}`;
}
