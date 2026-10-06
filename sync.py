#!/usr/bin/env python3
"""
sync.py — pull all content from the live WordPress site at ailab.mereka.io
and refresh data.json, then regenerate the static pages via build.py.

Two sources, both public (no credentials needed):
  * the WP REST API  (/wp-json/wp/v2/)  — ids, titles, categories, tags
  * the rendered /prompts/ listing pages — the exact category page each prompt
    links to. WordPress picks one "primary" category per prompt and there is no
    rule that reproduces its choice from the API alone, so we read it back from
    the rendered pages and keep ailab.mereka.dev 1-to-1 with ailab.mereka.io.

Run:  python3 sync.py      then commit & push (Coolify redeploys on push).
"""
import urllib.request, json, os, re, html as _html, time, subprocess, sys

SRC  = os.environ.get("WP_SRC",  "https://ailab.mereka.io/wp-json/wp/v2/")
SITE = os.environ.get("WP_SITE", "https://ailab.mereka.io")
REPO = os.path.dirname(os.path.abspath(__file__))
UA   = {"User-Agent": "ailab-sync"}

def _get(path):
    req = urllib.request.Request(SRC + path, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.load(r), r.headers

def _all(pt, fields):
    out, page = [], 1
    while True:
        d, h = _get(f"{pt}?per_page=100&page={page}&_fields={fields}&orderby=title&order=asc")
        out += d
        if page >= int(h.get("X-WP-TotalPages", "1")): break
        page += 1
    return out

def _dec(s):
    return _html.unescape(s) if s else ""

# ---------------------------------------------------------------- REST API
print("Fetching from", SRC)
cats_raw    = _get("categories?per_page=100&_fields=id,name,slug,count")[0]
tags_raw    = _get("tags?per_page=100&_fields=id,name,slug")[0]
prompts_raw = _all("prompt",   "id,slug,title,categories,tags")
uc_raw      = _all("use-case", "id,slug,title,categories")
deps_raw    = _get("department?per_page=100&orderby=title&order=asc")[0]

TAG = {t["id"]: t for t in tags_raw}
CAT = {c["id"]: c for c in cats_raw}

# ------------------------------------------------- rendered listing scrape
# Each row: <a class="... prompt__title" href="/<category>#prompt-<id>">Title</a>
#           followed by <span class="bricks-button">tag</span> chips.
def scrape_listing():
    rows, page = {}, 1
    while True:
        url = f"{SITE}/prompts/" if page == 1 else f"{SITE}/prompts/page/{page}/"
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=45) as r:
                s = r.read().decode("utf-8", "replace")
        except Exception as e:
            print(f"  listing page {page}: {e} — stopping scrape")
            break
        found = 0
        for m in re.finditer(
                r'<a[^>]*class="[^"]*prompt__title[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>(.*?)</div>', s, re.S):
            href, rest = m.group(1), m.group(3)
            pid = re.search(r"#prompt-(\d+)", href)
            if not pid: continue
            rows[int(pid.group(1))] = {
                "h": href,
                "g": [_dec(t).strip() for t in re.findall(r'<span class="bricks-button">([^<]*)</span>', rest)],
            }
            found += 1
        print(f"  listing page {page}: {found} rows (total {len(rows)})")
        if found == 0: break
        page += 1
        time.sleep(0.3)
    return rows

listing = scrape_listing()

# --------------------------------------------------------------- assemble
def href_for(p):
    """Category page this prompt links to.

    For a prompt in one category we use io's own rendered link. For a prompt in
    several, io is NOT deterministic — the same URL re-rendered picks a different
    "primary" category between requests (prompt 795 alternates between
    /human-resources and /recruitment). Chasing that would churn the diff on
    every sync, so we pin multi-category prompts to their lowest term id, which
    is one of the values io itself serves. Either way the link resolves: build.py
    writes the #prompt-<id> anchor onto EVERY category page a prompt appears on.
    """
    ids = [c for c in (p.get("categories") or []) if c in CAT and CAT[c]["slug"] != "uncategorized"]
    hit = listing.get(p["id"])
    if hit and hit["h"] and len(ids) <= 1:
        return hit["h"]
    return f"/{CAT[min(ids)]['slug']}#prompt-{p['id']}" if ids else ""

def tags_for(p):
    """Real post-tag slugs (pr, press-release, ...).

    The REST API decides WHICH tags a prompt has — it is authoritative and can
    legitimately be empty (prompt 737 carries none). The rendered listing only
    decides the ORDER they are shown in, so a prompt never inherits its category
    name as a pseudo-tag the way the old page did.
    """
    api = [TAG[t]["slug"] for t in (p.get("tags") or []) if t in TAG]
    hit = listing.get(p["id"])
    if hit and hit["g"]:
        order = {g: i for i, g in enumerate(hit["g"])}
        return sorted(api, key=lambda g: (order.get(g, len(order)), g))
    return api

prompts = [{
    "id": p["id"],
    "t":  _dec(p["title"]["rendered"]),
    "c":  p.get("categories") or [],
    "g":  tags_for(p),
    "h":  href_for(p),
} for p in prompts_raw]

# prompts per category (this is the count ailab.mereka.io shows in its dropdown)
pcount = {}
for p in prompts:
    for cid in p["c"]:
        pcount[cid] = pcount.get(cid, 0) + 1

data = {
  "categories": sorted(
      [{"id": c["id"], "name": _dec(c["name"]), "slug": c["slug"],
        "count": c["count"], "prompts": pcount.get(c["id"], 0)} for c in cats_raw],
      key=lambda x: x["name"].lower()),
  "tags": sorted([{"id": t["id"], "name": _dec(t["name"]), "slug": t["slug"]} for t in tags_raw],
                 key=lambda x: x["slug"]),
  "departments": [{
      "slug": d["slug"], "title": _dec(d["title"]["rendered"]),
      "desc": _dec((d.get("acf") or {}).get("department_description", "")),
      "roles": _dec((d.get("acf") or {}).get("department_roles", "")),
      "uc": [(x.get("ID") or x.get("id")) if isinstance(x, dict) else x
             for x in ((d.get("acf") or {}).get("department_use-cases") or [])],
      "pr": [(x.get("ID") or x.get("id")) if isinstance(x, dict) else x
             for x in ((d.get("acf") or {}).get("department_prompts") or [])],
  } for d in deps_raw],
  "prompts": prompts,
  "usecases": [{"id": u["id"], "t": _dec(u["title"]["rendered"]), "c": u.get("categories") or []} for u in uc_raw],
}

json.dump(data, open(f"{REPO}/data.json", "w"), ensure_ascii=False, indent=0)
missing = [p["id"] for p in prompts if not p["h"]]
print(f"data.json: {len(data['categories'])} cats, {len(data['tags'])} tags, "
      f"{len(data['departments'])} depts, {len(prompts)} prompts, {len(data['usecases'])} use-cases")
print(f"  prompts with a resolved detail link: {len(prompts)-len(missing)}/{len(prompts)}"
      + (f"  MISSING: {missing}" if missing else ""))

# ------------------------------------------------------------- regenerate
# build.py owns every rendered page (/prompts/ + the category pages).
print("\nRegenerating pages via build.py …")
sys.exit(subprocess.call([sys.executable, os.path.join(REPO, "build.py")]))
