# Agenda Rouen

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16-000000?logo=next.js&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4-06B6D4?logo=tailwindcss&logoColor=white)
![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-FF9900?logo=awslambda&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-4285F4?logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

> Agrégateur d'événements culturels et sportifs à Rouen et ses environs.
> Scrape, classifie via LLM, et publie un agenda statique consultable en PWA.

---

## Table des matières

- [Apercu](#apercu)
- [Architecture](#architecture)
- [Sources de données](#sources-de-données)
- [Stack technique](#stack-technique)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Développement](#développement)
- [Pipeline de données](#pipeline-de-données)
- [Frontend (PWA)](#frontend-pwa)
- [Déploiement](#déploiement)
- [Structure du projet](#structure-du-projet)
- [API JSON publiée](#api-json-publiée)
- [Taxonomie des événements](#taxonomie-des-événements)

---

## Apercu

Agenda Rouen agrège les événements de **5 sources locales**, les **classifie et déduplique automatiquement** via Gemini 2.5 Flash, puis publie des **fichiers JSON statiques** sur S3/CloudFront. Une **PWA Next.js** consomme ces fichiers pour afficher un agenda filtrable par date et catégorie.

**Objectif** : stack la moins chère possible, idéalement dans le free tier AWS.

---

## Architecture

```
                    ┌─────────────────────────────────────────────┐
                    │            EventBridge (cron)                │
                    └──────────────────┬──────────────────────────┘
                                       │ trigger quotidien
                                       ▼
                    ┌─────────────────────────────────────────────┐
                    │              AWS Lambda (Python)             │
                    │                                             │
                    │  ┌───────────┐  ┌──────────┐  ┌─────────┐  │
                    │  │ Scrapers  │→ │ Classify  │→ │ Publish │  │
                    │  │ (5 src)   │  │ (Gemini)  │  │ (S3)    │  │
                    │  └───────────┘  └──────────┘  └─────────┘  │
                    └─────────────────────────────────────────────┘
                                       │
                                       ▼
                    ┌─────────────────────────────────────────────┐
                    │         S3 + CloudFront (JSON statique)     │
                    │                                             │
                    │  /api/v1/events.json                        │
                    │  /api/v1/dates/{date}.json                  │
                    │  /api/v1/categories/{cat}.json               │
                    └──────────────────┬──────────────────────────┘
                                       │
                                       ▼
                    ┌─────────────────────────────────────────────┐
                    │          PWA Next.js (Vercel)                │
                    │          Filtres date + catégorie            │
                    └─────────────────────────────────────────────┘
```

**Pas de base de données, pas de serveur API** — uniquement des fichiers JSON servis par un CDN.

---

## Sources de données

| Source | Méthode | Détails |
|--------|---------|---------|
| **Métropole Rouen Normandie** | OpenAgenda API v2 | UID `11362982` — ~270 événements/mois |
| **Ville de Rouen** | OpenAgenda API v2 | UID `11174431` — ~15 événements/mois |
| **Bibliothèques de Rouen** | OpenAgenda API v2 | UID `8049538` — ~130 événements/mois |
| **JDS (Journal des Spectacles)** | HTML scraping | Scrapling + pagination `?&page=N` |
| **Rouen On Est** | Google Calendar API | 5 calendriers publics (spectacles, culture, sport, dates majeures, grands événements) |
| **Shotgun** | *Reporté* | Bloqué par Vercel bot protection |

Tous les scrapers récupèrent les événements sur une **fenêtre glissante de 30 jours**.

---

## Stack technique

| Couche | Technologie |
|--------|-------------|
| **Scrapers** | Python 3.12+, httpx (async), Scrapling |
| **Classification LLM** | Gemini 2.5 Flash via `google-genai` SDK |
| **Stockage** | AWS S3 + CloudFront |
| **Orchestration** | AWS Lambda + EventBridge |
| **Frontend** | Next.js 16, React, Tailwind CSS 4 |
| **Hébergement frontend** | Vercel (gratuit) |
| **Package manager** | uv (Python), npm (frontend) |
| **Linting** | ruff (Python), ESLint (frontend) |
| **Tests** | pytest, pytest-asyncio, moto (mock S3) |

---

## Prérequis

- **Python** 3.12+
- **Node.js** 18+
- **[uv](https://docs.astral.sh/uv/)** — gestionnaire de packages Python
- **Clés API** :
  - [Google Gemini](https://aistudio.google.com/apikey) — classification LLM
  - [Google Calendar API](https://console.cloud.google.com/) — scraper RouenOnEst
  - AWS credentials (pour le déploiement)

---

## Installation

### Backend

```bash
# Cloner le repo
git clone https://github.com/your-username/agenda-rouen.git
cd agenda-rouen

# Installer les dépendances (y compris dev)
uv sync --all-extras

# Copier et remplir les variables d'environnement
cp .env.example .env
```

### Frontend

```bash
cd frontend
npm install
```

---

## Configuration

Remplir le fichier `.env` à la racine :

```env
GEMINI_API_KEY=AIza...           # Google Gemini API key
GOOGLE_CALENDAR_API_KEY=AIza...  # Google Calendar API key
EVENTS_BUCKET=agenda-rouen-events
AWS_DEFAULT_REGION=eu-west-3
```

| Variable | Requis | Description |
|----------|:------:|-------------|
| `GEMINI_API_KEY` | Oui | Clé API Gemini pour la classification |
| `GOOGLE_CALENDAR_API_KEY` | Oui | Clé API Google Calendar (scraper RouenOnEst) |
| `EVENTS_BUCKET` | Non | Nom du bucket S3 (défaut : `agenda-rouen-events`) |
| `AWS_DEFAULT_REGION` | Non | Région AWS (défaut : `eu-west-3` Paris) |

---

## Développement

### Commandes backend

```bash
# Lancer tous les tests (45 tests)
uv run pytest

# Lancer un test spécifique
uv run pytest tests/test_openagenda.py::TestOpenAgendaScraper -v

# Lint
uv run ruff check src/ tests/

# Formatage automatique
uv run ruff format src/ tests/

# Vérification de types
uv run mypy src/
```

### Scripts utilitaires

```bash
# Tester les scrapers en live (pas besoin de clé Gemini)
uv run python scripts/test_scrape.py

# Tester le pipeline complet : scrape → classification Gemini
uv run python scripts/test_classify.py
```

### Commandes frontend

```bash
cd frontend

# Serveur de développement
npm run dev

# Build de production
npm run build

# Lint
npm run lint
```

---

## Pipeline de données

Le pipeline s'exécute dans une Lambda AWS déclenchée quotidiennement :

### 1. Scraping

Les 5 scrapers s'exécutent **en parallèle** (async) et collectent les événements des 30 prochains jours :

- **OpenAgenda** (×3) — API JSON v2 avec pagination cursor (`after[]`) et filtre temporel (`timings[gte]`/`timings[lte]`)
- **JDS** — parsing HTML avec Scrapling, pagination par page, filtrage client-side avec arrêt anticipé
- **RouenOnEst** — Google Calendar API avec `timeMin`/`timeMax`

### 2. Classification + Déduplication

Les événements bruts (`RawEvent`) sont classifiés via **Gemini 2.5 Flash** :

- Mapping statique des catégories sources connues vers notre taxonomie unifiée
- Appel LLM uniquement pour les catégories sources inconnues
- Classification par titre (via LLM) pour les événements sans catégorie source
- Déduplication par titre normalisé + date (sans LLM) — conserve l'entrée avec la description la plus longue

### 3. Publication

Les événements classifiés sont publiés en JSON statique sur S3 :

```
s3://{EVENTS_BUCKET}/api/v1/
├── events.json                  # Tous les événements
├── dates/
│   ├── 2026-03-20.json          # Événements du 20 mars
│   ├── 2026-03-21.json
│   └── ...
└── categories/
    ├── musique.json             # Événements musique
    ├── sport.json
    └── ...
```

---

## Frontend (PWA)

Application web progressive (PWA) installable, optimisée mobile-first.

### Fonctionnalités

- **Grille de cartes** responsive (1 / 2 / 3 colonnes)
- **Filtres** : par date (Tout / Aujourd'hui / 7 jours / Week-end) + par catégorie (scroll horizontal avec emojis)
- **Modal détail** : bottom sheet sur mobile, modal centré sur desktop
- **Sticky filters** avec backdrop blur au scroll
- Feedback tactile (`active:scale`) sur les cartes
- Bouton "Voir sur le site source" dans chaque événement
- Installable sur l'écran d'accueil (manifest PWA)

### Palette de couleurs

| Élément | Couleur |
|---------|---------|
| Accent principal | Orange `#F97316` |
| Accent secondaire | Cyan `#06B6D4` |
| Fond | Stone `#FAFAF9` |
| Chaque catégorie | Couleur dédiée (voir `CATEGORY_CONFIG` dans `types.ts`) |

---

## Déploiement

### Backend — AWS Lambda

> *Infrastructure as Code à venir (SAM/CDK)*

Déploiement manuel :

```bash
# 1. Packager les dépendances
uv pip install --target package/ .

# 2. Créer le zip
cd package && zip -r ../lambda.zip . && cd ..
zip lambda.zip -j src/agenda_rouen/handler.py

# 3. Déployer sur Lambda
aws lambda update-function-code \
  --function-name agenda-rouen-scraper \
  --zip-file fileb://lambda.zip

# 4. Configurer les variables d'environnement
aws lambda update-function-configuration \
  --function-name agenda-rouen-scraper \
  --environment "Variables={GEMINI_API_KEY=...,GOOGLE_CALENDAR_API_KEY=...,EVENTS_BUCKET=agenda-rouen-events}"

# 5. Configurer le cron (quotidien à 6h UTC)
aws events put-rule \
  --name agenda-rouen-daily \
  --schedule-expression "cron(0 6 * * ? *)"
```

### Frontend — Vercel

```bash
cd frontend

# Déployer sur Vercel
npx vercel --prod
```

Ou connecter le repo GitHub à Vercel pour des déploiements automatiques.

---

## Structure du projet

```
agenda-rouen/
├── src/agenda_rouen/                # Backend Python
│   ├── models.py                    # RawEvent, Event, Category
│   ├── handler.py                   # Lambda entry point
│   ├── scrapers/
│   │   ├── base.py                  # BaseScraper (async, httpx)
│   │   ├── openagenda.py            # 3 agendas OpenAgenda
│   │   ├── jds.py                   # HTML scraper jds.fr
│   │   └── rouen_on_est.py          # Google Calendar API
│   ├── classifier/
│   │   └── llm.py                   # Gemini classification
│   └── storage/
│       └── s3.py                    # Publication JSON → S3
├── tests/                           # 45 tests pytest
│   ├── test_models.py
│   ├── test_openagenda.py
│   ├── test_jds.py
│   ├── test_rouen_on_est.py
│   ├── test_classifier.py
│   └── test_storage.py
├── scripts/
│   ├── test_scrape.py               # Test live des scrapers
│   └── test_classify.py             # Test scrape + classification
├── frontend/                        # PWA Next.js
│   ├── src/
│   │   ├── app/                     # Pages Next.js (App Router)
│   │   ├── components/              # EventCard, EventModal, Filters, Header
│   │   └── lib/                     # Types, filtres, données sample
│   └── public/
│       └── manifest.json            # PWA manifest
├── pyproject.toml                   # Config Python (uv, ruff, pytest, mypy)
├── .env.example                     # Variables d'environnement template
└── CLAUDE.md                        # Guide pour Claude Code
```

---

## API JSON publiée

Une fois le pipeline exécuté, les fichiers JSON sont accessibles via CloudFront :

### `GET /api/v1/events.json`

Tous les événements classifiés et dédupliqués.

```json
[
  {
    "id": "3164642986eca7c1",
    "title": "Santa - Tournée",
    "description": "Santa présente son album...",
    "date_start": "2026-03-24",
    "date_end": null,
    "time": "20:30",
    "location": "Zénith de Rouen",
    "address": "44 Av. des Canadiens, 76120 Le Grand-Quevilly",
    "category": "musique",
    "tags": ["chanson française", "concert"],
    "urls": ["https://www.jds.fr/..."],
    "image_url": "https://...",
    "sources": ["jds", "openagenda_metropole"],
    "classified_at": "2026-03-18T12:00:00Z"
  }
]
```

### `GET /api/v1/dates/{YYYY-MM-DD}.json`

Événements pour une date spécifique.

### `GET /api/v1/categories/{category}.json`

Événements par catégorie (`musique`, `sport`, `spectacles`, etc.).

---

## Taxonomie des événements

| Catégorie | Emoji | Description |
|-----------|:-----:|-------------|
| `musique` | 🎵 | Concerts, DJ sets, festivals musicaux |
| `spectacles` | 🎭 | Théâtre, danse, cirque, performances |
| `sport` | ⚽ | Matchs, compétitions, événements sportifs |
| `expositions` | 🎨 | Expositions, galeries, visites guidées |
| `cinéma` | 🎬 | Projections, avant-premières |
| `festival` | 🎉 | Festivals multi-disciplinaires |
| `ateliers` | 🛠️ | Ateliers créatifs, scientifiques, participatifs |
| `famille` | 👨‍👩‍👧 | Activités familiales, ateliers enfants |
| `vie-nocturne` | 🌙 | Soirées, clubs, bars |
| `autre` | 📌 | Tout ce qui ne rentre pas ailleurs |

> Les catégories `conférences` et `gastronomie` sont exclues du pipeline (événements supprimés).
