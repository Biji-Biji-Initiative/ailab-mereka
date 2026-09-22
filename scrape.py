#!/usr/bin/env python3
"""Scrape ailab.mereka.io category (role) pages + prompt library into content.json.
Captures full prompt bodies (data-prompt-content), use-case grouping, subtitles."""
import urllib.request, re, html as H, json, os, time

REPO=os.path.dirname(os.path.abspath(__file__))
BASE="https://ailab.mereka.io"
UA={"User-Agent":"Mozilla/5.0 ailab-sync"}

def get(u):
    for _ in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=40).read().decode("utf-8","ignore")
        except Exception as e:
            time.sleep(2)
    raise RuntimeError("fetch failed "+u)

def strip(s): return H.unescape(re.sub("<[^>]+>","",s or "")).strip()

def content_region(h):
    s=h.find('id="brx-content"'); e=h.find('id="brx-footer"')
    return h[s:e] if s>0 and e>0 else h

def parse_role(slug):
    h=get(f"{BASE}/{slug}/")
    body=content_region(h)
    # subtitle: og:description or the hero sub text (between hero title and first h2)
    # tokens in order: h1/h2/h3 + prompt bodies + generic text blocks
    tok_re=re.compile(
        r'<(h1|h2|h3)[^>]*>(?P<ht>.*?)</\1>'
        r'|data-prompt-content[^>]*>(?P<pc>.*?)</div>'
        r'|<p[^>]*class="[^"]*hero__sub[^"]*"[^>]*>(?P<sub>.*?)</p>', re.S)
    title=None; subtitle=""; groups=[]; cur=None; last_h3=None
    for m in tok_re.finditer(body):
        if m.group(1):
            t=strip(m.group('ht'))
            if not t: continue
            tag=m.group(1)
            if tag=='h1' and not title: title=t
            elif tag=='h2':
                cur={"usecase":t,"prompts":[]}; groups.append(cur); last_h3=None
            elif tag=='h3':
                last_h3={"name":t,"body":""}
                if cur is None:
                    cur={"usecase":"","prompts":[]}; groups.append(cur)
                cur["prompts"].append(last_h3)
        elif m.group('pc') is not None:
            b=strip(m.group('pc'))
            if last_h3 is not None and not last_h3["body"]:
                last_h3["body"]=b
            elif cur is not None:
                cur["prompts"].append({"name":"","body":b})
        elif m.group('sub') is not None and not subtitle:
            subtitle=strip(m.group('sub'))
    # fallback subtitle from meta description
    if not subtitle:
        md=re.search(r'<meta name="description" content="([^"]*)"',h)
        if md: subtitle=strip(md.group(1))
    return {"slug":slug,"title":title or slug,"subtitle":subtitle,"groups":[g for g in groups if g["prompts"]]}

# role/category slugs from data.json (skip empty)
data=json.load(open(f"{REPO}/data.json"))
slugs=[c["slug"] for c in data["categories"] if c["count"]>0 and c["slug"]!="uncategorized"]
roles={}
for s in slugs:
    try:
        r=parse_role(s)
        np=sum(len(g["prompts"]) for g in r["groups"])
        roles[s]=r
        print(f"  {s:32} groups={len(r['groups']):2} prompts={np:3} sub={'Y' if r['subtitle'] else '-'}")
    except Exception as e:
        print("  ERR",s,e)

out={"roles":roles}
json.dump(out, open(f"{REPO}/content.json","w"), ensure_ascii=False)
tot=sum(sum(len(g['prompts']) for g in r['groups']) for r in roles.values())
print(f"content.json: {len(roles)} role pages, {tot} prompt bodies")
