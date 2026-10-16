# Shared theme matching ailab.mereka.io — used by build.py
import html, os, json
from navdata import MENUS

FONTFACE = """
@font-face{font-family:'Poppins Font';font-weight:400;font-display:swap;src:url('/assets/fonts/Poppins-Regular.woff2') format('woff2')}
@font-face{font-family:'Poppins Font';font-weight:500;font-display:swap;src:url('/assets/fonts/Poppins-Medium.woff2') format('woff2')}
@font-face{font-family:'Poppins Font';font-weight:600;font-display:swap;src:url('/assets/fonts/Poppins-SemiBold.woff2') format('woff2')}
@font-face{font-family:'Poppins Font';font-weight:700;font-display:swap;src:url('/assets/fonts/Poppins-Bold.woff2') format('woff2')}
"""

MENU_CSS = """
/* ---- the whole site header: structure, mega-menu panels and the mobile
     accordion. build.py injects this into assets/ailab.css too, so the
     hand-written pages cannot keep a drifted copy of it. ---- */
header.nav{position:sticky;top:0;z-index:50;background:rgba(255,255,255,.86);backdrop-filter:saturate(160%) blur(12px);border-bottom:1px solid var(--border)}
.nav-inner{display:flex;align-items:center;gap:28px;height:74px}
.nav-logo img{height:38px}
/* .nav-links fills the space left of the logo block so .nav-menus can centre
   inside it; the Contact CTA keeps its place against the right edge */
.nav-links{display:flex;align-items:center;gap:22px;flex:1;min-width:0;font-family:'Poppins Font';font-weight:500;font-size:.95rem}
.nav-menus{display:flex;align-items:center;gap:22px;margin:0 auto}
/* seven items need ~1105px; without nowrap they wrap inside each link */
.nav-links a{white-space:nowrap}
.nav-links a:not(.btn){color:#1a1623;font-weight:500}
.nav-links a:not(.btn):hover{color:var(--teal)}
/* without this the CTA inherits .nav-links a and renders dark-on-dark */
.nav-links a.btn-dark,.nav-links a.nav-cta{color:#fff}
.nav-cta{margin-left:4px;background:var(--anchor)}
.nav-links a[aria-current="page"]{color:var(--teal);font-weight:600}
.burger{display:none;margin-left:auto;background:none;border:0;cursor:pointer;padding:8px}
.burger span{display:block;width:24px;height:2px;background:var(--ink);margin:5px 0;border-radius:2px}
/* ---- mega-menu (hover panels), 1-to-1 with ailab.mereka.io ---- */
.navitem{position:relative;display:inline-flex;align-items:center}
.navtrigger{background:none;border:0;padding:0;font:inherit;color:#1a1623;font-weight:500;cursor:pointer;white-space:nowrap}
.navitem:hover .navtrigger,.navitem:focus-within .navtrigger{color:#8c8b91}
/* the panel's transparent top padding bridges the gap to the trigger, so the
   pointer never leaves the hover target on its way down */
.navpanel{position:absolute;top:100%;left:50%;transform:translateX(-50%);padding-top:18px;z-index:70;
  opacity:0;visibility:hidden;pointer-events:none;transition:opacity .16s var(--ease)}
.navitem:hover .navpanel,.navitem:focus-within .navpanel{opacity:1;visibility:visible;pointer-events:auto}
.navitem--end .navpanel{left:auto;right:0;transform:none}
.navcard{display:grid;grid-auto-flow:column;gap:0 40px;background:#fff;border-radius:20px;padding:6px;
  box-shadow:0 26px 64px rgba(26,22,35,.16),0 4px 14px rgba(26,22,35,.06)}
.navcard--stack{grid-auto-flow:row;grid-template-columns:auto auto}
.navcol{padding:11px 24px}
.navhead{font-size:.8rem;font-weight:500;text-transform:uppercase;color:#8c8b91;padding:7px 0;margin:0}
.navlink{display:flex;align-items:center;gap:16px;padding:7px 0;font-size:.875rem;font-weight:500;color:#53505a;white-space:nowrap}
.navlink:hover{color:var(--ink)}
.navlink .ni{flex:none;width:18px;height:18px;display:inline-flex;align-items:center;justify-content:center}
.navlink .ni svg{width:100%;height:100%;display:block}
.navfoot{grid-column:1/-1;display:grid;grid-auto-flow:column;gap:0 40px;background:#f0f2f3;border-radius:16px;padding:10px 24px;margin:6px}
/* below 1160px the panels stop hovering and stack inside the burger menu,
   aligned to the right edge the burger itself sits on */
@media(max-width:1160px){.nav-links{display:none}.nav-links.open{display:flex;position:absolute;top:74px;left:0;right:0;flex-direction:column;align-items:flex-end;text-align:right;background:#fff;padding:18px 24px;border-bottom:1px solid var(--border);gap:16px;max-height:calc(100dvh - 74px);overflow-y:auto;overscroll-behavior:contain;-webkit-overflow-scrolling:touch;box-shadow:0 18px 40px rgba(26,22,35,.14)}.nav-menus{display:contents}.nav-links.open .nav-cta{margin:6px 0 0}.nav-links.open a{white-space:normal}.burger{display:block}.navitem{display:block;width:100%}.navtrigger{display:flex;align-items:center;justify-content:flex-end;gap:10px;width:100%;text-align:right;padding:8px 0;font-weight:600;color:#1a1623}.navitem:hover .navtrigger{color:#1a1623}.navtrigger::after{content:'';flex:none;width:8px;height:8px;border-right:2px solid #8c8b91;border-bottom:2px solid #8c8b91;transform:rotate(45deg) translate(-2px,-2px);transition:transform .2s var(--ease)}.navitem.open .navtrigger::after{transform:rotate(-135deg) translate(-3px,-3px)}.navpanel{display:none;position:static;opacity:1;visibility:visible;pointer-events:auto;transform:none;padding-top:0}.navitem.open .navpanel{display:block}.navcard,.navcard--stack{display:block;box-shadow:none;border-radius:0;padding:0;background:transparent}.navcol{padding:2px 0 8px;text-align:right}.navhead{padding:6px 0 2px}.navlink{justify-content:flex-end}.navfoot{display:block;background:transparent;border-radius:0;padding:0;margin:0}.navlink{white-space:normal}}
"""

