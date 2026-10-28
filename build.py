#!/usr/bin/env python3
"""Generate ailab.mereka.dev pages 1-to-1 with ailab.mereka.io:
   /prompts/ (AI Cookbooks) and /{category}/ role pages. Uses data.json + content.json + theme.py."""
import json, os, html, sys, re, unicodedata
import html as _html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme

REPO=os.path.dirname(os.path.abspath(__file__))
data=json.load(open(f"{REPO}/data.json"))
content=json.load(open(f"{REPO}/content.json"))
cats={c["slug"]:c for c in data["categories"]}
catname=lambda ids:next((cats2["name"] for cid in ids for cats2 in [ {c["id"]:c for c in data["categories"]}.get(cid)] if cats2), "")
CATBYID={c["id"]:c for c in data["categories"]}
esc=html.escape

# ---------------- ROLE PAGES ----------------
ROLE_CSS = """
/* A role page stacks two sticky bars: the 78px nav and the "On this page"
   strip pinned under it (bottom edge ~149px). The global 100px that matches
   ailab.mereka.io is right for /prompts/, but here it would drop a linked
   prompt's title behind that strip, so clear the whole stack. */
html{scroll-padding-top:176px}
/* Hero, laid out as on ailab.mereka.io — full-bleed under the nav, rounded
   only along the bottom, "Back to Prompts" centred above the title — in the
   FOB AI Lab palette (Anchor Blue + Strategy Teal tints). */
.rhero{position:relative;overflow:hidden;text-align:center;padding:104px 0 118px;border-radius:0 0 80px 80px}
.rhero::before{content:'';position:absolute;inset:0;z-index:0;
  background:radial-gradient(58% 78% at 10% 28%,#9fd6d7 0%,rgba(159,214,215,0) 62%),radial-gradient(52% 72% at 88% 22%,#b9c8e4 0%,rgba(185,200,228,0) 64%),radial-gradient(64% 86% at 46% 102%,#d6e7ee 0%,rgba(214,231,238,0) 66%),linear-gradient(135deg,#eaf2f4 0%,#eef1f7 100%)}
.rhero-in{position:relative;z-index:1;max-width:1008px;margin:0 auto;padding:0 24px}
.rhero .back{display:inline-flex;gap:6px;align-items:center;font-weight:500;font-size:1rem;color:var(--ink);margin-bottom:36px}
.rhero .back:hover{opacity:.7}
.rhero h1{font-size:clamp(2.4rem,6.9vw,6rem);line-height:1.05;color:var(--ink);margin:0 0 20px}
.rhero p{color:var(--ink);font-size:1.25rem;line-height:1.5;max-width:64ch;margin:0 auto}
/* "On this page" — a sticky card that follows you down the page and marks the
   use case you are currently in, as on ailab.mereka.io. The wrapper reserves
   only the collapsed height so the open panel overlays the content instead of
   shoving it down. */
.onthis{position:sticky;top:98px;z-index:45;height:46px;max-width:var(--maxw);margin:24px auto 0;padding:0 28px}
.toc{position:absolute;left:28px;top:0;width:296px;max-width:calc(100vw - 56px);
  background:#fff;border:1px solid var(--line);border-radius:20px;box-shadow:0 14px 38px rgba(26,22,35,.14);padding:5px}
.toc-h{display:flex;align-items:center;justify-content:space-between;gap:10px;width:100%;
  background:none;border:0;cursor:pointer;font-family:inherit;font-weight:600;font-size:.98rem;color:var(--ink);padding:9px 14px}
.toc-h .chev{flex:none;transition:transform .2s var(--ease)}
.toc.open .toc-h .chev{transform:rotate(180deg)}
.toc-list{list-style:none;margin:0;padding:0 0 4px;display:none}
.toc.open .toc-list{display:block}
.toc-list a{display:block;padding:8px 16px;border-radius:12px;color:var(--muted);font-size:.95rem;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.toc-list a:hover{background:var(--grey);color:var(--ink)}
.toc-list a.on{background:var(--accent);color:#fff;font-weight:500}
@media(max-width:860px){.rhero{padding:64px 0 76px;border-radius:0 0 44px 44px}
  .rhero p{font-size:1.06rem}
  .onthis{top:92px;margin-top:18px;padding:0 20px}
  .toc{left:20px;max-width:calc(100vw - 40px)}
  html{scroll-padding-top:170px}}
.uc{padding:38px 0 0}
.uc .lbl{color:var(--pink);font-weight:600;font-size:.82rem;letter-spacing:.12em;text-transform:uppercase}
.uc h2{font-size:clamp(1.5rem,3vw,2.1rem);margin:8px 0 6px}
.uc .ucsub{color:var(--muted);font-size:1.02rem;margin:0 0 22px;max-width:70ch}
.prompt{margin:22px 0}
.prompt .pname{font-weight:600;font-size:1.02rem;margin-bottom:10px}
.pbox{position:relative;background:#161122;color:#d8d5e4;border-radius:16px;padding:22px 54px 22px 22px;
  font-family:'SFMono-Regular',ui-monospace,Menlo,Consolas,monospace;font-size:.86rem;line-height:1.72;white-space:pre-wrap;word-break:break-word}
.pbox .copy{position:absolute;top:14px;right:14px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.16);color:#cfc9e0;border-radius:9px;width:34px;height:34px;cursor:pointer;display:flex;align-items:center;justify-content:center}
.pbox .copy:hover{background:rgba(255,255,255,.16)}
.pbox .copy.done{background:var(--pink);color:#fff;border-color:var(--pink)}
.rfoot-cta{margin:54px 0 10px}
"""

