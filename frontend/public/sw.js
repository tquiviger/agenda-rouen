/**
 * Agenda Rouen — Service Worker
 *
 * Strategies:
 *  - Static assets (_next/static, fonts, images) → cache-first
 *  - Events JSON from CloudFront                 → stale-while-revalidate
 *  - Navigation requests                         → network-first, fallback to cache
 */

const CACHE = "agenda-rouen-v1";

// Shell resources to precache on install
const PRECACHE = ["/", "/manifest.json"];

// ── Install ──────────────────────────────────────────────────────────────────

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(PRECACHE))
  );
  self.skipWaiting();
});

// ── Activate ─────────────────────────────────────────────────────────────────

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
      )
  );
  self.clients.claim();
});

// ── Fetch ─────────────────────────────────────────────────────────────────────

self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Only handle same-origin + CloudFront requests
  if (url.origin !== self.location.origin && !url.hostname.includes("cloudfront.net")) {
    return;
  }

  // Events JSON from CloudFront → stale-while-revalidate
  if (url.hostname.includes("cloudfront.net") || url.pathname.endsWith(".json")) {
    event.respondWith(staleWhileRevalidate(request));
    return;
  }

  // Next.js static assets (_next/static) → cache-first
  if (url.pathname.startsWith("/_next/static/")) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // Static files (icons, fonts, images) → cache-first
  if (
    request.destination === "font" ||
    request.destination === "image" ||
    url.pathname.startsWith("/icon") ||
    url.pathname.startsWith("/apple-icon")
  ) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // Navigation → network-first, serve cached page if offline
  if (request.mode === "navigate") {
    event.respondWith(networkFirst(request));
    return;
  }
});

// ── Cache strategies ──────────────────────────────────────────────────────────

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;

  const response = await fetch(request);
  if (response.ok) {
    const cache = await caches.open(CACHE);
    cache.put(request, response.clone());
  }
  return response;
}

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    return cached ?? caches.match("/");
  }
}

async function staleWhileRevalidate(request) {
  const cache = await caches.open(CACHE);
  const cached = await cache.match(request);

  const fetchPromise = fetch(request).then((response) => {
    if (response.ok) cache.put(request, response.clone());
    return response;
  });

  return cached ?? fetchPromise;
}