CSS = FONTFACE + """
:root{
  --ink:#1a1623; --muted:#5a5f6b; --white:#fff; --grey:#f6f6f8; --line:#e9eaee;
  /* homepage nav tokens, so every page's header is literally the same */
  --anchor:#1f3f7c; --teal:#1fa3a6; --border:#e6e8ec;
  --pink:#1fa3a6; --blue:#1f3f7c; --accent:linear-gradient(135deg,#1f3f7c,#1fa3a6);
  --maxw:1180px; --ease:cubic-bezier(.2,.7,.2,1);
  --shadow:0 20px 60px rgba(26,22,35,.10); --shadow-sm:0 8px 24px rgba(26,22,35,.06);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:100px}
body{margin:0;font-family:'Poppins Font',system-ui,Arial,sans-serif;color:var(--ink);background:var(--white);line-height:1.6;-webkit-font-smoothing:antialiased}
h1,h2,h3,h4,h5{font-family:'Poppins Font',system-ui,sans-serif;font-weight:700;line-height:1.12;margin:0}
a{color:inherit;text-decoration:none}
img{max-width:100%;display:block}
.shell{max-width:var(--maxw);margin:0 auto;padding:0 28px}
.btn{display:inline-flex;align-items:center;gap:9px;font-family:'Poppins Font';font-weight:600;font-size:.98rem;padding:14px 26px;border-radius:999px;cursor:pointer;border:1.5px solid transparent;transition:transform .2s var(--ease),background .2s,box-shadow .2s}
.btn:hover{transform:translateY(-2px)}
.btn-dark{background:var(--ink);color:#fff}
.btn-accent{background:var(--accent);color:#fff;box-shadow:0 10px 28px rgba(31,63,124,.28)}
.btn-ghost{background:#fff;color:var(--ink);border-color:var(--line)}
.pill-accent{background:var(--accent);color:#fff;font-weight:600;font-size:.86rem;padding:8px 18px;border-radius:100px}
/* NAV */
""" + MENU_CSS + """
.chip{font-family:'Poppins Font';font-weight:500;font-size:.9rem;padding:9px 16px;border-radius:999px;background:#fff;border:1px solid var(--border);box-shadow:var(--shadow-sm)}
/* FOOTER */
footer{background:var(--ink);color:#cfd2da;padding:70px 0 34px;margin-top:40px}
footer h5{color:#fff;font-size:.82rem;letter-spacing:.12em;text-transform:uppercase;margin-bottom:16px}
footer ul{list-style:none;padding:0;margin:0}
footer li{margin:9px 0}
footer a{color:#cfd2da;font-size:.94rem}
footer a:hover{color:#fff}
.foot-top{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:34px;padding-bottom:34px;border-bottom:1px solid rgba(255,255,255,.12)}
.foot-logo img{height:28px;filter:brightness(0) invert(1);margin-bottom:14px}
.foot-social{display:flex;gap:12px;margin-top:14px}
.foot-social a{width:34px;height:34px;border:1px solid rgba(255,255,255,.24);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.74rem}
.foot-bottom{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;padding-top:22px;font-size:.86rem;color:#9a9dab}
.foot-bottom a{color:#9a9dab;margin-left:18px}
@media(max-width:860px){.foot-top{grid-template-columns:1fr 1fr}}
@media(max-width:560px){.foot-top{grid-template-columns:1fr;gap:26px}}
"""