COPY_SVG='<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg>'

def slugify(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')

# ---- title -> prompt id, so each card can carry the #prompt-<id> anchor that
# ---- /prompts/ links to (same scheme as ailab.mereka.io).
def _norm(s):
    s=unicodedata.normalize("NFKC", html.unescape(s or ""))
    for a,b in (("\u2018","'"),("\u2019","'"),("\u201c",'"'),("\u201d",'"'),("\u2013","-"),("\u2014","-")):
        s=s.replace(a,b)
    return re.sub(r"\s+"," ",s).strip().lower()

# prompts indexed by (category id, normalised title) and by title alone
PROMPT_BY_CAT={}
PROMPT_BY_TITLE={}
for _p in data["prompts"]:
    PROMPT_BY_TITLE.setdefault(_norm(_p["t"]), _p)
    for _cid in _p.get("c") or []:
        PROMPT_BY_CAT.setdefault((_cid, _norm(_p["t"])), _p)

def prompt_id_for(cat_id, title):
    """id of the prompt with this title on this category page (falls back to a
    title-only match so a card is still addressable if WP's categories drift)."""
    hit = PROMPT_BY_CAT.get((cat_id, _norm(title))) or PROMPT_BY_TITLE.get(_norm(title))
    return hit["id"] if hit else None

_SMALL = {"and", "or", "of", "for", "the", "a", "an", "to", "in", "on", "&"}
def _nice(name):
    """WordPress category names arrive in mixed case. Title-case them for titles,
    headings and breadcrumbs without touching words that are already capitalised."""
    words = name.split()
    return " ".join(w if (i and w.lower() in _SMALL) or w[:1].isupper() else w[:1].upper() + w[1:]
                    for i, w in enumerate(words))

def role_page(slug, r):
    groups=r["groups"]
    cat_id=(cats.get(slug) or {}).get("id")
    seen=set()
    # one id per use case, de-duplicated: a page can repeat a heading
    # (customer-support-service lists "Improve customer service" twice), and two
    # sections sharing an id would send the TOC to the wrong one.
    gids=[]; used={}
    for i,g in enumerate(groups,1):
        base=slugify(g["usecase"]) or f"uc{i}"
        used[base]=used.get(base,0)+1
        gids.append(base if used[base]==1 else f"{base}-{used[base]}")
    toc="".join(f'<li><a href="#{gid}">{esc(g["usecase"])}</a></li>'
                for gid,g in zip(gids,groups) if g["usecase"])
    body=""
    for i,(gid,g) in enumerate(zip(gids,groups),1):
        prompts=""
        for p in g["prompts"]:
            name=f'<div class="pname">{esc(p["name"])}</div>' if p.get("name") else ""
            b=esc(p["body"])
            # anchor target for /prompts/ — only on the card's first appearance,
            # so the id stays unique even when a prompt is reused across use cases
            pid=prompt_id_for(cat_id, p.get("name") or "")
            anchor=f' id="prompt-{pid}"' if pid and pid not in seen else ""
            if pid: seen.add(pid)
            prompts+=f'''<div class="prompt"{anchor}>{name}<div class="pbox"><button class="copy" aria-label="Copy" onclick="cp(this)"data-t="{esc(p["body"])}">{COPY_SVG}</button>{b}</div></div>'''
        body+=f'''<section class="uc" id="{gid}"><div class="shell">
  <div class="lbl">Use Case {i}</div>
  <h2>{esc(g["usecase"])}</h2>
  {prompts}
</div></section>'''
    n_prompts = sum(len(g["prompts"]) for g in groups)
    n_cases   = len([g for g in groups if g["usecase"]])
    name = _nice(r["title"])
    # keep the brand suffix; drop the count before dropping the brand
    seo_title = next(t for t in (f'{name} AI Prompts ({n_prompts}) | Mereka AI Lab',
                                 f'{name} AI Prompts | Mereka AI Lab',
                                 f'{name} AI Prompts ({n_prompts})') if len(t) <= 60)
    # whole clauses only, so a description never ends mid-sentence; the longest
    # option that fits wins (the old builder fell back to ~90-character stubs)
    _lead = (f'{n_prompts} tested AI {theme.plural(n_prompts, "prompt")} for {name.lower()} '
             f'across {n_cases} {theme.plural(n_cases, "use case")}')
    _sub  = " ".join((r.get("subtitle") or "").split()).rstrip(".")
    _opts = []
    if _sub:
        _opts += [f'{_lead}: {_sub}. Free to copy, no sign-up.', f'{_lead}: {_sub}.']
    _opts += [f'{_lead}. Copy into ChatGPT, Copilot, Claude or Gemini. Free, no sign-up.',
              f'{_lead}. Free to copy, no sign-up.', f'{_lead}.']
    seo_desc = next(d for d in _opts if len(d) <= 155)
    schema = [
        {"@type": "CollectionPage",
         "@id": theme.PROD_URL + f'/{slug}/#page',
         "url": theme.PROD_URL + f'/{slug}/',
         "name": f'{name} AI Prompts',
         "description": r.get("subtitle") or r["title"],
         "isPartOf": {"@id": theme.PROD_URL + "/#website"},
         "about": {"@type": "Thing", "name": name},
         "mainEntity": {"@type": "ItemList", "numberOfItems": n_prompts,
                        "itemListElement": [
                            {"@type": "ListItem", "position": i, "name": pr["name"]}
                            for i, pr in enumerate(
                                [pr for g in groups for pr in g["prompts"] if pr.get("name")][:25], 1)]}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": theme.PROD_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "AI Prompts", "item": theme.PROD_URL + "/prompts/"},
            {"@type": "ListItem", "position": 3, "name": name,
             "item": theme.PROD_URL + f'/{slug}/'}]},
    ]
    page=theme.head(seo_title, seo_desc, f'/{slug}/', ROLE_CSS, schema) + theme.nav("prompts") + f'''
<section class="rhero"><div class="rhero-in">
  <a class="back" href="/prompts/"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M15.41 16.59 10.83 12l4.58-4.59L14 6l-6 6 6 6 1.41-1.41Z"/></svg>Back to Prompts</a>
  <h1>{esc(name)}</h1>
  <p>{esc(r["subtitle"])}</p>
</div></section>
<div class="onthis"><div class="toc" id="toc">
  <button class="toc-h" type="button" aria-expanded="false" aria-controls="toc-list" onclick="tocToggle()">
    <span>On this page</span>
    <svg class="chev" width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7.41 8.59 12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41Z"/></svg>
  </button>
  <ul class="toc-list" id="toc-list">{toc}</ul>
</div></div>
{body}
<div class="shell rfoot-cta"><a class="btn btn-accent" href="/prompts/">Browse all prompts &rarr;</a></div>
{theme.footer()}
<script>
function cp(b){{navigator.clipboard.writeText(b.dataset.t).then(()=>{{b.classList.add('done');var s=b.innerHTML;b.textContent='✓';setTimeout(()=>{{b.classList.remove('done');b.innerHTML=s;}},1300);}});}}
/* Land on the #prompt-<id> a /prompts/ link points at. The browser already does
   this, but its on-load scroll is animated (html{{scroll-behavior:smooth}}) and
   runs before the self-hosted Poppins faces finish loading — the reflow that
   follows leaves you short of the prompt. Re-anchor once everything has settled. */
function anchorToHash(){{
  if(!location.hash) return;
  var el=document.getElementById(location.hash.slice(1));
  if(el) el.scrollIntoView({{behavior:'instant',block:'start'}});  /* 'auto' would inherit scroll-behavior:smooth */
}}
window.addEventListener('load',function(){{
  anchorToHash();
  if(document.fonts&&document.fonts.ready) document.fonts.ready.then(anchorToHash);
}});
window.addEventListener('hashchange',anchorToHash);

/* "On this page": open/close, and highlight the use case currently in view. */
(function(){{
  var toc=document.getElementById('toc');
  if(!toc) return;
  var links=[].slice.call(document.querySelectorAll('#toc-list a'));
  var secs=links.map(function(a){{ return document.getElementById(a.getAttribute('href').slice(1)); }});
  window.tocToggle=function(){{
    var open=toc.classList.toggle('open');
    toc.querySelector('.toc-h').setAttribute('aria-expanded', open?'true':'false');
  }};
  /* The marker sits just below the sticky nav + card, so a use case becomes
     "current" as soon as its heading clears them. Section offsets are measured
     up front and re-measured on resize/font load, which keeps the scroll
     handler pure arithmetic — no layout reads, so it needs no rAF throttle. */
  var OFFSET=180, tops=[], active=-1;
  function measure(){{
    tops=secs.map(function(s){{ return s ? s.getBoundingClientRect().top+window.scrollY : Infinity; }});
  }}
  function spy(){{
    var y=window.scrollY+OFFSET, best=0;
    for(var i=0;i<tops.length;i++){{ if(tops[i]<=y) best=i; }}
    /* at the very bottom the last section is current even if its top never
       reaches the marker */
    if(window.innerHeight+window.scrollY>=document.documentElement.scrollHeight-2) best=tops.length-1;
    if(best===active) return;
    active=best;
    for(var j=0;j<links.length;j++) links[j].classList.toggle('on', j===best);
  }}
  function remeasure(){{ measure(); active=-1; spy(); }}
  window.addEventListener('scroll',spy,{{passive:true}});
  window.addEventListener('resize',remeasure);
  window.addEventListener('load',remeasure);
  if(document.fonts&&document.fonts.ready) document.fonts.ready.then(remeasure);
  remeasure();
}})();
</script>
</body></html>'''
    os.makedirs(f"{REPO}/{slug}", exist_ok=True)
    open(f"{REPO}/{slug}/index.html","w").write(page)
    return sum(len(g["prompts"]) for g in groups)

