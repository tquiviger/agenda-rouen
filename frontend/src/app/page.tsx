import EventList from "@/components/EventList";
import { fetchEvents } from "@/lib/api";
import { SAMPLE_EVENTS } from "@/lib/sample-events";

export default async function Home() {
  const events = await fetchEvents();
  const data = events.length > 0 ? events : SAMPLE_EVENTS;

  return (
    <div className="min-h-screen pb-12">
      {/* Gradient accent bar */}
      <div className="h-1.5 bg-gradient-to-r from-orange-400 via-cyan-400 to-orange-400" />

      <EventList events={data} />
    </div>
  );
}