# ---------------------------------------------------------------- menus
# navdata.py is scraped from ailab.mereka.io and must stay a faithful copy, so
# the AI Lab's own pages are added here instead of hand-edited into it.
TRAINING_ICON = ('<svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" '
                 'viewBox="0 0 24 24" fill="none"><path d="M12 2 1.5 7.5 12 13l10.5-5.5L12 2Z" fill="#36C8F6"/>'
                 '<path d="M5 10.5v5.2c0 .6.3 1.1.8 1.4C7.3 18 9.5 19 12 19s4.7-1 6.2-1.9c.5-.3.8-.8.8-1.4v-5.2'
                 'L12 15 5 10.5Z" fill="#2583EF"/><path d="M21 8.6v6.1h1.5V8.6H21Z" fill="#A2E4F4"/></svg>')

TRAINING_COLUMN = {"heading": "Training", "footer": False, "items": [
    {"text": "AI Lab Corporate Training", "href": "/corporate-training/",
     "svg": TRAINING_ICON, "blank": False},
    {"text": "AI Lab Public Training", "href": "/public-training/",
     "svg": TRAINING_ICON, "blank": False},
]}

def _menus():
    """MENUS with the AI Lab's own Training column pushed to the front of the
    'Grow with us' panel. Copied, never mutated, so a rebuild in the same
    process cannot stack the column twice."""
    out = []
    for m in MENUS:
        if m["label"] == "Grow with us":
            m = dict(m, columns=[TRAINING_COLUMN] + list(m["columns"]))
        out.append(m)
    return out


def _menu(m, is_last):
    """One hover panel: columns of icon links, plus the grey full-width row
    that only the Company menu has."""
    cols, foot = "", ""
    for c in m["columns"]:
        links = "".join(
            f'<a class="navlink" href="{i["href"]}"'
            f'{" target=\"_blank\" rel=\"noopener\"" if i.get("blank", True) else ""}>'
            f'<span class="ni">{i["svg"]}</span><span>{html.escape(i["text"])}</span></a>'
            for i in c["items"])
        if c.get("footer"):
            foot = f'<div class="navfoot">{links}</div>'
        else:
            head = f'<p class="navhead">{html.escape(c["heading"])}</p>' if c["heading"] else ""
            cols += f'<div class="navcol">{head}{links}</div>'
    card = "navcard navcard--stack" if foot else "navcard"
    tail = " navitem--end" if is_last else ""
    return (f'<div class="navitem{tail}">'
            f'<button class="navtrigger" type="button" aria-haspopup="true">{html.escape(m["label"])}</button>'
            f'<div class="navpanel"><div class="{card}">{cols}{foot}</div></div></div>')


# ---------------------------------------------------------------- SEO
# ailab.mereka.dev is a preview of the production site and must never be
# indexed. The metadata below is written for production, so promoting it is a
# single switch: build with AILAB_SITE_URL=https://ailab.mereka.io and every
# canonical, og:url, sitemap entry and the robots rules flip with it, and the
# noindex comes off. Until then every page ships noindex,nofollow and
# robots.txt disallows everything.
PROD_URL = "https://ailab.mereka.io"
SITE_URL = os.environ.get("AILAB_SITE_URL", "https://ailab.mereka.dev").rstrip("/")
IS_PROD  = SITE_URL == PROD_URL