total=0
for slug,r in content["roles"].items():
    total+=role_page(slug,r)
print(f"role pages: {len(content['roles'])}, prompts rendered: {total}")

# ------------- keep the hand-written pages' chrome in sync -------------
# index.html and the two training pages are hand-written, but they must not
# carry their own copies of the header, the footer or the mega-menu CSS: that
# drifted from theme.nav() twice already. Each page declares marker pairs and
# this injects the generated markup into them. The page CSS and JS are shared
# files under /assets, so the nav CSS is injected there instead of per page.
import re as _re

_FOOTER = open(f"{REPO}/partials/footer.html").read().rstrip("\n")
# Home drops the "Book a Free Discovery Call" band (Ambika's design, 2026-10-16);
# the training pages keep it. Same partial, band cut out where a page opts out.
_FOOTER_NO_BAND = _re.sub(r'\n?\s*<div class="cta-band">.*?(?=\n\s*<div class="foot2">)', "",
                          _FOOTER, count=1, flags=_re.S)
assert "cta-band" not in _FOOTER_NO_BAND and "foot2" in _FOOTER_NO_BAND, "contact band split failed"

def _inject(path, marker, markup):
    """Replace <!--MARKER-->…<!--/MARKER--> (or the /*MARKER*/ form in CSS)."""
    txt = open(path).read()
    if marker.startswith("/*"):
        open_t, close_t = marker, "/*/" + marker[2:]
        pat = _re.escape(open_t) + ".*?" + _re.escape(close_t)
    else:
        open_t, close_t = f"<!--{marker}-->", f"<!--/{marker}-->"
        pat = _re.escape(open_t) + ".*?" + _re.escape(close_t)
    if open_t not in txt or close_t not in txt:
        raise SystemExit(f"{path} is missing its {open_t} / {close_t} markers")
    out = _re.sub(pat, lambda _m: open_t + markup + close_t, txt, flags=_re.S)
    if out != txt:
        open(path, "w").write(out)
    return out != txt

