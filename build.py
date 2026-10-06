#!/usr/bin/env python3
"""Generate ailab.mereka.dev pages 1-to-1 with ailab.mereka.io:
   /prompts/ (AI Cookbooks) and /{category}/ role pages. Uses data.json + content.json + theme.py."""
import json, os, html, sys, re, unicodedata
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
    page=theme.head(f'{r["title"]} — AI Labs', r["subtitle"] or r["title"],
                    f'https://ailab.mereka.dev/{slug}/', ROLE_CSS) + theme.nav("prompts") + f'''
<section class="rhero"><div class="rhero-in">
  <a class="back" href="/prompts/"><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M15.41 16.59 10.83 12l4.58-4.59L14 6l-6 6 6 6 1.41-1.41Z"/></svg>Back to Prompts</a>
  <h1>{esc(r["title"])}</h1>
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

# ---------------- keep the homepage's header in sync ----------------
# index.html is hand-written and carries its own copy of the header; it has
# drifted from theme.nav() twice. Inject the generated markup and mega-menu CSS
# so there is only one source of truth.
import re as _re
_home_path = f"{REPO}/index.html"
_home = open(_home_path).read()
_before = _home
_home = _re.sub(r"<!--NAV-->.*?<!--/NAV-->",
                lambda _m: "<!--NAV-->" + theme.nav() + "<!--/NAV-->", _home, flags=_re.S)
_home = _re.sub(r"/\*NAV-CSS\*/.*?/\*/NAV-CSS\*/",
                lambda _m: "/*NAV-CSS*/" + theme.MENU_CSS + "/*/NAV-CSS*/", _home, flags=_re.S)
if "<!--NAV-->" not in _home or "/*NAV-CSS*/" not in _home:
    raise SystemExit("index.html is missing its <!--NAV--> / /*NAV-CSS*/ markers")
open(_home_path, "w").write(_home)
print("index.html: header", "updated" if _home != _before else "already current")

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

lib=theme.head("AI Prompts — AI Labs","Whether you're exploring automation, customer insights, or decision intelligence, these practical guides show you how AI fits into your business.","https://ailab.mereka.dev/prompts/",LIB_CSS)+theme.nav("prompts")+f'''
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
