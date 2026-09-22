# ailab.mereka.dev — AI Labs (static clone of ailab.mereka.io)

A clean, hand-coded static rebuild of the Mereka **AI Labs** WordPress site
(`ailab.mereka.io`). No WordPress, no Bricks, no PHP — just HTML/CSS/JS served
by nginx. Deployed on GitHub → Coolify (`deploy-apps-01`) → Traefik/TLS.

## Structure
```
index.html                     Homepage (hero, departments, programmes, impact, resources)
prompts/index.html             Prompt Library — searchable/filterable directory (187 prompts + 131 use cases)
department/<slug>/index.html    5 department pages (use cases + prompts + roles)
data.json                      Content pulled from the WP REST API (categories, departments, prompts, use cases)
sync.py                        Re-sync pipeline (the "WordPress connector") — pulls live content & regenerates
Dockerfile / nginx.conf        Container: nginx:alpine serving the static files on :80
```

## The WordPress "connector" (content sync)
The site is decoupled from WordPress, but stays in sync with it on demand.
`sync.py` reads the **public WordPress REST API** at `ailab.mereka.io/wp-json/wp/v2/`
(no credentials needed for published content) and regenerates `data.json`,
`prompts/index.html`, and every `department/<slug>/index.html`.

```bash
python3 sync.py          # pull latest content from ailab.mereka.io and regenerate
git add -A && git commit -m "sync content from ailab.mereka.io" && git push
```
Pushing to `main` triggers a Coolify redeploy. A weekly GitHub Action
(`.github/workflows/sync.yml`) can run this automatically.

> Prompt text lives in each item's title (the WP CMS stores it there);
> use-case bodies are titles too. Departments map to prompts/use-cases via
> ACF fields `department_prompts` / `department_use-cases`.

## Deploy
- Coolify app UUID: `f5uw9prltijdaifgkq95wgme` (build pack: Dockerfile, port 80)
- Domains: `ailab.mereka.dev`, `www.ailab.mereka.dev`
- DNS: Cloudflare A records → `194.233.71.200` (DNS-only / grey cloud)