# the shared stylesheet owns the mega-menu CSS
_css_changed = _inject(f"{REPO}/assets/ailab.css", "/*NAV-CSS*/", theme.MENU_CSS)
print("assets/ailab.css: nav CSS", "updated" if _css_changed else "already current")

# ---- the three hand-written pages ----
import catalogue as _cat

# Titles stay under ~60 characters and descriptions under ~155 so neither is
# truncated in a results page; every claim here is stated on the page itself.
_HOME_TITLE = "HRD Corp Claimable AI Training in Malaysia | Mereka AI Lab"
_HOME_DESC  = ("Hands-on, HRD Corp claimable AI training for Malaysian teams: in-house corporate "
               "programmes, open public workshops and 187 free AI prompts by role.")
_CORP_TITLE = "Corporate AI Training for Teams in Malaysia | Mereka AI Lab"
_CORP_DESC  = ("In-house, HRD Corp claimable AI training for your team: AI Foundation, Levels 2-5, "
               "AI Leadership, tool deep dives and custom department programmes.")
_PUB_TITLE  = "Public AI Workshops in Kuala Lumpur | Mereka AI Lab"
_PUB_DESC   = ("Book an open, HRD Corp claimable AI workshop: AI Foundation or a hands-on deep dive "
               "in ChatGPT, Copilot, Claude, Gemini or Canva AI. Seats from RM 300.")
for _t, _d in ((_HOME_TITLE, _HOME_DESC), (_CORP_TITLE, _CORP_DESC), (_PUB_TITLE, _PUB_DESC)):
    assert len(_t) <= 60 and len(_d) <= 155, (_t, len(_t), len(_d))

_ORG = {"@id": theme.PROD_URL + "/#organisation"}

def _crumbs(name, path):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": theme.PROD_URL + "/"},
        {"@type": "ListItem", "position": 2, "name": name, "item": theme.PROD_URL + path}]}

def _service(service_type, audience, low, unit, url):
    return {"@type": "Service", "serviceType": service_type, "provider": _ORG,
            "areaServed": {"@type": "Country", "name": "Malaysia"},
            "audience": {"@type": "BusinessAudience", "name": audience},
            "offers": {"@type": "Offer", "url": url, "priceCurrency": "MYR",
                       "priceSpecification": {"@type": "UnitPriceSpecification", "minPrice": low,
                                              "priceCurrency": "MYR", "unitText": unit}}}

# AI case studies: each is a hand-written article at /case-studies/<slug>/,
# listed newest first on /case-studies/. Add one entry here per new article;
# "published" is the date it went live on this site, never an earlier post's.
_CS_TITLE = "AI Case Studies: How Mereka Teams Use AI | Mereka AI Lab"
_CS_DESC  = ("Real examples of Mereka teams building with AI: what each tool does, what it "
             "changed and the numbers behind it.")
CASE_STUDIES = [
    {"slug": "team-analytics-dashboard",
     "headline": "How We Built an AI-Powered Team Analytics Dashboard",
     "title": "AI Team Analytics Dashboard Case Study | Mereka AI Lab",
     "desc": ("How Mereka built a team analytics dashboard with AI: reports that took 4 to 6 "
              "hours now take 30 seconds, with 50+ metrics refreshed every 2 hours."),
     "published": "2026-10-28"},
]
for _t, _d in [(_CS_TITLE, _CS_DESC)] + [(_c["title"], _c["desc"]) for _c in CASE_STUDIES]:
    assert len(_t) <= 60 and len(_d) <= 155, (_t, len(_t), len(_d))

def _case_crumbs(c):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": theme.PROD_URL + "/"},
        {"@type": "ListItem", "position": 2, "name": "AI Case Studies",
         "item": theme.PROD_URL + "/case-studies/"},
        {"@type": "ListItem", "position": 3, "name": c["headline"],
         "item": theme.PROD_URL + f"/case-studies/{c['slug']}/"}]}

def _case_article(c):
    return {"@type": "Article", "headline": c["headline"], "description": c["desc"],
            "datePublished": c["published"], "inLanguage": "en-MY",
            "author": _ORG, "publisher": _ORG,
            "mainEntityOfPage": {"@id": theme.PROD_URL + f"/case-studies/{c['slug']}/#page"},
            "image": theme.PROD_URL + theme.OG_IMAGES["home"][0]}

