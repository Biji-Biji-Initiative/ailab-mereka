#!/usr/bin/env python3
"""Generate ailab.mereka.dev pages 1-to-1 with ailab.mereka.io:
   /prompts/ (AI Cookbooks) and /{category}/ role pages. Uses data.json + content.json + theme.py."""
import json, os, html, sys, re
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
.rhero{padding:26px 0 10px}
.rhero .blob{position:relative;border-radius:26px;padding:56px 40px 60px;text-align:center;overflow:hidden;
  background:linear-gradient(118deg,#f7bfe6 0%,#c8ccff 42%,#a7ecef 100%)}
.rhero .back{position:absolute;top:22px;left:26px;font-weight:600;font-size:.92rem;color:#3a2f52;display:inline-flex;gap:6px;align-items:center}
.rhero h1{font-size:clamp(2.2rem,5vw,3.6rem);color:#1a1623;margin:6px auto 14px;max-width:16ch}
.rhero p{color:#43405a;font-size:1.06rem;max-width:60ch;margin:0 auto}
.onthis{position:sticky;top:78px;z-index:40;background:#fff;border-bottom:1px solid var(--line);padding:12px 0}
.onthis details{max-width:var(--maxw);margin:0 auto;padding:0 28px}
.onthis summary{font-weight:600;cursor:pointer;list-style:none;display:inline-flex;gap:8px;align-items:center;border:1px solid var(--line);border-radius:100px;padding:9px 18px}
.onthis summary::-webkit-details-marker{display:none}
.onthis ul{list-style:none;display:flex;flex-wrap:wrap;gap:8px 22px;padding:14px 2px 4px;margin:0}
.onthis a{color:var(--muted);font-size:.92rem}.onthis a:hover{color:var(--pink)}
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

def role_page(slug, r):
    groups=r["groups"]
    toc="".join(f'<li><a href="#{slugify(g["usecase"])}">{esc(g["usecase"])}</a></li>' for g in groups if g["usecase"])
    body=""
    for i,g in enumerate(groups,1):
        gid=slugify(g["usecase"]) or f"uc{i}"
        prompts=""
        for p in g["prompts"]:
            name=f'<div class="pname">{esc(p["name"])}</div>' if p.get("name") else ""
            b=esc(p["body"])
            prompts+=f'''<div class="prompt">{name}<div class="pbox"><button class="copy" aria-label="Copy" onclick="cp(this)"data-t="{esc(p["body"])}">{COPY_SVG}</button>{b}</div></div>'''
        body+=f'''<section class="uc" id="{gid}"><div class="shell">
  <div class="lbl">Use Case {i}</div>
  <h2>{esc(g["usecase"])}</h2>
  {prompts}
</div></section>'''
    page=theme.head(f'{r["title"]} — AI Labs', r["subtitle"] or r["title"],
                    f'https://ailab.mereka.dev/{slug}/', ROLE_CSS) + theme.nav() + f'''
<section class="rhero"><div class="shell"><div class="blob">
  <a class="back" href="/prompts/">&larr; Back to Prompts</a>
  <h1>{esc(r["title"])}</h1>
  <p>{esc(r["subtitle"])}</p>
</div></div></section>
<div class="onthis"><details><summary>On this page &#9662;</summary><ul>{toc}</ul></details></div>
{body}
<div class="shell rfoot-cta"><a class="btn btn-accent" href="/prompts/">Browse all prompts &rarr;</a></div>
{theme.footer()}
<script>function cp(b){{navigator.clipboard.writeText(b.dataset.t).then(()=>{{b.classList.add('done');var s=b.innerHTML;b.textContent='✓';setTimeout(()=>{{b.classList.remove('done');b.innerHTML=s;}},1300);}});}}</script>
</body></html>'''
    os.makedirs(f"{REPO}/{slug}", exist_ok=True)
    open(f"{REPO}/{slug}/index.html","w").write(page)
    return sum(len(g["prompts"]) for g in groups)

total=0
for slug,r in content["roles"].items():
    total+=role_page(slug,r)
print(f"role pages: {len(content['roles'])}, prompts rendered: {total}")

# ---------------- PROMPTS LIBRARY (AI Cookbooks) ----------------
LIB_CSS = """
.chero{padding:30px 0 8px}
.chero .blob{border-radius:26px;padding:60px 30px 66px;text-align:center;background:linear-gradient(118deg,#f7bfe6 0%,#c8ccff 42%,#a7ecef 100%)}
.chero h1{font-size:clamp(2.3rem,5.4vw,4rem);color:#1a1623;max-width:18ch;margin:0 auto 16px}
.chero p{color:#43405a;font-size:1.06rem;max-width:64ch;margin:0 auto 24px}
.chero .search{max-width:520px;margin:0 auto;display:flex;align-items:center;gap:10px;background:#fff;border-radius:100px;padding:13px 22px;box-shadow:var(--shadow-sm)}
.chero .search input{border:0;outline:0;width:100%;font-family:inherit;font-size:1rem;background:transparent;color:var(--ink)}
.chero .search .qclear{border:0;background:none;cursor:pointer;color:var(--blue);font-size:1.4rem;line-height:1;padding:0 2px;display:none}
.chero .search .qclear.show{display:block}
.res-count{color:var(--muted);font-size:.92rem;margin:0 0 16px;min-height:1.2em}
.sec{padding:54px 0}
.sechead{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:24px}
.sechead h2{font-size:1.9rem}
.feat{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.fcard{border:1px solid var(--line);border-radius:16px;padding:24px;transition:transform .18s var(--ease),box-shadow .18s}
.fcard:hover{transform:translateY(-4px);box-shadow:var(--shadow-sm)}
.fcard h3{font-size:1.06rem;line-height:1.35;margin-bottom:16px;min-height:2.7em}
.tags{display:flex;flex-wrap:wrap;gap:8px}
.tag{background:#eef0ff;color:#4f5bd0;font-weight:500;font-size:.74rem;padding:5px 12px;border-radius:100px}
.toolbar{display:flex;gap:14px;align-items:center;flex-wrap:wrap;margin-bottom:8px}
.toolbar select,.toolbar .sinput{font-family:inherit;font-size:.94rem;padding:11px 16px;border:1.5px solid var(--line);border-radius:100px;background:#fff;color:var(--ink)}
.toolbar select{cursor:pointer}.toolbar .sp{margin-left:auto}
table.plist{width:100%;border-collapse:collapse}
table.plist td{padding:16px 6px;border-bottom:1px solid var(--line);vertical-align:middle}
table.plist td.nm{font-weight:500}
table.plist td.tg{text-align:right;white-space:nowrap}
table.plist td.tg .tag{display:inline-block;margin-left:6px;background:transparent;color:#7b7f8c;padding:2px 0;font-size:.82rem}
.pager{display:flex;gap:8px;justify-content:center;align-items:center;margin-top:30px}
.pager button{min-width:40px;height:40px;border:1px solid var(--line);background:#fff;border-radius:12px;font-family:inherit;font-weight:600;cursor:pointer;color:var(--ink)}
.pager button.on{border-color:var(--ink)}
.pager button:disabled{opacity:.4;cursor:default}
@media(max-width:820px){.feat{grid-template-columns:1fr}}
"""

# featured (as on ailab.mereka.io)
FEATURED=[
 ("Craft a list of customer communication best practices",["hiring","customer-support"]),
 ("Create a formula to calculate the difference between two columns",["formula","audit"]),
 ("Clean a user feedback survey spreadsheet",["survey","data-cleaning"]),
 ("Add more information to a press release",["pr","press-release"]),
 ("Create a detailed lesson plan for a 5th-grade history class",["learning"]),
]
# table rows: all prompts, tag = category name(s)
def tagsfor(ids):
    out=[]
    for cid in ids:
        c=CATBYID.get(cid)
        if c and c["slug"]!="uncategorized": out.append(c["name"])
    return out
rows=sorted(({"t":p["t"],"tags":tagsfor(p["c"])} for p in data["prompts"]), key=lambda x:x["t"].lower())
catopts="".join(f'<option value="{esc(c["name"])}">{esc(c["name"])}</option>' for c in data["categories"] if c["count"]>0 and c["slug"]!="uncategorized")
def _tagspans(tg):
    return "".join('<span class="tag">'+esc(x)+'</span>' for x in tg)
featcards="".join('<div class="fcard"><h3>'+esc(t)+'</h3><div class="tags">'+_tagspans(tg)+'</div></div>' for t,tg in FEATURED)

lib=theme.head("AI Prompts — AI Labs","Whether you're exploring automation, customer insights, or decision intelligence, these practical guides show you how AI fits into your business.","https://ailab.mereka.dev/prompts/",LIB_CSS)+theme.nav()+f'''
<section class="chero"><div class="shell"><div class="blob">
  <h1>Turn Strategy Into AI-Driven Results With AI Cookbooks</h1>
  <p>Whether you're exploring automation, customer insights, or decision intelligence, these practical guides will show you how AI fits into your business&mdash;step by step, no PhD required.</p>
  <div class="search"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#8a8fa0" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><input id="q" type="search" placeholder="Search prompts by keyword..." autocomplete="off"><button id="qclear" class="qclear" type="button" aria-label="Clear search">&times;</button></div>
</div></div></section>

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
  return ROWS.filter(r=>(!c||r.tags.includes(c))&&(!term||r.t.toLowerCase().includes(term)));}}
function render(){{const f=filtered();const pages=Math.max(1,Math.ceil(f.length/PER));if(page>pages)page=1;
  const term=q.value.trim();count.textContent=f.length+(f.length===1?' prompt':' prompts')+((term||cat.value)?' found':'')+(term?(' for \u201c'+esc(term)+'\u201d'):'');
  const slice=f.slice((page-1)*PER,page*PER);
  tb.innerHTML=slice.map(r=>`<tr><td class="nm">${{esc(r.t)}}</td><td class="tg">${{r.tags.map(x=>'<span class="tag">'+esc(x.toLowerCase().replace(/ & /g,' ').replace(/\\s+/g,'-'))+'</span>').join('')}}</td></tr>`).join('')||'<tr><td colspan="2" style="color:var(--muted);padding:40px 6px">No prompts found. Try a different keyword.</td></tr>';
  let btns='<button '+(page===1?'disabled':'')+' onclick="go(page-1)">&larr;</button>';
  for(let i=1;i<=pages;i++){{if(i<=3||i===pages||Math.abs(i-page)<=1){{btns+=`<button class="${{i===page?'on':''}}" onclick="go(${{i}})">${{i}}</button>`;}}else if(i===4||i===pages-1){{btns+='<span style="padding:0 4px">…</span>';}}}}
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
