import type { Event } from "./types";

const CDN_BASE_URL = process.env.NEXT_PUBLIC_CDN_URL ?? "";
const API_PREFIX = "api/v1";

/**
 * Fetch all events from the CloudFront CDN.
 * Falls back to an empty array on failure.
 */
export async function fetchEvents(): Promise<Event[]> {
  if (!CDN_BASE_URL) {
    return [];
  }

  const res = await fetch(`${CDN_BASE_URL}/${API_PREFIX}/events.json`, {
    next: { revalidate: 3600 },
  });

  if (!res.ok) {
    console.error(`Failed to fetch events: ${res.status} ${res.statusText}`);
    return [];
  }

  return res.json();
}
