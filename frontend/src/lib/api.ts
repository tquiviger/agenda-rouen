import type { Event } from "./types";

const CDN_BASE_URL = process.env.NEXT_PUBLIC_CDN_URL ?? "";
const API_PREFIX = "api/v1";

/**
 * Fetch all events from the CloudFront CDN.
 * Returns [] silently when CDN_BASE_URL is not set (dev / sample-data mode).
 * Throws when the CDN is configured but unreachable or returns an error status.
 */
export async function fetchEvents(): Promise<Event[]> {
  if (!CDN_BASE_URL) {
    return [];
  }

  const res = await fetch(`${CDN_BASE_URL}/${API_PREFIX}/events.json`, {
    next: { revalidate: 3600 },
  });

  if (!res.ok) {
    throw new Error(`CDN error ${res.status}: ${res.statusText}`);
  }

  return res.json();
}
