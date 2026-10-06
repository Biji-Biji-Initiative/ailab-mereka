import re, json, html as H

s=open('io-hdr.html',encoding='utf-8',errors='replace').read()
i=s.find('brx-nav-nested-items'); j=s.find('</header>')
hdr=s[i:j]

def split_blocks(text, cls):
    """yield the inner HTML of each <tag class="...cls..."> ... </tag> by depth-matching."""
    out=[]
    for m in re.finditer(r'<(\w+)[^>]*class="[^"]*'+re.escape(cls)+r'[^"]*"[^>]*>', text):
        tag=m.group(1); depth=1; p=m.end()
        pat=re.compile(r'</?'+tag+r'\b[^>]*>')
        while depth and p<len(text):
            mm=pat.search(text,p)
            if not mm: break
            depth += -1 if mm.group(0).startswith('</') else 1
            p=mm.end()
        out.append((m.start(), text[m.end():p-len(f'</{tag}>')]))
    return out

def strip(t): return H.unescape(re.sub(r'<[^>]+>','',t or '')).strip()

menus=[]
for start, inner in split_blocks(hdr,'megamenu'):
    tog=re.search(r'class="[^"]*brx-submenu-toggle[^"]*"[^>]*>(.*?)<button', inner, re.S)
    label=strip(tog.group(1)) if tog else '?'
    content=re.search(r'class="[^"]*megamenu__content[^"]*"[^>]*>(.*)', inner, re.S)
    body=content.group(1) if content else ''
    cols=[]
    for _, col in split_blocks(body,'submenu-column'):
        ht=re.search(r'class="[^"]*submenu-list-title[^"]*"[^>]*>(.*?)</', col, re.S)
        heading=strip(ht.group(1)) if ht else ''
        items=[]
        for am in re.finditer(r'<a[^>]*class="[^"]*submenu-link[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', col, re.S):
            href, in_a = am.group(1), am.group(2)
            svg=re.search(r'(<svg.*?</svg>)', in_a, re.S)
            text=strip(re.sub(r'<svg.*?</svg>','',in_a,flags=re.S))
            items.append({'text':text,'href':href,'svg':svg.group(1) if svg else ''})
        if items: cols.append({'heading':heading,'items':items})
    menus.append({'label':label,'columns':cols})

json.dump(menus, open('io_menus.json','w'), ensure_ascii=False, indent=1)
for m in menus:
    print(f"{m['label']}: {len(m['columns'])} column(s)")
    for c in m['columns']:
        print(f"   [{c['heading'] or '-'}] " + ", ".join(i['text'] for i in c['items']))
        print(f"      svg bytes: {[len(i['svg']) for i in c['items']]}")