OG_IMAGE   = "/assets/img/bg-cta.jpg"   # 1500x600 session photo
OG_IMAGE_W = "1500"
OG_IMAGE_H = "600"
SITE_NAME  = "Mereka AI Lab"
TWITTER    = "@mereka_io"

ORGANISATION = {
    "@type": "Organization",
    "@id": PROD_URL + "/#organisation",
    "name": "Mereka AI Lab",
    "url": PROD_URL + "/",
    "logo": PROD_URL + "/assets/mereka-logo.svg",
    "description": "HRD Corp claimable, hands-on AI training for Malaysian teams.",
    "email": "ailab@mereka.io",
    "areaServed": "MY",
    "parentOrganization": {"@type": "Organization", "name": "Mereka", "url": "https://mereka.io/"},
    "sameAs": [
        "https://www.linkedin.com/company/mereka",
        "https://www.facebook.com/mereka.io",
        "https://www.instagram.com/mereka.io/",
        "https://www.tiktok.com/@mereka.io",
        "https://www.youtube.com/channel/UCGJ5RzyL0oib2ONP2gPvOYA",
    ],
}


def _ld(graph):
    """One @graph block per page; Organization and WebSite are always present."""
    base = [ORGANISATION, {
        "@type": "WebSite",
        "@id": PROD_URL + "/#website",
        "url": PROD_URL + "/",
        "name": SITE_NAME,
        "publisher": {"@id": PROD_URL + "/#organisation"},
        "inLanguage": "en-MY",
    }]
    doc = {"@context": "https://schema.org", "@graph": base + list(graph or [])}
    return ('<script type="application/ld+json">'
            + json.dumps(doc, ensure_ascii=False, separators=(",", ":"))
            + "</script>")


def clamp(text, limit):
    """Trim to a word boundary so a description is not cut mid-word in a SERP."""
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(" ,;:\u2014-")
    return cut + "\u2026"


def plural(n, one, many=None):
    return one if n == 1 else (many or one + "s")


def seo(title, desc, path, schema=None, og_type="website"):
    """Title/description/canonical/OG/Twitter/robots + JSON-LD for one page."""
    url = SITE_URL + path
    img = SITE_URL + OG_IMAGE
    e = html.escape
    robots = ('<meta name="robots" content="index, follow, max-image-preview:large, '
              'max-snippet:-1, max-video-preview:-1">') if IS_PROD else \
             '<meta name="robots" content="noindex, nofollow">'
    return (
        f'<title>{e(title)}</title>\n'
        f'<meta name="description" content="{e(desc)}">\n'
        f'{robots}\n'
        f'<link rel="canonical" href="{url}">\n'
        f'<meta property="og:type" content="{og_type}">'
        f'<meta property="og:site_name" content="{SITE_NAME}">'
        f'<meta property="og:locale" content="en_MY">'
        f'<meta property="og:title" content="{e(title)}">'
        f'<meta property="og:description" content="{e(desc)}">'
        f'<meta property="og:url" content="{url}">'
        f'<meta property="og:image" content="{img}">'
        f'<meta property="og:image:width" content="{OG_IMAGE_W}">'
        f'<meta property="og:image:height" content="{OG_IMAGE_H}">\n'
        f'<meta name="twitter:card" content="summary_large_image">'
        f'<meta name="twitter:site" content="{TWITTER}">'
        f'<meta name="twitter:title" content="{e(title)}">'
        f'<meta name="twitter:description" content="{e(desc)}">'
        f'<meta name="twitter:image" content="{img}">\n'
        + _ld(schema)
    )


NAV_SCRIPT = """
<script>
/* The mega-menus hover open on desktop. Below the breakpoint there is no
   hover, and showing every panel at once made the burger menu a 3000px wall —
   so each trigger becomes an accordion, one open at a time. Desktop is left
   entirely to CSS; this only binds while the mobile layout is active. */
(function(){
  var mq = matchMedia('(max-width:1160px)');
  var nav = document.getElementById('nav');
  if (!nav) return;
  var items = [].slice.call(nav.querySelectorAll('.navitem'));
  items.forEach(function(it){
    var trigger = it.querySelector('.navtrigger');
    if (!trigger) return;
    trigger.setAttribute('aria-expanded', 'false');
    trigger.addEventListener('click', function(){
      if (!mq.matches) return;           /* desktop still opens on hover */
      var open = it.classList.contains('open');
      items.forEach(function(o){
        o.classList.remove('open');
        var t = o.querySelector('.navtrigger');
        if (t) t.setAttribute('aria-expanded', 'false');
      });
      if (!open) { it.classList.add('open'); trigger.setAttribute('aria-expanded', 'true'); }
    });
  });
  /* leaving the mobile layout must not strand a collapsed menu: desktop reads
     .open from :hover, and a stale .open would pin one panel permanently */
  mq.addEventListener('change', function(){
    if (!mq.matches) {
      items.forEach(function(o){
        o.classList.remove('open');
        var t = o.querySelector('.navtrigger');
        if (t) t.setAttribute('aria-expanded', 'false');
      });
      nav.classList.remove('open');
    }
  });
})();
</script>
"""


