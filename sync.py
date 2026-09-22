#!/usr/bin/env python3
"""
sync.py — pull all content from the live WordPress REST API at ailab.mereka.io
and regenerate the static clone (data.json + /prompts/ + /department/*).
No credentials needed for published content. Run:  python3 sync.py
Then commit & push; Coolify redeploys automatically (or trigger via API).
"""
import urllib.request, urllib.parse, json, os, html as _html

SRC = os.environ.get("WP_SRC", "https://ailab.mereka.io/wp-json/wp/v2/")
REPO = os.path.dirname(os.path.abspath(__file__))

def _get(path):
    req = urllib.request.Request(SRC + path, headers={"User-Agent": "ailab-sync"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r), r.headers

def _all(pt, fields):
    out, page = [], 1
    while True:
        d, h = _get(f"{pt}?per_page=100&page={page}&_fields={fields}&orderby=title&order=asc")
        out += d
        tp = int(h.get("X-WP-TotalPages", "1"))
        if page >= tp: break
        page += 1
    return out

def _dec(s):
    if not s: return ""
    import html as H
    return H.unescape(s)

print("Fetching from", SRC)
cats_raw = _get("categories?per_page=100&_fields=id,name,slug,count")[0]
prompts_raw = _all("prompt", "id,slug,title,categories")
uc_raw = _all("use-case", "id,slug,title,categories")
deps_raw = _get("department?per_page=100&orderby=title&order=asc")[0]

data = {
  "categories": sorted([{"id":c["id"],"name":_dec(c["name"]),"slug":c["slug"],"count":c["count"]} for c in cats_raw], key=lambda x:x["name"].lower()),
  "departments": [{
      "slug": d["slug"], "title": _dec(d["title"]["rendered"]),
      "desc": _dec((d.get("acf") or {}).get("department_description","")),
      "roles": _dec((d.get("acf") or {}).get("department_roles","")),
      "uc": [ (x.get("ID") or x.get("id")) if isinstance(x,dict) else x for x in ((d.get("acf") or {}).get("department_use-cases") or []) ],
      "pr": [ (x.get("ID") or x.get("id")) if isinstance(x,dict) else x for x in ((d.get("acf") or {}).get("department_prompts") or []) ],
  } for d in deps_raw],
  "prompts": [{"id":p["id"],"t":_dec(p["title"]["rendered"]),"c":p.get("categories") or []} for p in prompts_raw],
  "usecases": [{"id":u["id"],"t":_dec(u["title"]["rendered"]),"c":u.get("categories") or []} for u in uc_raw],
}
json.dump(data, open(f"{REPO}/data.json","w"), ensure_ascii=False, indent=0)
print(f"data.json: {len(data['categories'])} cats, {len(data['departments'])} depts, {len(data['prompts'])} prompts, {len(data['usecases'])} use-cases")

# ---- generation (shared with gen.py) ----
cats={c["id"]:c for c in data["categories"]}
prompts={p["id"]:p for p in data["prompts"]}
usecases={u["id"]:u for u in data["usecases"]}
deps=data["departments"]
import html
idx=open(f"{REPO}/index.html").read().splitlines()
style="\n".join(idx[17:187])  # includes <style> ... </style>

FONTS='''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">'''

FAV='<link rel="icon" href="https://ailab.mereka.io/wp-content/uploads/sites/9/2025/11/favicon_256x256.png" />'

def nav(prefix=""):
    return f'''<header class="nav">
  <div class="shell nav-inner">
    <a class="nav-logo" href="{prefix}/" aria-label="AI Labs home"><img src="https://ailab.mereka.io/wp-content/uploads/sites/9/2025/11/mereka-logo.svg" alt="AI Labs"></a>
    <button class="burger" aria-label="Menu" onclick="document.getElementById('nav').classList.toggle('open')"><span></span><span></span><span></span></button>
    <nav class="nav-links" id="nav">
      <a href="{prefix}/#departments">Departments</a>
      <a href="{prefix}/prompts/">Prompt Library</a>
      <a href="{prefix}/#programmes">Programmes</a>
      <a href="{prefix}/#portfolio">Impact</a>
      <a class="btn btn-primary nav-cta" href="{prefix}/#contact">Get In Touch</a>
    </nav>
  </div>
</header>'''

FOOTER='''<footer>
  <div class="shell">
    <div class="foot-top">
      <div>
        <div class="foot-logo"><img src="https://ailab.mereka.io/wp-content/uploads/sites/9/2025/11/mereka-logo.svg" alt="AI Labs"></div>
        <p style="max-width:34ch">We upskill &amp; empower companies to boost productivity with AI.</p>
        <div class="foot-social">
          <a href="https://www.tiktok.com/@mereka.io" target="_blank" rel="noopener">TT</a>
          <a href="https://www.instagram.com/mereka.io/" target="_blank" rel="noopener">IG</a>
          <a href="https://www.facebook.com/mereka.io" target="_blank" rel="noopener">FB</a>
          <a href="https://www.linkedin.com/company/mereka-io" target="_blank" rel="noopener">IN</a>
          <a href="https://www.youtube.com/channel/UCGJ5RzyL0oib2ONP2gPvOYA" target="_blank" rel="noopener">YT</a>
        </div>
      </div>
      <div><h5>Company</h5><ul>
        <li><a href="https://corporate.mereka.io/about-us" target="_blank" rel="noopener">About</a></li>
        <li><a href="https://corporate.mereka.io/portfolio" target="_blank" rel="noopener">Portfolio</a></li>
        <li><a href="https://corporate.mereka.io/our-team" target="_blank" rel="noopener">Team</a></li>
        <li><a href="https://corporate.mereka.io/blog" target="_blank" rel="noopener">Blog</a></li>
      </ul></div>
      <div><h5>Academy</h5><ul>
        <li><a href="https://corporate.mereka.io/academy/future-of-work" target="_blank" rel="noopener">Future of Work</a></li>
        <li><a href="https://corporate.mereka.io/academy/all-courses" target="_blank" rel="noopener">All Courses</a></li>
        <li><a href="https://corporate.mereka.io/academy/makerspace" target="_blank" rel="noopener">Build a Makerspace</a></li>
      </ul></div>
      <div><h5>Marketplace</h5><ul>
        <li><a href="https://mereka.io/experiences" target="_blank" rel="noopener">Experiences</a></li>
        <li><a href="https://mereka.io/hubs" target="_blank" rel="noopener">Hubs</a></li>
        <li><a href="https://mereka.io/jobs" target="_blank" rel="noopener">Jobs</a></li>
      </ul></div>
    </div>
    <div class="foot-bottom">
      <span>&copy; 2026 Mereka</span>
      <span>
        <a href="https://legal.mereka.io/" target="_blank" rel="noopener">Terms of Use</a>
        <a href="https://legal.mereka.io/privacy-policy/" target="_blank" rel="noopener">Privacy Policy</a>
      </span>
    </div>
  </div>
</footer>'''

PAGECSS='''<style>
.page-hero{background:linear-gradient(180deg,#fff, var(--grey));padding:60px 0 42px;border-bottom:1px solid var(--border)}
.crumb{font-family:Poppins;font-weight:500;font-size:.85rem;color:var(--muted);margin-bottom:14px}
.crumb a{color:var(--teal)}
.page-hero h1{font-size:clamp(2rem,4.4vw,3rem)}
.toolbar{position:sticky;top:74px;z-index:30;background:rgba(255,255,255,.92);backdrop-filter:blur(10px);border-bottom:1px solid var(--border);padding:16px 0}
.toolbar-inner{display:flex;gap:12px;flex-wrap:wrap;align-items:center}
.search{flex:1;min-width:220px;display:flex;align-items:center;gap:10px;background:#fff;border:1.5px solid var(--border);border-radius:999px;padding:11px 18px}
.search input{border:none;outline:none;font-family:Inter;font-size:1rem;width:100%;background:transparent;color:var(--ink)}
.selectwrap select{font-family:Poppins;font-weight:500;font-size:.92rem;padding:11px 16px;border:1.5px solid var(--border);border-radius:999px;background:#fff;color:var(--ink);cursor:pointer}
.seg{display:inline-flex;background:var(--grey);border-radius:999px;padding:4px}
.seg button{font-family:Poppins;font-weight:600;font-size:.86rem;border:none;background:none;padding:8px 16px;border-radius:999px;cursor:pointer;color:var(--muted)}
.seg button.on{background:#fff;color:var(--anchor);box-shadow:var(--shadow-sm)}
.count-line{font-family:Poppins;font-weight:500;color:var(--muted);font-size:.9rem;margin:22px 0 16px}
.card-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}
.pcard{background:#fff;border:1px solid var(--border);border-radius:var(--radius-sm);padding:18px 18px 16px;display:flex;flex-direction:column;gap:12px;transition:transform .18s var(--ease),box-shadow .18s,border-color .18s}
.pcard:hover{transform:translateY(-3px);box-shadow:var(--shadow-sm);border-color:rgba(31,163,166,.4)}
.pcard .ttl{font-family:Poppins;font-weight:600;font-size:1rem;line-height:1.32;color:var(--ink)}
.pcard .meta{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:auto}
.tag{font-family:Poppins;font-weight:600;font-size:.68rem;letter-spacing:.04em;text-transform:uppercase;padding:5px 10px;border-radius:999px}
.tag.prompt{background:rgba(31,163,166,.12);color:var(--teal-600)}
.tag.usecase{background:rgba(31,63,124,.1);color:var(--anchor)}
.tag.cat{background:var(--grey);color:var(--muted)}
.copybtn{margin-left:auto;font-family:Poppins;font-weight:600;font-size:.78rem;border:1.5px solid var(--border);background:#fff;border-radius:999px;padding:7px 14px;cursor:pointer;color:var(--anchor);transition:background .15s,border-color .15s}
.copybtn:hover{background:rgba(31,63,124,.06)}
.copybtn.done{background:var(--teal);color:#fff;border-color:var(--teal)}
.empty{padding:60px 0;text-align:center;color:var(--muted);font-family:Poppins}
.dept-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin-top:8px}
.dept-tile{display:block;background:#fff;border:1px solid var(--border);border-radius:var(--radius-sm);padding:22px;transition:transform .18s var(--ease),box-shadow .18s}
.dept-tile:hover{transform:translateY(-4px);box-shadow:var(--shadow-sm)}
.dept-tile h3{font-size:1.12rem;margin-bottom:8px}
.dept-tile p{color:var(--muted);font-size:.92rem;margin:0}
.dept-tile .n{font-family:Poppins;font-weight:600;color:var(--teal);font-size:.82rem;margin-top:12px}
.roles-chip{display:inline-block;background:rgba(255,255,255,.16);color:#fff;font-family:Poppins;font-weight:500;font-size:.82rem;padding:7px 14px;border-radius:999px;margin:4px 6px 0 0}
.dh{background:var(--anchor);color:#fff;padding:64px 0 56px}
.dh .eyebrow{color:#8fd6d8}
.dh h1{font-size:clamp(2rem,4.6vw,3.2rem);margin:10px 0 14px;color:#fff}
.dh p.lead{color:rgba(255,255,255,.85);max-width:64ch}
.sub-tabs{display:inline-flex;background:var(--grey);border-radius:999px;padding:5px;margin-bottom:26px}
.sub-tabs button{font-family:Poppins;font-weight:600;font-size:.9rem;border:none;background:none;padding:10px 20px;border-radius:999px;cursor:pointer;color:var(--muted)}
.sub-tabs button.on{background:#fff;color:var(--anchor);box-shadow:var(--shadow-sm)}
.list-col{columns:2;column-gap:16px}
@media(max-width:720px){.list-col{columns:1}}
.li{break-inside:avoid;background:#fff;border:1px solid var(--border);border-radius:var(--radius-sm);padding:14px 16px;margin-bottom:12px;display:flex;gap:12px;align-items:flex-start}
.li .ic{flex:0 0 auto;width:26px;height:26px;border-radius:8px;background:rgba(31,163,166,.12);color:var(--teal-600);display:flex;align-items:center;justify-content:center;font-weight:700;font-family:Poppins;font-size:.85rem}
.li.uc .ic{background:rgba(31,63,124,.1);color:var(--anchor)}
.li span{font-family:Inter;font-size:.96rem;line-height:1.4;color:var(--ink)}
</style>'''

def head(title, desc, canonical, pagecss=True):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}" />
<link rel="canonical" href="{canonical}" />
<meta property="og:type" content="website" />
<meta property="og:title" content="{html.escape(title)}" />
<meta property="og:description" content="{html.escape(desc)}" />
<meta property="og:url" content="{canonical}" />
{FAV}
{FONTS}
{style}
{PAGECSS if pagecss else ''}
</head>
<body id="top">'''


# ---------- build combined items for prompt library ----------
def catname(ids):
    for i in ids:
        if i in cats: return cats[i]["name"]
    return "General"
items=[]
for p in data["prompts"]:
    items.append({"t":p["t"],"k":"prompt","c":catname(p["c"])})
for u in data["usecases"]:
    items.append({"t":u["t"],"k":"usecase","c":catname(u["c"])})
items.sort(key=lambda x:x["t"].lower())
# category options (names present), sorted
present=sorted({it["c"] for it in items})

dept_tiles=""
for d in deps:
    dept_tiles+=f'''<a class="dept-tile" href="/department/{d['slug']}/">
      <h3>{html.escape(d['title'])}</h3>
      <p>{html.escape(d['desc'])}</p>
      <div class="n">{len(d['uc'])} use cases &middot; {len(d['pr'])} prompts &rarr;</div>
    </a>'''

opts="".join(f'<option value="{html.escape(c)}">{html.escape(c)}</option>' for c in present)

prompts_html = head(
  "AI Prompt Library — Mereka AI Labs",
  f"Browse {len(data['prompts'])} ready-to-use AI prompts and {len(data['usecases'])} use cases across every department. Filter by team and category.",
  "https://ailab.mereka.dev/prompts/") + nav() + f'''
