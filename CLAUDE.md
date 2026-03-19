# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend (Python)

```bash
uv sync --all-extras          # Install all deps (including dev)
uv run pytest                 # Run all tests
uv run pytest tests/test_models.py::test_name -v  # Single test
uv run ruff check src/ tests/ # Lint
uv run ruff format src/ tests/# Format
uv run mypy src/              # Type check
uv run python scripts/test_scrape.py   # Live test scrapers against real sites
uv run python scripts/test_classify.py # Test scrape + Gemini classification
```

### Frontend (Next.js)

```bash
cd frontend
npm install          # Install deps
npm run dev          # Dev server on http://localhost:3000
npm run build        # Production build
```

## Architecture

**Pipeline**: EventBridge (cron) → Lambda → Scrape → Classify (Gemini API) → Publish JSON → S3 → CloudFront → PWA

This is a **fully static architecture** — no database, no API server. The Lambda scraper generates JSON files grouped by date and category, pushes them to S3, and CloudFront serves them to the frontend.

### Backend — Key modules

- **`src/agenda_rouen/scrapers/`** — One scraper per source site, all inherit `BaseScraper` (async, httpx-based). Each must implement `async scrape() -> list[RawEvent]`.
- **`src/agenda_rouen/scrapers/openagenda.py`** — Generic scraper for OpenAgenda v2 JSON API (no API key needed). Handles 3 agendas: Métropole (UID 11362982), Ville de Rouen (11174431), Bibliothèques (8049538). Cursor-based pagination via `after[]` params. Time-filtered via `timings[gte]`/`timings[lte]`.
- **`src/agenda_rouen/scrapers/jds.py`** — HTML scraper for jds.fr. Parses `ul.list-articles-v2 > li` cards with BeautifulSoup. Page-based pagination (`?&page=N`). Client-side date filtering with early pagination stop.
- **`src/agenda_rouen/scrapers/rouen_on_est.py`** — Google Calendar API scraper. Fetches 5 public calendars (Grands événements, Animations & Spectacles, Culture & Expos, Dates majeures, Sports & Compétitions). Requires `GOOGLE_CALENDAR_API_KEY`.
- **`src/agenda_rouen/classifier/llm.py`** — Classifies events via Gemini 2.5 Flash. Maps raw categories to our unified taxonomy using a static mapping with LLM fallback for unknown categories.
- **`src/agenda_rouen/storage/s3.py`** — Publishes classified events as static JSON files to S3 (`events.json`, `dates/{date}.json`, `categories/{cat}.json`).
- **`src/agenda_rouen/handler.py`** — Lambda entry point. Orchestrates: scrape all → classify → publish.
- **`src/agenda_rouen/models.py`** — `RawEvent` (pre-classification), `Event` (post-classification), `Category` enum (unified taxonomy).

### Frontend — `frontend/`

Next.js 16 + Tailwind CSS PWA. Consumes static JSON from S3/CloudFront (currently uses sample data in `src/lib/sample-events.ts`).

- **`src/app/page.tsx`** — Main page: filter state, grid layout, modal trigger.
- **`src/components/CategoryFilter.tsx`** — Horizontal-scroll category chips with emoji + color per category.
- **`src/components/DateFilter.tsx`** — Segmented control: Tout / Aujourd'hui / 7 jours / Week-end.
- **`src/components/EventCard.tsx`** — Card with image (or colored placeholder), category badge, date, location, description, tags.
- **`src/components/EventModal.tsx`** — Bottom sheet on mobile, centered modal on desktop. Shows full event details + link to source.
- **`src/lib/types.ts`** — `Event` interface, `Category` type, `CATEGORY_CONFIG` (label, color, bg, emoji per category).
- **`src/lib/filters.ts`** — Client-side date/category filtering and date formatting.

### Scraper sources

| Scraper | Site | Method | Status |
|---------|------|--------|--------|
| `openagenda_metropole` | OpenAgenda (Métropole Rouen) | JSON API v2 (UID 11362982) | Active |
| `openagenda_rouen` | OpenAgenda (Ville de Rouen) | JSON API v2 (UID 11174431) | Active |
| `openagenda_bibliotheques` | OpenAgenda (Bibliothèques) | JSON API v2 (UID 8049538) | Active |
| `jds` | jds.fr | HTML scraping (BeautifulSoup) | Active |
| `rouen_on_est` | rouenonest.fr | Google Calendar API (5 public calendars) | Active |
| `shotgun` | shotgun.live | Blocked by Vercel bot protection | Deferred |

### Event taxonomy

Categories defined in `Category` enum: `musique`, `spectacles`, `sport`, `expositions`, `cinéma`, `festival`, `conférences`, `ateliers`, `famille`, `gastronomie`, `vie-nocturne`, `autre`.

## Environment variables

| Variable | Used by | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | classifier | Google Gemini API key for classification |
| `GOOGLE_CALENDAR_API_KEY` | rouen_on_est scraper | Google Calendar API key |
| `EVENTS_BUCKET` | storage | S3 bucket name (default: `agenda-rouen-events`) |
| `AWS_DEFAULT_REGION` | storage | AWS region (default: `eu-west-3`) |

## Conventions

- All scrapers are **async** (httpx + BeautifulSoup/lxml).
- All scrapers fetch events on a **30-day rolling window** from today.
- Scraper tests use `httpx.MockTransport` to mock HTTP responses.
- Storage tests use **moto** for S3 mocking — no real AWS calls in tests.
- The LLM classifier uses **Gemini 2.5 Flash** (`google-genai` SDK) with `response_mime_type="application/json"`.
- Classifier uses a static category mapping with LLM fallback for unknown categories, and title-based classification for events without a raw category.
- Region: `eu-west-3` (Paris).
- Frontend uses sample data for now (`sample-events.ts`), to be replaced by CloudFront fetch.