# The header CTA opens WhatsApp with the AI Lab message already written.
# It used to scroll to #contact, which looked like a dead link in review:
# the URL changed to #contact and, from the footer, nothing moved.
CONTACT_WA = ("https://wa.me/601130116472?text=Hi%20Mereka%20AI%20Lab%2C%0A"
              "%0AI%E2%80%99d%20like%20to%20know%20more%20about%20your%20AI%20training%20programmes.")


def nav(current="", contact=CONTACT_WA):
    """The site header. build.py injects this exact string into index.html too,
    so the homepage and the generated pages cannot drift apart. The five
    mega-menus come from navdata.py, scraped from ailab.mereka.io's own header
    (scrape_nav.py) — icons included."""
    menus = "".join(_menu(m, i == len(_menus()) - 1) for i, m in enumerate(_menus()))
    return f"""<header class="nav">
  <div class="shell nav-inner">
    <a class="nav-logo" href="/" aria-label="Mereka home"><img src="/assets/mereka-logo-emblem.svg" alt="Mereka"></a>
    <a class="chip" href="https://mereka.io" target="_blank" rel="noopener" style="background:var(--accent);color:#fff;border:0;font-weight:600;margin-left:2px">Marketplace</a>
    <button class="burger" aria-label="Menu" onclick="document.getElementById('nav').classList.toggle('open')"><span></span><span></span><span></span></button>
    <nav class="nav-links" id="nav">
      <div class="nav-menus">{menus}</div>
      <a class="btn btn-dark nav-cta" href="{contact}" target="_blank" rel="noopener">Contact Us</a>
    </nav>
  </div>
</header>""" + NAV_SCRIPT

def footer():
    return """<footer><div class="shell">
  <div class="foot-top">
    <div>
      <div class="foot-logo"><img src="/assets/mereka-logo.svg" alt="Mereka"></div>
      <p style="max-width:34ch;color:#cfd2da">We upskill &amp; empower companies to boost productivity with AI.</p>
      <div class="foot-social">
        <a href="https://www.tiktok.com/@mereka.io" target="_blank" rel="noopener">TT</a>
        <a href="https://www.instagram.com/mereka.io/" target="_blank" rel="noopener">IG</a>
        <a href="https://www.facebook.com/mereka.io" target="_blank" rel="noopener">FB</a>
        <a href="https://www.linkedin.com/company/mereka" target="_blank" rel="noopener">IN</a>
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
      <li><a href="https://corporate.mereka.io/academy/makerspace" target="_blank" rel="noopener">Makerspace</a></li>
    </ul></div>
    <div><h5>Marketplace</h5><ul>
      <li><a href="https://mereka.io/experiences" target="_blank" rel="noopener">Experiences</a></li>
      <li><a href="https://mereka.io/hubs" target="_blank" rel="noopener">Hubs</a></li>
      <li><a href="https://mereka.io/jobs" target="_blank" rel="noopener">Jobs</a></li>
    </ul></div>
  </div>
  <div class="foot-bottom"><span>&copy; 2026 Mereka</span>
    <span><a href="https://legal.mereka.io/" target="_blank" rel="noopener">Terms of Use</a><a href="https://legal.mereka.io/privacy-policy/" target="_blank" rel="noopener">Privacy Policy</a></span>
  </div>
</div></footer>"""

def head(title, desc, path, extra_css="", schema=None):
    """`path` is site-root-relative ("/prompts/"); seo() turns it into the
    canonical and og:url for whichever host this build targets."""
    return f"""<!doctype html><html lang="en-MY"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
{seo(title, desc, path, schema)}
<link rel="icon" href="/assets/favicon.png">
<style>{CSS}{extra_css}</style></head><body id="top">"""
