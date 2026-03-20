import EventList from "@/components/EventList";
import { fetchEvents } from "@/lib/api";
import type { Event } from "@/lib/types";
import { SAMPLE_EVENTS } from "@/lib/sample-events";

export default async function Home() {
  let events: Event[] = [];
  let cdnError = false;

  try {
    events = await fetchEvents();
  } catch (err) {
    console.error("[CDN] fetchEvents failed:", err);
    cdnError = true;
  }

  const data = events.length > 0 ? events : SAMPLE_EVENTS;

  return (
    <div className="min-h-screen bg-atmosphere">
      <EventList events={data} cdnError={cdnError} />
    </div>
  );
}
