import EventList from "@/components/EventList";
import { fetchEvents } from "@/lib/api";
import { SAMPLE_EVENTS } from "@/lib/sample-events";

export default async function Home() {
  const events = await fetchEvents();
  const data = events.length > 0 ? events : SAMPLE_EVENTS;

  return (
    <div className="min-h-screen bg-atmosphere">
      <EventList events={data} />
    </div>
  );
}
