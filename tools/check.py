"""Pre-flight: broken internal links, stray dashes, meta tags, JSON-LD."""
import json, re, sys
from pathlib import Path
from html.parser import HTMLParser
ROOT = Path(__file__).resolve().parent.parent
BASE = "https://obsidianstudiodesigns.github.io/Blush-and-Blue/"
pages = [p for p in ROOT.rglob("*.html") if "tools" not in p.parts]
bad = []
class P(HTMLParser):
    def __init__(s): super().__init__(); s.refs = []; s.ids = set()
    def handle_starttag(s, tag, attrs):
        a = dict(attrs)
        for k in ("href", "src"):
            if k in a and a[k]: s.refs.append(a[k])
        if "srcset" in a: s.refs.append(a["srcset"])
for f in pages:
    t = f.read_text(encoding="utf-8")
    if "—" in t or "–" in t: bad.append((f.name, "dash"))
    for need in ('property="og:image"', 'property="og:title"', 'property="og:description"', 'rel="canonical"', 'name="description"', "<title>"):
        if need not in t: bad.append((f.name, "missing " + need))
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        json.loads(m)
    og = re.search(r'property="og:image" content="([^"]+)"', t).group(1).replace(BASE, "")
    if not (ROOT / og).exists(): bad.append((f.name, "og missing " + og))
    p = P(); p.feed(t)
    for r in p.refs:
        if r.startswith(("http://", "https://", "tel:", "mailto:", "#", "data:")):
            if not r.startswith(BASE): continue
            r = r.replace(BASE, "")
            tgt = ROOT / r.split("?")[0]
        else:
            tgt = (f.parent / r.split("?")[0].split("#")[0]).resolve()
        if r in ("", ) : continue
        if tgt.is_dir(): tgt = tgt / "index.html"
        if not tgt.exists(): bad.append((f.name, "broken " + r))
    title = re.search(r"<title>(.*?)</title>", t).group(1)
    if len(title) > 70: bad.append((f.name, f"long title {len(title)}"))
    d = re.search(r'name="description" content="([^"]*)"', t).group(1)
    if len(d) > 200: bad.append((f.name, f"long desc {len(d)}"))
print(len(pages), "pages checked")
for b in bad: print(b)
print("sitemap urls", (ROOT / "sitemap.xml").read_text().count("<loc>"))
print("largest og KB", max(p.stat().st_size for p in (ROOT / "assets/img/og").glob("*.jpg")) // 1024)