HAND_PAGES = [
    {"file": f"{REPO}/index.html", "path": "/", "contact_band": False, "image": "home",
     "title": _HOME_TITLE, "desc": _HOME_DESC, "name": "Mereka AI Lab",
     "extra": [
        # the two prices Home states on its training cards
        _service("Corporate AI training", "Corporate and government teams", "3000",
                 "per group of up to 20", theme.PROD_URL + "/corporate-training/"),
        _service("Public AI training", "Professionals and small teams", "300",
                 "per participant", theme.PROD_URL + "/public-training/"),
        {"@type": "ItemList", "name": "Mereka AI Lab", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "AI Lab Corporate Training",
             "url": theme.PROD_URL + "/corporate-training/"},
            {"@type": "ListItem", "position": 2, "name": "AI Lab Public Training",
             "url": theme.PROD_URL + "/public-training/"},
            {"@type": "ListItem", "position": 3, "name": "AI Prompt Library",
             "url": theme.PROD_URL + "/prompts/"}]}]},
    {"file": f"{REPO}/corporate-training/index.html", "path": "/corporate-training/",
     "image": "corporate", "title": _CORP_TITLE, "desc": _CORP_DESC,
     "name": "AI Lab Corporate Training",
     "extra": [_crumbs("AI Lab Corporate Training", "/corporate-training/"),
               _cat.item_list("Mereka AI Lab programmes", _cat.corporate_courses())]},
    {"file": f"{REPO}/public-training/index.html", "path": "/public-training/",
     "image": "public", "title": _PUB_TITLE, "desc": _PUB_DESC,
     "name": "AI Lab Public Training",
     "extra": [_crumbs("AI Lab Public Training", "/public-training/"),
               _cat.item_list("Mereka AI Lab public workshops", _cat.public_courses())]},
    {"file": f"{REPO}/case-studies/index.html", "path": "/case-studies/",
     "image": "home", "title": _CS_TITLE, "desc": _CS_DESC, "name": "AI Case Studies",
     "extra": [_crumbs("AI Case Studies", "/case-studies/")]},
] + [
    {"file": f"{REPO}/case-studies/{_c['slug']}/index.html",
     "path": f"/case-studies/{_c['slug']}/", "image": "home",
     "title": _c["title"], "desc": _c["desc"], "name": _c["headline"],
     "extra": [_case_crumbs(_c), _case_article(_c)]}
    for _c in CASE_STUDIES
]

# nginx caches /assets/*.css and *.js for 7 days, so a deploy that only changes
# the shared stylesheet would reach returning visitors a week late. Stamp both
# links with a content hash instead.
import hashlib as _hashlib

def _stamp(rel):
    return rel + "?v=" + _hashlib.sha1(open(f"{REPO}{rel}", "rb").read()).hexdigest()[:8]

_CSS_HREF, _JS_SRC = _stamp("/assets/ailab.css"), _stamp("/assets/ailab.js")

for _pg in HAND_PAGES:
    _f = _pg["file"]
    _inject(_f, "NAV", theme.nav())
    _inject(_f, "FOOT", _FOOTER if _pg.get("contact_band", True) else _FOOTER_NO_BAND)
    # the FAQ rich result is parsed back out of the page's own markup, so the
    # structured data and the visible copy can never disagree
    _txt = open(_f).read()
    _faq = []
    for _m in _re.finditer(r"<details><summary>(.*?)</summary><p>(.*?)</p></details>", _txt, _re.S):
        _q = _html.unescape(_re.sub(r"<[^>]+>", "", _m.group(1))).strip()
        _a = _html.unescape(_re.sub(r"<[^>]+>", "", _m.group(2))).strip()
        if _q and _a:
            _faq.append({"@type": "Question", "name": _q,
                         "acceptedAnswer": {"@type": "Answer", "text": _a}})
    _schema = [
        {"@type": "WebPage", "@id": theme.PROD_URL + _pg["path"] + "#page",
         "url": theme.PROD_URL + _pg["path"], "inLanguage": "en-MY",
         "name": _pg["title"], "description": _pg["desc"],
         "isPartOf": {"@id": theme.PROD_URL + "/#website"},
         "about": {"@id": theme.PROD_URL + "/#organisation"},
         "primaryImageOfPage": {"@type": "ImageObject",
                                "url": theme.PROD_URL + theme.OG_IMAGES[_pg["image"]][0],
                                "width": 1200, "height": 630}},
    ] + _pg["extra"]
    if _faq:
        _schema.append({"@type": "FAQPage", "mainEntity": _faq})
    _inject(_f, "SEO", theme.seo(_pg["title"], _pg["desc"], _pg["path"], _schema,
                                 image=_pg["image"]))
    _t = open(_f).read()
    # the hand-written shells said lang="en"; every generated page says en-MY
    _t2 = _t.replace('<html lang="en">', '<html lang="en-MY">', 1)
    # below-the-fold images load lazily; the first section (the hero) stays eager
    _m = _re.search(r'<main id="top">.*?</section>(.*?)</main>', _t2, _re.S)
    if _m:
        _rest = _re.sub(r'<img(?![^>]*\bloading=)', '<img loading="lazy" decoding="async"', _m.group(1))
        _t2 = _t2[:_m.start(1)] + _rest + _t2[_m.end(1):]
    if _t2 != _t:
        open(_f, "w").write(_t2)
    _t = open(_f).read()
    _t2 = _re.sub(r'(?<=")/assets/ailab\.css(\?v=[0-9a-f]+)?(?=")', _CSS_HREF, _t)
    _t2 = _re.sub(r'(?<=")/assets/ailab\.js(\?v=[0-9a-f]+)?(?=")', _JS_SRC, _t2)
    if _t2 != _t:
        open(_f, "w").write(_t2)
    print(f"{_pg['path']}: header, footer and SEO written ({len(_faq)} FAQ entries)")

