# TODO

## Pipeline backend

- [ ] Ajouter le scraper Shotgun (actuellement bloqué par la protection bot Vercel)
- [ ] Tests scrapers : couvrir les cas d'erreur (HTTP 500, JSON malformé, timeout, 429)
- [ ] Dédup : fusionner les URLs des events dupliqués entre sources (multi-source support)
- [ ] Publier un `api/v1/index.json` dans S3 (dates, catégories, count, last_updated)
- [ ] Utiliser `context.get_remaining_time_in_millis()` dans le handler Lambda pour shutdown gracieux
- [ ] Validation Pydantic : titre non vide, date_end >= date_start dans les modèles

## Frontend

- [ ] Ajouter `loading.tsx` (skeleton) et `error.tsx` (error boundary Next.js)
- [ ] Contraste dark mode : remonter `--muted` à `#8a8580` en dark pour respecter WCAG AA (4.5:1)
- [ ] Filtre catégorie : navigation clavier (flèches) + `role="radiogroup"`
- [ ] `aria-label` manquants sur EventCard (bouton), EventModal (fermer), SearchBar (effacer)
- [ ] Utiliser `next/image` pour optimisation auto (WebP, srcset, lazy load)
- [ ] Précacher `/icon` et `/apple-icon` dans le service worker

## Infra

- [ ] Configurer le déploiement IaC (CDK, Terraform, ou SAM) pour Lambda + EventBridge + S3 + CloudFront
- [ ] Ajouter un domaine custom sur CloudFront
