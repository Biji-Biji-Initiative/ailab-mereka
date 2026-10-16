# ailab.mereka.dev — AI Labs (static clone of ailab.mereka.io)

A clean, hand-coded static rebuild of the Mereka **AI Labs** WordPress site
(`ailab.mereka.io`). No WordPress, no Bricks, no PHP — just HTML/CSS/JS served
by nginx. Deployed on GitHub → Coolify (`deploy-apps-01`) → Traefik/TLS.

## Structure
```
index.html                     Home — hero, the two audiences, Prompts, proof        hand-written
corporate-training/index.html  AI Lab Corporate Training (in-house)                  hand-written
public-training/index.html     AI Lab Public Training (open cohorts)                 hand-written
partials/footer.html           The CTA band + footer those three share               hand-written
assets/ailab.css               Their stylesheet (holds the injected NAV-CSS block)
assets/ailab.js               Their JS: reveal, counters, Prompts tabs, cohort filter
prompts/index.html             Prompt Library — 187 prompts + 131 use cases          generated
<slug>/index.html              20 role pages (use cases + prompts + roles)           generated
data.json / content.json       Content pulled from the WP REST API
build.py                       Generates the pages above; injects nav/footer/SEO into the hand-written three
theme.py / navdata.py          Shared chrome. navdata.py is scraped — add AI Lab items in theme.py
sync.py                        Re-sync pipeline (the "WordPress connector")
Dockerfile / nginx.conf        Container: nginx:alpine serving the static files on :80
```

### The three hand-written pages
They carry content only. Everything shared reaches them through marker pairs
that `build.py` rewrites, so none of it can drift:

| Marker | Filled with |
| --- | --- |
| `<!--NAV-->…<!--/NAV-->` | `theme.nav()` |
| `<!--FOOT-->…<!--/FOOT-->` | `partials/footer.html` |
| `<!--SEO-->…<!--/SEO-->` | title, meta, canonical and JSON-LD (the FAQ block is parsed back out of the page's own markup) |
| `/*NAV-CSS*/…/*/NAV-CSS*/` in `assets/ailab.css` | `theme.MENU_CSS` |

Run `python3 build.py` after editing any of them — it also stamps
`/assets/ailab.{css,js}` with a content hash, because nginx caches those for
7 days and a stale stylesheet would outlive the deploy.

## The WordPress "connector" (content sync)
The site is decoupled from WordPress, but stays in sync with it on demand.
`sync.py` reads the **public WordPress REST API** at `ailab.mereka.io/wp-json/wp/v2/`
(no credentials needed for published content) and regenerates `data.json`,
`prompts/index.html`, and every `department/<slug>/index.html`.

```bash
python3 sync.py          # pull latest content from ailab.mereka.io and regenerate
git add -A && git commit -m "sync content from ailab.mereka.io" && git push
```
Pushing to `main` redeploys via the GitHub webhook below. Always byte-compare the live pages against the repo afterwards — a green Coolify job is not proof the site changed. A weekly GitHub Action
(`.github/workflows/sync.yml`) can run this automatically.

> Prompt text lives in each item's title (the WP CMS stores it there);
> use-case bodies are titles too. Departments map to prompts/use-cases via
> ACF fields `department_prompts` / `department_use-cases`.

## SEO / going to production

`ailab.mereka.dev` is a preview and must never be indexed. Every page ships
`noindex, nofollow` and `robots.txt` disallows everything.

The metadata itself is written for production, so promoting it is one switch:

```bash
AILAB_SITE_URL=https://ailab.mereka.io python3 build.py
```

That flips every canonical, `og:url`, sitemap entry and the robots rules to the
production host and drops the noindex. Build without the variable and you are
back to a noindexed preview. Nothing else needs editing.

Per page: unique title (<=60 chars) and description (<=155), Open Graph +
Twitter card, and JSON-LD — Organization and WebSite everywhere, plus
Service/OfferCatalog and FAQPage on the homepage (the FAQ schema is parsed out
of the rendered page, so it cannot drift from the visible copy) and
CollectionPage + BreadcrumbList on the library and category pages.

## Deploy
- Coolify app UUID: `f5uw9prltijdaifgkq95wgme` (build pack: Dockerfile, port 80)
- Auto-deploy: `.github/workflows/deploy.yml` calls the Coolify deploy API on every push
  to `main`, using the `COOLIFY_API_TOKEN` repo secret. Coolify's own "deploy on push"
  cannot work here — the app's Git source is **Public GitHub**, not a GitHub App, so
  Coolify may not install a webhook on the repo and never hears about a push. That is why
  pushes did nothing until 2026-10-16.
- Domains: `ailab.mereka.dev`, `www.ailab.mereka.dev`
- DNS: Cloudflare A records → `194.233.71.200` (DNS-only / grey cloud)
