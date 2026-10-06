# Shared theme matching ailab.mereka.io — used by build.py
import html

FONTFACE = """
@font-face{font-family:'Poppins Font';font-weight:400;font-display:swap;src:url('/assets/fonts/Poppins-Regular.woff2') format('woff2')}
@font-face{font-family:'Poppins Font';font-weight:500;font-display:swap;src:url('/assets/fonts/Poppins-Medium.woff2') format('woff2')}
@font-face{font-family:'Poppins Font';font-weight:600;font-display:swap;src:url('/assets/fonts/Poppins-SemiBold.woff2') format('woff2')}
@font-face{font-family:'Poppins Font';font-weight:700;font-display:swap;src:url('/assets/fonts/Poppins-Bold.woff2') format('woff2')}
"""

CSS = FONTFACE + """
:root{
  --ink:#1a1623; --muted:#5a5f6b; --white:#fff; --grey:#f6f6f8; --line:#e9eaee;
  /* homepage nav tokens, so every page's header is literally the same */
  --anchor:#1f3f7c; --teal:#1fa3a6; --border:#e6e8ec;
  --pink:#ee53b1; --blue:#5177f9; --accent:linear-gradient(135deg,#ee53b1,#5177f9);
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
.btn-accent{background:var(--accent);color:#fff;box-shadow:0 10px 28px rgba(129,100,220,.32)}
.btn-ghost{background:#fff;color:var(--ink);border-color:var(--line)}
.pill-accent{background:var(--accent);color:#fff;font-weight:600;font-size:.86rem;padding:8px 18px;border-radius:100px}
/* NAV */
header.nav{position:sticky;top:0;z-index:50;background:rgba(255,255,255,.86);backdrop-filter:saturate(160%) blur(12px);border-bottom:1px solid var(--border)}
.nav-inner{display:flex;align-items:center;gap:28px;height:74px}
.nav-logo img{height:38px}
.nav-links{display:flex;align-items:center;gap:26px;margin-left:auto;font-family:'Poppins Font';font-weight:500;font-size:.95rem}
.nav-links a:not(.btn){color:#1a1623;font-weight:500}
.nav-links a:not(.btn):hover{color:var(--teal)}
/* without this the CTA inherits .nav-links a and renders dark-on-dark */
.nav-links a.btn-dark,.nav-links a.nav-cta{color:#fff}
.nav-cta{margin-left:4px;background:var(--anchor)}
.chip{font-family:'Poppins Font';font-weight:500;font-size:.9rem;padding:9px 16px;border-radius:999px;background:#fff;border:1px solid var(--border);box-shadow:var(--shadow-sm)}
.burger{display:none;margin-left:auto;background:none;border:0;cursor:pointer;padding:8px}
.burger span{display:block;width:24px;height:2px;background:var(--ink);margin:5px 0;border-radius:2px}
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
@media(max-width:860px){.nav-links{display:none}.nav-links.open{display:flex;position:absolute;top:74px;left:0;right:0;flex-direction:column;background:#fff;padding:18px 24px;border-bottom:1px solid var(--border);gap:16px}.nav-links.open .nav-cta{margin:6px 0 0}.burger{display:block}.foot-top{grid-template-columns:1fr 1fr}}
"""

def nav():
    """Byte-for-byte the homepage's header (index.html) — same classes, same
    order, same logo — so /prompts/ and the category pages render an identical
    navigation bar."""
    return """<header class="nav">
  <div class="shell nav-inner">
    <a class="nav-logo" href="/" aria-label="Mereka home"><img src="/assets/mereka-logo-emblem.svg" alt="Mereka"></a>
    <a class="chip" href="https://mereka.io" target="_blank" rel="noopener" style="background:var(--accent);color:#fff;border:0;font-weight:600;margin-left:2px">Marketplace</a>
    <button class="burger" aria-label="Menu" onclick="document.getElementById('nav').classList.toggle('open')"><span></span><span></span><span></span></button>
    <nav class="nav-links" id="nav">
      <a href="https://corporate.mereka.io" target="_blank" rel="noopener">Our Approach</a>
      <a href="https://corporate.mereka.io/academy" target="_blank" rel="noopener">Grow with us</a>
      <a href="https://corporate.mereka.io/create-with-us" target="_blank" rel="noopener">Create With Us</a>
      <a href="https://mereka.io/hubs" target="_blank" rel="noopener">Discover Spaces</a>
      <a href="https://corporate.mereka.io/about-us" target="_blank" rel="noopener">Company</a>
      <a class="btn btn-dark nav-cta" href="/#contact">Contact Us</a>
    </nav>
  </div>
</header>"""

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

def head(title, desc, canonical, extra_css=""):
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:url" content="{canonical}">
<link rel="icon" href="/assets/favicon.png">
<style>{CSS}{extra_css}</style></head><body id="top">"""