# ---- the Prompts section's links must point at pages that exist ----
# assets/ailab.js hand-carries a department card link and a #prompt-<id> anchor
# for every power prompt. Those ids come from data.json, so a re-sync can retire
# one and the card would quietly link to nowhere. Check them on every build.
_deptjs = open(f"{REPO}/assets/ailab.js").read()
_dept_block = _re.search(r"const DEPTS = \[(.*?)\n\];", _deptjs, _re.S)
if not _dept_block:
    raise SystemExit("assets/ailab.js: DEPTS array not found")
_bad = []
for _href in _re.findall(r'href:"(/[a-z-]+/)"', _dept_block.group(1)):
    if not os.path.exists(f"{REPO}{_href}index.html"):
        _bad.append(f"{_href} (no such page)")
for _target in _re.findall(r'"(/[a-z-]+/#prompt-\d+)"', _dept_block.group(1)):
    _page, _frag = _target.split("#")
    if not os.path.exists(f"{REPO}{_page}index.html"):
        _bad.append(f"{_target} (no such page)")
    elif f'id="{_frag}"' not in open(f"{REPO}{_page}index.html").read():
        _bad.append(f"{_target} (anchor missing on the page)")
if _bad:
    raise SystemExit("Prompts section links are broken:\n  " + "\n  ".join(_bad))
_n_anchor = len(_re.findall(r'"/[a-z-]+/#prompt-\d+"', _dept_block.group(1)))
_n_card   = len(_re.findall(r'href:"/[a-z-]+/"', _dept_block.group(1)))
print(f"prompts section: {_n_anchor} prompt anchors + {_n_card} card links verified")

# ---- robots.txt + sitemap.xml ----
_paths = ["/", "/corporate-training/", "/public-training/", "/prompts/", "/case-studies/"] \
    + [f"/case-studies/{_c['slug']}/" for _c in CASE_STUDIES] + sorted(f"/{sl}/" for sl in content["roles"])
if theme.IS_PROD:
    _robots = ("User-agent: *\nAllow: /\n\n"
               f"Sitemap: {theme.SITE_URL}/sitemap.xml\n")
else:
    _robots = ("# Preview build — not for indexing.\n"
               "User-agent: *\nDisallow: /\n")
open(f"{REPO}/robots.txt", "w").write(_robots)

# lastmod per URL, from a hash of the page's content rather than the build
# date: rebuilding without changes must not make every page look fresh. The
# hashes and dates persist in sitemap-dates.json, which is committed.
import datetime as _dt
_DATES_F = f"{REPO}/sitemap-dates.json"
_dates = json.load(open(_DATES_F)) if os.path.exists(_DATES_F) else {}
_today = _dt.date.today().isoformat()
def _lastmod(path):
    f = f"{REPO}{path}index.html"
    if not os.path.exists(f):
        return _today
    body = open(f).read()
    # canonical/robots/asset stamps differ between hosts and builds; hash content only
    body = _re.sub(r"<!--SEO-->.*?<!--/SEO-->|\?v=[0-9a-f]+", "", body, flags=_re.S)
    h = _hashlib.sha1(body.encode()).hexdigest()
    if _dates.get(path, {}).get("hash") != h:
        _dates[path] = {"hash": h, "lastmod": _today}
    return _dates[path]["lastmod"]
_urls = "".join(
    f"<url><loc>{theme.SITE_URL}{_p}</loc><lastmod>{_lastmod(_p)}</lastmod><changefreq>monthly</changefreq>"
    f"<priority>{'1.0' if _p == '/' else ('0.9' if _p in ('/corporate-training/', '/public-training/', '/prompts/') else '0.7')}</priority></url>"
    for _p in _paths)
json.dump(_dates, open(_DATES_F, "w"), indent=1, sort_keys=True)
open(f"{REPO}/sitemap.xml", "w").write(
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + _urls + "</urlset>")
print(f"robots.txt ({'ALLOW' if theme.IS_PROD else 'DISALLOW ALL'}) + sitemap.xml ({len(_paths)} urls)")