<section class="page-hero"><div class="shell">
  <div class="crumb"><a href="/">Home</a> / Prompt Library</div>
  <span class="eyebrow">Prompt Library</span>
  <h1>{len(data['prompts'])} AI prompts &amp; {len(data['usecases'])} use cases</h1>
  <p class="lead">Battle-tested prompts and real-world AI use cases your team can put to work today &mdash; organised by department and category.</p>
  <div class="dept-grid">{dept_tiles}</div>
</div></section>

<div class="toolbar"><div class="shell toolbar-inner">
  <label class="search"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5a5f6b" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
    <input id="q" type="search" placeholder="Search prompts and use cases..." autocomplete="off"></label>
  <div class="selectwrap"><select id="cat"><option value="">All categories</option>{opts}</select></div>
  <div class="seg" id="seg">
    <button data-k="" class="on">All</button>
    <button data-k="prompt">Prompts</button>
    <button data-k="usecase">Use cases</button>
  </div>
</div></div>

<section class="section" style="padding-top:28px"><div class="shell">
  <div class="count-line" id="count"></div>
  <div class="card-grid" id="grid"></div>
  <div class="empty" id="empty" style="display:none">No results. Try a different search or filter.</div>
</div></section>
{FOOTER}
<script>
const DATA={json.dumps(items,ensure_ascii=False)};
const grid=document.getElementById('grid'),q=document.getElementById('q'),cat=document.getElementById('cat'),count=document.getElementById('count'),empty=document.getElementById('empty');
let kind="";
document.getElementById('seg').addEventListener('click',e=>{{const b=e.target.closest('button');if(!b)return;[...b.parentNode.children].forEach(x=>x.classList.remove('on'));b.classList.add('on');kind=b.dataset.k;render();}});
function esc(s){{return s.replace(/[&<>"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));}}
function render(){{
  const term=q.value.trim().toLowerCase(),c=cat.value;
  const out=DATA.filter(d=>(!kind||d.k===kind)&&(!c||d.c===c)&&(!term||d.t.toLowerCase().includes(term)));
  count.textContent=out.length+" result"+(out.length===1?"":"s");
  empty.style.display=out.length?"none":"block";
  grid.innerHTML=out.slice(0,600).map(d=>`<div class="pcard"><div class="ttl">${{esc(d.t)}}</div><div class="meta"><span class="tag ${{d.k}}">${{d.k==='prompt'?'Prompt':'Use case'}}</span><span class="tag cat">${{esc(d.c)}}</span>${{d.k==='prompt'?`<button class="copybtn" onclick="cp(this)" data-t="${{esc(d.t)}}">Copy</button>`:''}}</div></div>`).join('');
}}
function cp(b){{navigator.clipboard.writeText(b.dataset.t).then(()=>{{b.textContent='Copied';b.classList.add('done');setTimeout(()=>{{b.textContent='Copy';b.classList.remove('done');}},1400);}});}}
q.addEventListener('input',render);cat.addEventListener('change',render);render();
</script>
</body></html>'''
os.makedirs(f"{REPO}/prompts",exist_ok=True)
open(f"{REPO}/prompts/index.html","w").write(prompts_html)
print("wrote prompts/index.html", len(prompts_html))

# ---------- department pages ----------
def resolve(ids, table):
    out=[]
    for i in ids:
        r=table.get(i)
        if r: out.append(r["t"])
    # unique preserve order
    seen=set(); u=[]
    for t in out:
        if t not in seen: seen.add(t); u.append(t)
    return sorted(u, key=str.lower)

for d in deps:
    uc=resolve(d["uc"], usecases)
    pr=resolve(d["pr"], prompts)
    roles=[r.strip() for r in d["roles"].split(",") if r.strip()]
    roles_html="".join(f'<span class="roles-chip">{html.escape(r)}</span>' for r in roles)
    uc_html="".join(f'<div class="li uc"><span class="ic">UC</span><span>{html.escape(t)}</span></div>' for t in uc)
    pr_html="".join(f'<div class="li"><span class="ic">P</span><span>{html.escape(t)}</span></div>' for t in pr)
    # other departments for footer nav
    others="".join(f'<a class="dept-tile" href="/department/{o["slug"]}/"><h3>{html.escape(o["title"])}</h3><p>{html.escape(o["desc"])}</p><div class="n">{len(o["uc"])} use cases &middot; {len(o["pr"])} prompts &rarr;</div></a>' for o in deps if o["slug"]!=d["slug"])
    page = head(
      f"{d['title']} — AI Use Cases & Prompts | Mereka AI Labs",
      f"{d['desc']} {len(uc)} AI use cases and {len(pr)} prompts for {d['title']} teams.",
      f"https://ailab.mereka.dev/department/{d['slug']}/") + nav() + f'''
<section class="dh"><div class="shell">
  <div class="crumb" style="color:rgba(255,255,255,.7)"><a href="/" style="color:#8fd6d8">Home</a> / <a href="/prompts/" style="color:#8fd6d8">Prompt Library</a> / {html.escape(d['title'])}</div>
  <span class="eyebrow">Department</span>
  <h1>{html.escape(d['title'])}</h1>
  <p class="lead">{html.escape(d['desc'])}</p>
  <div style="margin-top:18px">{roles_html}</div>
</div></section>

<section class="section" style="padding-top:48px"><div class="shell">
  <div class="sub-tabs" id="st">
    <button data-p="uc" class="on">Use cases ({len(uc)})</button>
    <button data-p="pr">Prompts ({len(pr)})</button>
  </div>
  <div id="pane-uc"><div class="list-col">{uc_html}</div></div>
  <div id="pane-pr" style="display:none"><div class="list-col">{pr_html}</div></div>
  <div style="margin-top:36px"><a class="btn btn-primary" href="/prompts/">Browse the full prompt library &rarr;</a></div>
</div></section>

<section class="section section--grey"><div class="shell">
  <span class="eyebrow">Explore other teams</span>
  <h2 style="font-size:1.7rem;margin:8px 0 22px">More departments</h2>
  <div class="dept-grid">{others}</div>
</div></section>
{FOOTER}
<script>
document.getElementById('st').addEventListener('click',e=>{{const b=e.target.closest('button');if(!b)return;[...b.parentNode.children].forEach(x=>x.classList.remove('on'));b.classList.add('on');
document.getElementById('pane-uc').style.display=b.dataset.p==='uc'?'block':'none';
document.getElementById('pane-pr').style.display=b.dataset.p==='pr'?'block':'none';}});
</script>
</body></html>'''
    os.makedirs(f"{REPO}/department/{d['slug']}",exist_ok=True)
    open(f"{REPO}/department/{d['slug']}/index.html","w").write(page)
    print("wrote department/"+d['slug'], len(uc),"uc",len(pr),"pr", len(page),"bytes")