# ---------------- PROMPTS LIBRARY (AI Cookbooks) ----------------
LIB_CSS = """
/* Hero, laid out as on ailab.mereka.io/prompts/ — full-bleed under the nav,
   rounded only along the bottom, title at 7.51vw over a 960px column, 400px
   search pill with the icon on the right — but in the FOB AI Lab palette: a
   mesh of Anchor Blue and Strategy Teal tints rather than io's pink/purple. */
.chero{position:relative;overflow:hidden;text-align:center;padding:100px 0 116px;border-radius:0 0 80px 80px}
.chero::before{content:'';position:absolute;inset:0;z-index:0;
  background:radial-gradient(58% 78% at 10% 28%,#9fd6d7 0%,rgba(159,214,215,0) 62%),radial-gradient(52% 72% at 88% 22%,#b9c8e4 0%,rgba(185,200,228,0) 64%),radial-gradient(64% 86% at 46% 102%,#d6e7ee 0%,rgba(214,231,238,0) 66%),linear-gradient(135deg,#eaf2f4 0%,#eef1f7 100%)}
.chero-in{position:relative;z-index:1;max-width:1008px;margin:0 auto;padding:0 24px}
.chero h1{font-size:clamp(2.4rem,7.5vw,6.2rem);line-height:1.1;color:var(--ink);margin:0 0 35px}
.chero p{color:var(--ink);font-size:1.25rem;line-height:1.5;margin:0 auto 34px}
.chero .search{max-width:400px;margin:0 auto;display:flex;align-items:center;gap:10px;background:#fff;border-radius:100px;padding:14px 24px}
.chero .search input{border:0;outline:0;width:100%;font-family:inherit;font-size:1rem;background:transparent;color:var(--ink)}
.chero .search .sicon{flex:none;color:#1a1623}
.chero .search .qclear{border:0;background:none;cursor:pointer;color:var(--muted);font-size:1.4rem;line-height:1;padding:0 2px;display:none}
.chero .search .qclear.show{display:block}
@media(max-width:860px){.chero{padding:64px 0 76px;border-radius:0 0 44px 44px}
  .chero p{font-size:1.06rem}}
.res-count{color:var(--muted);font-size:.92rem;margin:0 0 16px;min-height:1.2em}
.sec{padding:54px 0}
.sechead{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:24px}
.sechead h2{font-size:1.9rem}
.feat{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.fcard{border:1px solid var(--line);border-radius:16px;padding:24px;transition:transform .18s var(--ease),box-shadow .18s}
.fcard:hover{transform:translateY(-4px);box-shadow:var(--shadow-sm)}
.fcard h3{font-size:1.06rem;line-height:1.35;margin-bottom:16px;min-height:2.7em}
.tags{display:flex;flex-wrap:wrap;gap:8px}
.tag{background:#e6f2f2;color:#17787a;font-weight:500;font-size:.74rem;padding:5px 12px;border-radius:100px}
.toolbar{display:flex;gap:14px;align-items:center;flex-wrap:wrap;margin-bottom:8px}
.toolbar select,.toolbar .sinput{font-family:inherit;font-size:.94rem;padding:11px 16px;border:1.5px solid var(--line);border-radius:100px;background:#fff;color:var(--ink)}
.toolbar select{cursor:pointer}.toolbar .sp{margin-left:auto}
table.plist{width:100%;border-collapse:collapse}
table.plist td{padding:16px 6px;border-bottom:1px solid var(--line);vertical-align:middle}
table.plist td.nm{font-weight:500}
table.plist td.nm a{display:block;color:var(--ink);transition:color .15s var(--ease)}
table.plist tr:hover td.nm a{color:var(--blue)}
table.plist tr:hover{background:#f3f8f8}
a.fcard{display:block;color:inherit}
table.plist td.tg{text-align:right;white-space:nowrap}
table.plist td.tg .tag{display:inline-block;margin-left:6px;background:transparent;color:#6b7280;padding:2px 0;font-size:.82rem}
.pager{display:flex;gap:8px;justify-content:center;align-items:center;margin-top:30px}
.pager button{min-width:40px;height:40px;border:1px solid var(--line);background:#fff;border-radius:12px;font-family:inherit;font-weight:600;cursor:pointer;color:var(--ink)}
.pager button.on{border-color:var(--ink)}
.pager button:disabled{opacity:.4;cursor:default}
@media(max-width:820px){.feat{grid-template-columns:1fr}}
"""

# featured prompts, in ailab.mereka.io's order — resolved against data.json so
# each card carries the same tags and detail link as the row in the table below
FEATURED_TITLES=[
 "Craft a list of customer communication best practices",
 "Create a formula to calculate the difference between two columns",
 "Clean a user feedback survey spreadsheet",
 "Create a detailed lesson plan for a 5th-grade history class",
 "Add more information to a press release",
]

def catslugs(ids):
    return [CATBYID[cid]["slug"] for cid in ids
            if cid in CATBYID and CATBYID[cid]["slug"]!="uncategorized"]

def href_for(p):
    """Detail link: /<category>#prompt-<id>, as on ailab.mereka.io."""
    if p.get("h"): return p["h"]
    sl=catslugs(p.get("c") or [])
    return f'/{sl[0]}#prompt-{p["id"]}' if sl else ""

def tags_for(p):
    """Real post tags (pr, press-release, …) — never the category name.
    A prompt with no tags shows none, exactly as on io; the category-name
    fallback only applies to a data.json written before sync.py recorded tags."""
    if "g" in p: return p["g"]
    return [slugify(n) for n in (CATBYID[cid]["name"] for cid in (p.get("c") or []) if cid in CATBYID)]

rows=sorted(({"t":p["t"],"h":href_for(p),"g":tags_for(p),"c":catslugs(p.get("c") or [])}
             for p in data["prompts"]), key=lambda x:x["t"].lower())

# category filter: value = slug, label carries the prompt count (as on io)
def _pcount(c):
    n=c.get("prompts")
    if n is None: n=sum(1 for r in rows if c["slug"] in r["c"])
    return n
catopts="".join(
    f'<option value="{esc(c["slug"])}">{esc(c["name"])} ({_pcount(c)})</option>'
    for c in data["categories"] if c["slug"]!="uncategorized" and _pcount(c)>0)

def _tagspans(tg):
    return "".join('<span class="tag">'+esc(x)+'</span>' for x in tg)

BY_TITLE={r["t"].strip().lower():r for r in rows}
featcards=""
for _t in FEATURED_TITLES:
    _r=BY_TITLE.get(_t.strip().lower()) or {"t":_t,"h":"","g":[]}
    _inner=f'<h3>{esc(_r["t"])}</h3><div class="tags">{_tagspans(_r["g"])}</div>'
    featcards+=(f'<a class="fcard" href="{esc(_r["h"])}">{_inner}</a>' if _r["h"]
                else f'<div class="fcard">{_inner}</div>')

LIB_TITLE = f"AI Prompt Library — {len(rows)} Free Prompts | Mereka AI Lab"
LIB_DESC  = theme.clamp(
    f"{len(rows)} tested AI prompts across "
    f"{len([c for c in data['categories'] if c['slug']!='uncategorized'])} business functions: "
    "sales, marketing, HR, operations and more. Filter by department, copy, use today.", 155)
LIB_SCHEMA = [
    {"@type": "CollectionPage",
     "@id": theme.PROD_URL + "/prompts/#page",
     "url": theme.PROD_URL + "/prompts/",
     "name": "AI Prompt Library",
     "description": LIB_DESC,
     "isPartOf": {"@id": theme.PROD_URL + "/#website"},
     "mainEntity": {"@type": "ItemList", "numberOfItems": len(rows),
                    "itemListElement": [{"@type": "ListItem", "position": i, "name": r["t"],
                                         "url": theme.PROD_URL + r["h"]}
                                        for i, r in enumerate(rows[:25], 1)]}},
    {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": theme.PROD_URL + "/"},
        {"@type": "ListItem", "position": 2, "name": "AI Prompts"}]},
]
lib=theme.head(LIB_TITLE, LIB_DESC, "/prompts/", LIB_CSS, LIB_SCHEMA)+theme.nav("prompts")+f'''
<section class="chero"><div class="chero-in">
  <h1>Turn Strategy Into AI-Driven Results With AI Cookbooks</h1>
  <p>Whether you're exploring automation, customer insights, or decision intelligence, these practical guides will show you how AI fits into your business&mdash;step by step, no PhD required.</p>
  <div class="search"><input id="q" type="search" placeholder="Search ..." autocomplete="off"><button id="qclear" class="qclear" type="button" aria-label="Clear search">&times;</button><svg class="sicon" width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M15.5 14h-.79l-.28-.27A6.47 6.47 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5Zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14Z"/></svg></div>
</div></section>

<section class="sec"><div class="shell">
  <div class="sechead"><h2>Featured Prompts</h2><a class="btn btn-dark" href="#all" style="padding:11px 22px">See All Prompts</a></div>
  <div class="feat">{featcards}</div>
</div></section>

<section class="sec" id="all" style="padding-top:0"><div class="shell">
  <h2 style="font-size:1.9rem;margin-bottom:6px">All Prompts</h2>
  <div class="res-count" id="count"></div>
  <div class="toolbar">
    <select id="cat"><option value="">All Categories</option>{catopts}</select>
    <input class="sinput sp" id="q2" type="search" placeholder="Search">
  </div>
  <table class="plist"><tbody id="tb"></tbody></table>
  <div class="pager" id="pager"></div>
</div></section>
{theme.footer()}
<script>
const ROWS={json.dumps(rows,ensure_ascii=False)};
const PER=24;let page=1;
const tb=document.getElementById('tb'),pager=document.getElementById('pager'),cat=document.getElementById('cat'),q2=document.getElementById('q2'),q=document.getElementById('q'),qclear=document.getElementById('qclear'),count=document.getElementById('count'),ALL=document.getElementById('all');
function esc(s){{return s.replace(/[&<>"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));}}
function filtered(){{const term=q.value.trim().toLowerCase(),c=cat.value;
  return ROWS.filter(r=>(!c||r.c.indexOf(c)>-1)&&(!term||r.t.toLowerCase().includes(term)||r.g.some(g=>g.includes(term))));}}
function render(){{const f=filtered();const pages=Math.max(1,Math.ceil(f.length/PER));if(page>pages)page=1;
  const term=q.value.trim();count.textContent=f.length+(f.length===1?' prompt':' prompts')+((term||cat.value)?' found':'')+(term?(' for \u201c'+esc(term)+'\u201d'):'');
  const slice=f.slice((page-1)*PER,page*PER);
  tb.innerHTML=slice.map(r=>`<tr><td class="nm">${{r.h?`<a href="${{esc(r.h)}}">${{esc(r.t)}}</a>`:esc(r.t)}}</td><td class="tg">${{r.g.map(x=>'<span class="tag">'+esc(x)+'</span>').join('')}}</td></tr>`).join('')||'<tr><td colspan="2" style="color:var(--muted);padding:40px 6px">No prompts found. Try a different keyword.</td></tr>';
  let btns='<button '+(page===1?'disabled':'')+' onclick="go(page-1)">&larr;</button>';
  let gap=false;
  for(let i=1;i<=pages;i++){{
    if(i<=3||i===pages||Math.abs(i-page)<=1){{btns+=`<button class="${{i===page?'on':''}}" onclick="go(${{i}})">${{i}}</button>`;gap=false;}}
    else if(!gap){{btns+='<span style="padding:0 4px">…</span>';gap=true;}}
  }}
  btns+='<button '+(page===pages?'disabled':'')+' onclick="go(page+1)">&rarr;</button>';
  pager.innerHTML=pages>1?btns:'';}}
function go(p){{page=p;render();window.scrollTo({{top:document.getElementById('all').offsetTop-90,behavior:'smooth'}});}}
function apply(val,fromHero){{q.value=val;q2.value=val;qclear.classList.toggle('show',!!val);page=1;render();if(fromHero&&val){{ALL.scrollIntoView({{behavior:'smooth',block:'start'}});}}}}
q.addEventListener('input',e=>apply(e.target.value,true));
q2.addEventListener('input',e=>apply(e.target.value,false));
q.addEventListener('keydown',e=>{{if(e.key==='Enter'){{e.preventDefault();if(q.value)ALL.scrollIntoView({{behavior:'smooth',block:'start'}});}}}});
cat.addEventListener('change',()=>{{page=1;render();}});
qclear.addEventListener('click',()=>{{apply('',false);q.focus();}});
render();
</script>
</body></html>'''
open(f"{REPO}/prompts/index.html","w").write(lib)
print("prompts/index.html (Cookbooks):", len(lib), "bytes,", len(rows), "table rows")
