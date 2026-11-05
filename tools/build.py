"""Builds every page of the static store from tools/catalogue.json.

Run:  python tools/build.py
To load the real range: replace tools/catalogue.json, add images to assets/img/products, run this again.
"""
import html
import json
import re
from datetime import date
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://obsidianstudiodesigns.github.io/Blush-and-Blue/"
NAME = "Blush and Blue"
PHONE_DISPLAY = "061 510 7109"
PHONE_INTL = "+27615107109"
WA = "27615107109"
STUDIO = "https://obsidianstudiodesigns.co.za/"
TODAY = date.today().isoformat()
UPDATED = "5 November 2026"
PHOTOS = {"rose-dune-flip-flop", "onyx-ring-thong-2"}  # lifestyle shots that fill the tile instead of multiplying into it
PRODUCTS = json.loads((ROOT / "tools/catalogue.json").read_text(encoding="utf-8"))
ICONS = ["whatsapp-logo", "tote", "x", "plus", "minus", "magnifying-glass", "list", "arrow-right", "arrow-left", "phone", "house", "storefront", "caret-down", "circle-half"]
PH = Path(r"C:/Users/Henry/AppData/Local/Temp/claude/26d4b3e86753fb36/eeaec55e-f899-467d-a48a-30f0f0e73832/scratchpad/ph/package/assets/light")
SPRITE_CACHE = ROOT / "tools/icons.svg"

esc = lambda s: html.escape(str(s), quote=True)
money = lambda n: "R " + f"{n:,}".replace(",", " ")
DEPT = {"ladies": "Ladies", "mens": "Mens"}
CAT = {"shoes": "Shoes", "clothing": "Clothing", "accessories": "Accessories"}


def sprite():
    if PH.exists():
        out = []
        for n in ICONS:
            svg = (PH / f"{n}-light.svg").read_text(encoding="utf-8")
            inner = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1)
            out.append(f'<symbol id="i-{n}" viewBox="0 0 256 256">{inner}</symbol>')
        SPRITE_CACHE.write_text("".join(out), encoding="utf-8")  # Phosphor Icons, MIT
    return f'<svg width="0" height="0" style="position:absolute" aria-hidden="true">{SPRITE_CACHE.read_text(encoding="utf-8")}</svg>'


SPRITE = sprite()
ic = lambda n: f'<svg class="icon" aria-hidden="true"><use href="#i-{n}"></use></svg>'


def head(r, title, desc, path, og="assets/img/og/home.jpg", og_alt="Blush and Blue: ladies and mens clothing, shoes and accessories", ld=None, noindex=False, og_type="website"):
    url = SITE + path
    img = SITE + og
    robots = '<meta name="robots" content="noindex,follow">' if noindex else '<meta name="robots" content="index,follow,max-image-preview:large">'
    jsonld = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>' if ld else ""
    return f"""<!doctype html>
<html lang="en-ZA" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
{robots}
<meta name="theme-color" content="#fbf1ee">
<meta name="color-scheme" content="light dark">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{NAME}">
<meta property="og:locale" content="en_ZA">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta property="og:image:secure_url" content="{img}">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(og_alt)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{img}">
<link rel="icon" href="{r}favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="96x96" href="{r}favicon-96.png">
<link rel="icon" type="image/png" sizes="192x192" href="{r}icon-192.png">
<link rel="apple-touch-icon" href="{r}apple-touch-icon.png">
<link rel="manifest" href="{r}site.webmanifest">
<link rel="preload" href="{r}assets/fonts/BodoniModa-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{r}assets/fonts/Jost-normal.woff2" as="font" type="font/woff2" crossorigin>
<script>(function(){{var t=null;try{{t=localStorage.getItem('bb-theme')}}catch(e){{}}if(!t)t=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';var d=document.documentElement;d.dataset.theme=t;d.classList.add('js');document.querySelector('meta[name=theme-color]').content=t==='dark'?'#0b1324':'#fbf1ee'}})();</script>
<link rel="stylesheet" href="{r}assets/css/style.css">
{jsonld}
</head>"""


def wordmark(r, cls=""):
    return (f'<img class="on-light" src="{r}assets/img/brand/wordmark-on-light.png" alt="{NAME}" width="1000" height="62">'
            f'<img class="on-dark" src="{r}assets/img/brand/wordmark-on-dark.png" alt="" width="1000" height="62">')


NAV = [("Ladies", "shop.html?dept=ladies"), ("Mens", "shop.html?dept=mens"), ("Shoes", "shop.html?cat=shoes"), ("Clothing", "shop.html?cat=clothing"), ("Accessories", "shop.html?cat=accessories")]


def top(r, page=""):
    links = "".join(f'<a href="{r}{h}">{t}</a>' for t, h in NAV)
    menu = "".join(f'<li><a class="menu-link" href="{r}{h}">{t}</a></li>' for t, h in NAV)
    def cur(p):
        return ' aria-current="page"' if p == page else ""
    return f"""<body data-root="{r}" data-page="{page}">
{SPRITE}
<a class="skip" href="#main">Skip to content</a>
<header class="site-head">
  <div class="wrap site-head__row">
    <nav class="site-nav" aria-label="Main">{links}</nav>
    <button class="icon-btn menu-btn" type="button" data-open-menu aria-label="Open menu">{ic('list')}</button>
    <a class="brand" href="{r}index.html" aria-label="{NAME} home">{wordmark(r)}</a>
    <div class="head-actions">
      <a class="icon-btn wa-head" href="https://wa.me/{WA}" target="_blank" rel="noopener" aria-label="Chat to us on WhatsApp">{ic('whatsapp-logo')}</a>
      <button class="theme-switch" type="button" data-theme-toggle aria-pressed="false" aria-label="Switch theme"><span class="t-blush">Blush</span><span class="t-blue">Blue</span></button>
      <button class="icon-btn bag-btn" type="button" data-open-bag aria-label="Open your bag">{ic('tote')}<span class="bag-count" hidden>0</span></button>
    </div>
  </div>
</header>
<nav class="tabbar" aria-label="Quick links">
  <a class="tab" href="{r}index.html"{cur('home')}>{ic('house')}Home</a>
  <a class="tab" href="{r}shop.html"{cur('shop')}>{ic('storefront')}Shop</a>
  <button class="tab" type="button" data-theme-toggle aria-pressed="false" aria-label="Switch theme">{ic('circle-half')}Theme</button>
  <a class="tab tab--wa" href="https://wa.me/{WA}" target="_blank" rel="noopener">{ic('whatsapp-logo')}WhatsApp</a>
  <button class="tab" type="button" data-open-bag>{ic('tote')}<span class="bag-count" hidden>0</span>Bag</button>
</nav>
<dialog class="sheet sheet--left" id="menu" aria-label="Menu">
  <div class="sheet__head"><h2>Menu</h2><button class="icon-btn" type="button" data-close aria-label="Close menu">{ic('x')}</button></div>
  <div class="sheet__body">
    <ul class="menu-list">{menu}<li><a class="menu-link" href="{r}shop.html?tag=new">New in</a></li></ul>
    <ul class="menu-sub">
      <li><a href="{r}contact.html">Contact</a></li>
      <li><a href="{r}size-guide.html">Size guide</a></li>
      <li><a href="{r}delivery-returns.html">Delivery and returns</a></li>
    </ul>
  </div>
</dialog>"""


def bottom(r, extra=""):
    year = date.today().year
    return f"""<footer class="site-foot">
  <div class="wrap">
    <div class="foot-grid">
      <div class="foot-brand">
        {wordmark(r)}
        <p>Ladies and mens clothing, shoes and accessories, ordered on WhatsApp and delivered across South Africa.</p>
      </div>
      <div class="foot-col">
        <h3>Shop</h3>
        <ul>
          <li><a href="{r}shop.html?dept=ladies">Ladies</a></li>
          <li><a href="{r}shop.html?dept=mens">Mens</a></li>
          <li><a href="{r}shop.html?cat=shoes">Shoes</a></li>
          <li><a href="{r}shop.html?cat=clothing">Clothing</a></li>
          <li><a href="{r}shop.html?cat=accessories">Accessories</a></li>
        </ul>
      </div>
      <div class="foot-col">
        <h3>Help</h3>
        <ul>
          <li><a href="{r}contact.html">Contact</a></li>
          <li><a href="{r}size-guide.html">Size guide</a></li>
          <li><a href="{r}delivery-returns.html">Delivery and returns</a></li>
          <li><a href="{r}privacy.html">Privacy policy</a></li>
          <li><a href="{r}terms.html">Terms and conditions</a></li>
        </ul>
      </div>
      <div class="foot-col foot-contact">
        <h3>Talk to us</h3>
        <ul>
          <li><a href="https://wa.me/{WA}" target="_blank" rel="noopener">WhatsApp {PHONE_DISPLAY}</a></li>
          <li><a href="tel:{PHONE_INTL}">Call {PHONE_DISPLAY}</a></li>
        </ul>
      </div>
    </div>
    <div class="foot-end">
      <span>&copy; {year} {NAME}. All rights reserved.</span>
      <span class="credit">Designed by <a href="{STUDIO}" target="_blank" rel="noopener">Obsidian Studio Designs</a></span>
      <span class="sample-note">Preview catalogue: products and prices are samples until the final range is loaded.</span>
    </div>
  </div>
</footer>
<dialog class="sheet" id="bag" aria-labelledby="bag-title">
  <div class="sheet__head"><h2 id="bag-title">Your bag</h2><button class="icon-btn" type="button" data-close aria-label="Close your bag">{ic('x')}</button></div>
  <div class="sheet__body" id="bag-body"></div>
  <div class="sheet__foot" id="bag-foot" hidden>
    <div class="sum-row sum-row--total"><span>Subtotal</span><span id="bag-total"></span></div>
    <p class="sum-note" id="bag-note"></p>
    <a class="btn btn--block" href="{r}checkout.html">Go to checkout</a>
  </div>
</dialog>
<dialog class="quick" id="quick" aria-labelledby="quick-name">
  <div class="quick__grid">
    <div class="quick__img"><img id="quick-img" src="" alt="" width="380" height="380"></div>
    <div class="quick__info">
      <button class="icon-btn quick__close" type="button" data-close aria-label="Close">{ic('x')}</button>
      <div>
        <h2 id="quick-name"></h2>
        <p class="quick__price" id="quick-price"></p>
      </div>
      <p class="line__meta">Colour: <span id="quick-colour"></span></p>
      <div>
        <div class="opt-label"><b>Choose a size</b><a class="link" href="{r}size-guide.html">Size guide</a></div>
        <div class="chips" id="quick-sizes"></div>
        <p class="opt-error" id="quick-error" role="alert" hidden>Choose a size to add this to your bag.</p>
      </div>
      <button class="btn btn--block" type="button" id="quick-add">Add to bag</button>
      <a class="link" id="quick-link" href="#">View full details</a>
    </div>
  </div>
</dialog>
{extra}
<script src="{r}assets/js/products.js"></script>
<script src="{r}assets/js/app.js"></script>
</body>
</html>
"""


def card(p, r, lazy=True):
    img = p["images"][0]
    photo = ' class="is-photo"' if img in PHOTOS else ""
    label = f'{DEPT[p["dept"]]} {CAT[p["cat"]].lower()}'
    search = esc(f'{p["name"]} {label} {p["colours"][0][0]} {p["desc"]}'.lower())
    load = 'loading="lazy" decoding="async"' if lazy else 'decoding="async"'
    return f"""<article class="card" data-dept="{p['dept']}" data-cat="{p['cat']}" data-price="{p['price']}" data-tags="{' '.join(p['tags'])}" data-search="{search}">
  <div class="card__media"><img{photo} src="{r}assets/img/products/{img}.webp" alt="{esc(p['name'])} in {esc(p['colours'][0][0].lower())}" width="500" height="500" {load}>
    <button class="card__add" type="button" data-quick="{p['slug']}" aria-label="Add {esc(p['name'])} to bag">{ic('plus')}</button></div>
  <div class="card__body"><a class="card__name" href="{r}products/{p['slug']}.html">{esc(p['name'])}</a><span class="card__meta">{label}</span><span class="card__price">{money(p['price'])}</span></div>
</article>"""


ORG = {
    "@type": "OnlineStore", "@id": SITE + "#store", "name": NAME, "url": SITE, "logo": SITE + "icon-512.png", "image": SITE + "assets/img/og/home.jpg",
    "description": "Ladies and mens clothing, shoes and accessories in South Africa, ordered on WhatsApp.",
    "telephone": PHONE_INTL, "currenciesAccepted": "ZAR", "areaServed": {"@type": "Country", "name": "South Africa"},
    "contactPoint": {"@type": "ContactPoint", "telephone": PHONE_INTL, "contactType": "sales", "areaServed": "ZA", "availableLanguage": "English"},
}


def write(path, content):
    f = ROOT / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")


def home():
    r = ""
    rail = [p for p in PRODUCTS if "new" in p["tags"]][:10]
    ld = {"@context": "https://schema.org", "@graph": [ORG, {
        "@type": "WebSite", "@id": SITE + "#website", "url": SITE, "name": NAME, "publisher": {"@id": SITE + "#store"},
        "potentialAction": {"@type": "SearchAction", "target": SITE + "shop.html?q={search_term_string}", "query-input": "required name=search_term_string"},
    }]}
    body = f"""<main id="main">
<section class="hero">
  <div class="hero__img hero__img--blush"><picture><source media="(max-width: 899px)" srcset="assets/img/editorial/hero-blush-m.webp"><img src="assets/img/editorial/hero-blush.webp" alt="Gold strappy heels on a stone plinth against a soft blush backdrop" width="2200" height="1125" fetchpriority="high"></picture></div>
  <div class="hero__img hero__img--blue"><picture><source media="(max-width: 899px)" srcset="assets/img/editorial/hero-blue-m.webp"><img src="assets/img/editorial/hero-blue.webp" alt="Gold strappy heels under a warm spotlight against a midnight blue backdrop" width="2200" height="1125" fetchpriority="high"></picture></div>
  <div class="wrap hero__inner">
    <h1><span class="hero__line"><span>Well dressed,</span></span><span class="hero__line"><span>from the ground up.</span></span></h1>
    <p>Shoes, clothing and accessories for ladies and men. Order on WhatsApp, delivered across South Africa.</p>
    <div class="hero__cta"><a class="btn" href="shop.html?dept=ladies">Shop ladies</a><a class="btn btn--ghost" href="shop.html?dept=mens">Shop mens</a></div>
  </div>
</section>
<section class="sec wrap depts" aria-label="Departments">
  <a class="dept reveal" href="shop.html?dept=ladies"><span class="dept__media"><img src="assets/img/editorial/ladies.webp" alt="Woman in a flowing blush dress and gold sandals crossing a limestone terrace" width="848" height="1264" loading="lazy"></span><span class="dept__cap"><h2>Ladies</h2><span>{sum(p['dept']=='ladies' for p in PRODUCTS)} pieces</span></span></a>
  <a class="dept dept--mens reveal" href="shop.html?dept=mens"><span class="dept__media"><img src="assets/img/editorial/mens.webp" alt="Man in a midnight linen suit and cognac loafers against a blue wall" width="848" height="1264" loading="lazy"></span><span class="dept__cap"><h2>Mens</h2><span>{sum(p['dept']=='mens' for p in PRODUCTS)} pieces</span></span></a>
</section>
<section class="sec" style="padding-top:0" aria-labelledby="new-in">
  <div class="wrap rail-head">
    <h2 class="sec-title" id="new-in">New this season</h2>
    <div class="rail-ctrl">
      <button class="icon-btn" type="button" data-rail="-1" data-target="rail-new" aria-label="Scroll back">{ic('arrow-left')}</button>
      <button class="icon-btn" type="button" data-rail="1" data-target="rail-new" aria-label="Scroll forward">{ic('arrow-right')}</button>
      <a class="link" href="shop.html?tag=new" style="margin-left:10px">See all</a>
    </div>
  </div>
  <div class="rail" id="rail-new" tabindex="0" aria-label="New products">{''.join(card(p, r) for p in rail)}</div>
</section>
<section class="sec wrap" style="padding-top:0" aria-label="Shop by category">
  <div class="bento">
    <a class="bento__cell bento__cell--clothing reveal" href="shop.html?cat=clothing"><span class="bento__media"><img src="assets/img/editorial/clothing.webp" alt="Blush, ivory and navy garments on a brass rail in window light" width="848" height="1264" loading="lazy"></span><span class="bento__cap"><h3>Clothing</h3><span>Linen, satin and tailoring</span></span></a>
    <a class="bento__cell bento__cell--shoes reveal" href="shop.html?cat=shoes"><span class="bento__media"><img src="assets/img/editorial/hero-blush.webp" alt="Gold heels on a stone plinth" width="2200" height="1125" loading="lazy"></span><span class="bento__cap"><h3>Shoes</h3><span>Heels, sandals, loafers and boots</span></span></a>
    <a class="bento__cell bento__cell--acc reveal" href="shop.html?cat=accessories"><span class="bento__media"><img src="assets/img/editorial/accessories.webp" alt="Gold hoops, sunglasses, a silk scarf, a leather belt and a blush bag on pale stone" width="1264" height="848" loading="lazy"></span><span class="bento__cap"><h3>Accessories</h3><span>Bags, gold, belts and shades</span></span></a>
  </div>
</section>
<section class="coast" aria-labelledby="coast-title">
  <img src="assets/img/editorial/coast.webp" alt="Couple walking barefoot on a timber boardwalk towards the Atlantic at golden hour" width="1600" height="893" loading="lazy">
  <div class="wrap coast__inner">
    <h2 id="coast-title">Ready for a South African summer</h2>
    <p>Sandals, linen and light layers for long days at the coast.</p>
    <a class="btn" href="shop.html?tag=summer">Shop summer</a>
  </div>
</section>
<section class="sec wrap how" aria-labelledby="how-title">
  <div>
    <h2 class="sec-title" id="how-title">Ordering takes three steps</h2>
    <a class="btn btn--wa how__wa" href="https://wa.me/{WA}" target="_blank" rel="noopener">{ic('whatsapp-logo')}Chat to us</a>
  </div>
  <ol class="how__steps">
    <li class="how__step"><div><h3>Fill your bag</h3><p>Choose your size and add what you like. Your bag stays saved on your device.</p></div></li>
    <li class="how__step"><div><h3>Send it on WhatsApp</h3><p>Add your delivery details and press send. Your order arrives with us already written out.</p></div></li>
    <li class="how__step"><div><h3>Pay your invoice</h3><p>We confirm stock and send you an invoice. Your parcel goes out as soon as payment reflects.</p></div></li>
  </ol>
</section>
</main>"""
    write("index.html", head(r, "Blush and Blue | Ladies and Mens Clothing, Shoes and Accessories", "Shop shoes, clothing and accessories for ladies and men. Order on WhatsApp and get an invoice, with courier delivery across South Africa.", "", ld=ld).replace('<html lang="en-ZA" data-theme="light">', '<html lang="en-ZA" data-theme="light" class="has-hero">') + top(r, "home") + body + bottom(r))


def shop():
    r = ""
    depts = "".join(f'<button class="chip" type="button" data-filter-dept="{k}" aria-pressed="false">{t}</button>' for k, t in [("all", "All"), ("ladies", "Ladies"), ("mens", "Mens")])
    cats = "".join(f'<button class="chip" type="button" data-filter-cat="{k}" aria-pressed="false">{t}</button>' for k, t in [("all", "Everything"), ("shoes", "Shoes"), ("clothing", "Clothing"), ("accessories", "Accessories")])
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Shop Blush and Blue", "url": SITE + "shop.html", "isPartOf": {"@id": SITE + "#website"},
          "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}products/{p['slug']}.html", "name": p["name"]} for i, p in enumerate(PRODUCTS)]}}
    body = f"""<main id="main">
<div class="wrap page-head"><h1 id="shop-title">The full range</h1></div>
<div class="filters"><div class="wrap filters__row">
  <div class="filter-scroll" role="group" aria-label="Department">{depts}<span class="filter-sep" aria-hidden="true"></span>{cats}</div>
  <div class="filter-tools">
    <div class="field-inline">{ic('magnifying-glass')}<label class="sr" for="shop-search">Search products</label><input class="search-input" id="shop-search" type="search" placeholder="Search" enterkeyhint="search"></div>
    <div class="select-wrap"><label class="sr" for="shop-sort">Sort by</label><select class="select" id="shop-sort"><option value="featured">Featured</option><option value="low">Price: low to high</option><option value="high">Price: high to low</option></select>{ic('caret-down')}</div>
  </div>
</div></div>
<div class="wrap">
  <p class="result-count" id="shop-count" aria-live="polite">{len(PRODUCTS)} pieces</p>
  <div class="grid" id="shop-grid">{''.join(card(p, r, i >= 8) for i, p in enumerate(PRODUCTS))}</div>
  <div class="empty" id="shop-empty" hidden><h3>Nothing matches that</h3><p>Try a different word or clear your filters to see the full range.</p><button class="btn btn--ghost" type="button" id="shop-clear">Clear filters</button></div>
</div>
</main>"""
    write("shop.html", head(r, "Shop Shoes, Clothing and Accessories | Blush and Blue", "Browse the Blush and Blue range: ladies and mens shoes, clothing and accessories, ordered on WhatsApp and delivered across South Africa.", "shop.html", ld=ld) + top(r, "shop") + body + bottom(r))


def product(p):
    r = "../"
    img0 = p["images"][0]
    label = f'{DEPT[p["dept"]]} {CAT[p["cat"]].lower()}'
    colour = p["colours"][0]
    one = len(p["sizes"]) == 1
    url = f"{SITE}products/{p['slug']}.html"
    title = f"{p['name']} | {label.capitalize()} | Blush and Blue"
    desc = f"{p['desc']} {money(p['price'])}. Order on WhatsApp."
    if len(desc) > 200:
        desc = p["desc"]
    ld = {"@context": "https://schema.org", "@graph": [{
        "@type": "Product", "name": p["name"], "description": p["desc"], "sku": "BB-" + p["slug"].upper()[:18], "category": label,
        "image": [f"{SITE}assets/img/products/{i}.webp" for i in p["images"]], "color": colour[0], "brand": {"@type": "Brand", "name": NAME},
        "offers": {"@type": "Offer", "url": url, "priceCurrency": "ZAR", "price": str(p["price"]), "availability": "https://schema.org/InStock", "itemCondition": "https://schema.org/NewCondition", "seller": {"@type": "Organization", "name": NAME}},
    }, {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
        {"@type": "ListItem", "position": 2, "name": DEPT[p["dept"]], "item": f"{SITE}shop.html?dept={p['dept']}"},
        {"@type": "ListItem", "position": 3, "name": p["name"], "item": url},
    ]}]}
    thumbs = ""
    if len(p["images"]) > 1:
        thumbs = '<div class="pdp__thumbs">' + "".join(
            f'<button class="pdp__thumb" type="button" data-thumb="{r}assets/img/products/{i}.webp" data-photo="{1 if i in PHOTOS else 0}" aria-current="{"true" if n == 0 else "false"}" aria-label="View image {n + 1}"><img src="{r}assets/img/products/{i}.webp" alt="" width="86" height="86" loading="lazy"{" class='is-photo'" if i in PHOTOS else ""}></button>'
            for n, i in enumerate(p["images"])) + "</div>"
    sizes = "".join(f'<button class="chip" type="button" data-pick-size="{esc(s)}" aria-pressed="false">{esc(s)}</button>' for s in p["sizes"])
    size_block = "" if one else f"""<div id="size-block">
        <div class="opt-label"><span><b>Size</b> <span id="size-picked"></span></span><a class="link" href="{r}size-guide.html">Size guide</a></div>
        <div class="chips">{sizes}</div>
        <p class="opt-error" id="size-error" role="alert" hidden>Choose a size to add this to your bag.</p>
      </div>"""
    wa_text = f"Hi Blush and Blue, I have a question about the {p['name']}: {url}"
    related = [x for x in PRODUCTS if x["slug"] != p["slug"] and x["cat"] == p["cat"]]
    related = ([x for x in related if x["dept"] == p["dept"]] + [x for x in related if x["dept"] != p["dept"]])[:4]
    photo = ' class="is-photo"' if img0 in PHOTOS else ""
    extra = f'<div class="buybar" id="buybar"><b>{money(p["price"])}</b><button class="btn" type="button" data-add>Add to bag</button></div>'
    body = f"""<main id="main" class="wrap">
<div style="padding-top:18px"><nav aria-label="Breadcrumb"><ol class="crumbs"><li><a href="{r}index.html">Home</a></li><li><a href="{r}shop.html?dept={p['dept']}">{DEPT[p['dept']]}</a></li><li><a href="{r}shop.html?dept={p['dept']}&amp;cat={p['cat']}">{CAT[p['cat']]}</a></li></ol></nav></div>
<section class="pdp" id="pdp" data-slug="{p['slug']}">
  <div class="pdp__gallery">
    <div class="pdp__main"><img{photo} id="pdp-main" src="{r}assets/img/products/{img0}.webp" alt="{esc(p['name'])} in {esc(colour[0].lower())}" width="1000" height="1000" fetchpriority="high"></div>
    {thumbs}
  </div>
  <div class="pdp__info">
    <div>
      <h1>{esc(p['name'])}</h1>
      <p class="pdp__price">{money(p['price'])}</p>
    </div>
    <p class="pdp__desc">{esc(p['desc'])}</p>
    <div class="swatch"><i style="background:{colour[1]}"></i><span>{esc(colour[0])}</span></div>
    {size_block}
    <div class="qty-row">
      <div class="stepper" role="group" aria-label="Quantity">
        <button type="button" data-qty="-1" aria-label="One less">{ic('minus')}</button><output id="qty">1</output><button type="button" data-qty="1" aria-label="One more">{ic('plus')}</button>
      </div>
    </div>
    <div class="pdp__actions" id="add-inline">
      <button class="btn btn--block" type="button" data-add>Add to bag</button>
      <a class="btn btn--ghost btn--block" href="https://wa.me/{WA}?text={esc(__import__('urllib.parse').parse.quote(wa_text))}" target="_blank" rel="noopener">{ic('whatsapp-logo')}Ask about this item</a>
    </div>
    <div>
      <details class="acc" open><summary>Details{ic('caret-down')}</summary><ul>{''.join(f'<li>{esc(d)}</li>' for d in p['details'])}</ul></details>
      <details class="acc"><summary>Delivery{ic('caret-down')}</summary><p>Courier or PostNet across South Africa, free on orders over R 1 500. Your parcel goes out once your invoice is paid. <a class="link" href="{r}delivery-returns.html">Read more</a></p></details>
      <details class="acc"><summary>Returns{ic('caret-down')}</summary><p>Unworn items in their original packaging can be returned within 14 days of delivery. <a class="link" href="{r}delivery-returns.html">Read more</a></p></details>
    </div>
  </div>
</section>
<section class="related" aria-labelledby="rel-title">
  <h2 class="sec-title" id="rel-title">You may also like</h2>
  <div class="grid">{''.join(card(x, r) for x in related)}</div>
</section>
</main>"""
    write(f"products/{p['slug']}.html", head(r, title, desc, f"products/{p['slug']}.html", og=f"assets/img/og/{p['slug']}.jpg", og_alt=f"{p['name']} from Blush and Blue", ld=ld, og_type="product") + top(r, "product") + body + bottom(r, extra))


def checkout():
    r = ""
    provinces = ["Eastern Cape", "Free State", "Gauteng", "KwaZulu-Natal", "Limpopo", "Mpumalanga", "North West", "Northern Cape", "Western Cape"]
    opts = "".join(f"<option>{p}</option>" for p in provinces)
    body = f"""<main id="main" class="wrap">
<div class="page-head"><h1 id="checkout-title">Checkout</h1></div>
<div class="empty" id="checkout-empty" hidden><h3>Your bag is empty</h3><p>Add something to your bag to start an order.</p><a class="btn" href="shop.html">Go to the shop</a></div>
<div class="done" id="checkout-done" hidden>
    <p>WhatsApp has opened with your order written out. It only reaches us once you press send there. We will then confirm stock and send your invoice.</p>
  <p class="done__ref" id="done-ref"></p>
  <div class="done__actions"><a class="btn btn--wa" id="done-open" href="#" target="_blank" rel="noopener">{ic('whatsapp-logo')}Open WhatsApp again</a><a class="btn btn--ghost" href="shop.html">Keep shopping</a></div>
</div>
<div class="checkout" id="checkout-main">
  <form id="checkout-form" novalidate>
    <fieldset class="form-group">
      <legend>Your details</legend>
      <div class="field"><label for="f-name">Full name</label><input id="f-name" name="name" autocomplete="name" required><span class="err" role="alert"></span></div>
      <div class="field"><label for="f-phone">WhatsApp number</label><input id="f-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" required><span class="hint">We will send your invoice to this number.</span><span class="err" role="alert"></span></div>
      <div class="field"><label for="f-email">Email (optional)</label><input id="f-email" name="email" type="email" autocomplete="email" autocapitalize="none"><span class="err" role="alert"></span></div>
    </fieldset>
    <fieldset class="form-group">
      <legend>Delivery</legend>
      <label class="radio"><input type="radio" name="delivery" value="courier" checked><span>Door-to-door courier<small>Delivered to your address, usually 2 to 4 working days</small></span><span id="fee-courier"></span></label>
      <label class="radio"><input type="radio" name="delivery" value="postnet"><span>PostNet to PostNet<small>Collect at your nearest branch, usually 2 to 3 working days</small></span><span id="fee-postnet"></span></label>
      <div id="addr-courier" style="margin-top:18px">
        <div class="field"><label for="f-street">Street address</label><input id="f-street" name="street" autocomplete="street-address"><span class="err" role="alert"></span></div>
        <div class="field"><label for="f-suburb">Suburb (optional)</label><input id="f-suburb" name="suburb" autocomplete="address-level3"><span class="err" role="alert"></span></div>
        <div class="field-2">
          <div class="field"><label for="f-city">Town or city</label><input id="f-city" name="city" autocomplete="address-level2"><span class="err" role="alert"></span></div>
          <div class="field"><label for="f-postcode">Postal code</label><input id="f-postcode" name="postcode" inputmode="numeric" autocomplete="postal-code"><span class="err" role="alert"></span></div>
        </div>
        <div class="field"><label for="f-province">Province</label><select id="f-province" name="province" autocomplete="address-level1"><option value="">Select a province</option>{opts}</select><span class="err" role="alert"></span></div>
      </div>
      <div id="addr-postnet" style="margin-top:18px" hidden>
        <div class="field"><label for="f-branch">Nearest PostNet branch</label><input id="f-branch" name="branch"><span class="err" role="alert"></span></div>
      </div>
    </fieldset>
    <fieldset class="form-group" style="margin-bottom:0">
      <legend>Anything else?</legend>
      <div class="field"><label for="f-notes">Order notes (optional)</label><textarea id="f-notes" name="notes"></textarea></div>
    </fieldset>
    <button class="btn btn--wa btn--block send-btn" type="submit">{ic('whatsapp-logo')}Send order on WhatsApp</button>
    <p class="consent">Pressing this opens WhatsApp with your order written out. By sending it you agree to our <a class="link" href="terms.html">terms</a> and <a class="link" href="privacy.html">privacy policy</a>. You pay only once you have your invoice.</p>
  </form>
  <aside class="summary" aria-label="Order summary">
    <h2>Your order</h2>
    <ul id="sum-lines"></ul>
    <div class="sum-row"><span>Subtotal</span><span id="sum-sub"></span></div>
    <div class="sum-row"><span>Delivery</span><span id="sum-del"></span></div>
    <div class="sum-row sum-row--total"><span>Total</span><span id="sum-total"></span></div>
  </aside>
</div>
</main>"""
    write("checkout.html", head(r, "Checkout | Blush and Blue", "Send your Blush and Blue order on WhatsApp and we will send you an invoice.", "checkout.html", noindex=True) + top(r, "checkout") + body + bottom(r))


def prose(path, title, h1, desc, content, intro=""):
    r = ""
    inner = f'<p>{intro}</p>' if intro else ""
    body = f'<main id="main" class="wrap"><div class="page-head"><h1>{h1}</h1>{inner}</div><div class="prose">{content}</div></main>'
    write(path, head(r, title, desc, path) + top(r, path) + body + bottom(r))


def pages():
    wa_link = f'<a href="https://wa.me/{WA}" target="_blank" rel="noopener">WhatsApp {PHONE_DISPLAY}</a>'
    prose("privacy.html", "Privacy Policy | Blush and Blue", "Privacy policy", "How Blush and Blue collects, uses and protects your personal information under POPIA.", f"""
<p>Last updated: {UPDATED}</p>
<p>This policy explains how Blush and Blue ("we", "us") collects, uses and protects your personal information, in line with the Protection of Personal Information Act 4 of 2013 (POPIA).</p>
<h2>Who we are</h2>
<ul><li><strong>Business:</strong> Blush and Blue, South Africa</li><li><strong>WhatsApp and calls:</strong> {PHONE_DISPLAY}</li><li><strong>Website:</strong> obsidianstudiodesigns.github.io/Blush-and-Blue</li></ul>
<p>The owner of Blush and Blue is our Information Officer under POPIA. Contact them on the number above about anything in this policy.</p>
<h2>What we collect</h2>
<p>We only collect the information you choose to give us when you order or ask a question:</p>
<ul><li>your name and cellphone number (WhatsApp shares your number with us when you message us)</li><li>your email address, if you add one</li><li>your delivery address or PostNet branch</li><li>the products, sizes and quantities in your order</li><li>anything you add in a note</li></ul>
<h2>How the bag and checkout work</h2>
<p>Your bag and your Blush or Blue theme choice are saved in your own browser's storage on your device. They are not cookies and they are not sent to us. You can clear them by clearing this site's data in your browser.</p>
<p>The checkout does not send anything to us by itself. When you press "Send order on WhatsApp", WhatsApp opens with your order already written. Nothing reaches us unless you send that message yourself.</p>
<h2>Why we use it</h2>
<ul><li>to confirm stock and send your invoice</li><li>to arrange delivery and tell you when your parcel is on its way</li><li>to answer your questions and handle returns</li><li>to keep the records the law requires</li></ul>
<p>We do not sell, rent or trade your personal information. We only send you specials if you ask us to.</p>
<h2>Who we share it with</h2>
<p>We share only what is needed to deliver your order, such as your name, number and address with the courier or PostNet. WhatsApp is run by WhatsApp LLC, and its own privacy policy applies to messages sent through it.</p>
<h2>How long we keep it</h2>
<p>We keep order and invoice records for as long as tax and consumer law require, usually five years, and delete or anonymise what we no longer need.</p>
<h2>Your rights</h2>
<p>You may ask to see the information we hold about you, ask us to correct or delete it, or object to how we use it. Contact us on {wa_link}. You may also complain to the Information Regulator of South Africa at <a href="https://inforegulator.org.za/" target="_blank" rel="noopener">inforegulator.org.za</a>.</p>
<h2>Website hosting and fonts</h2>
<p>This website is hosted on GitHub Pages, which may keep standard technical logs such as IP addresses to keep the service secure. We load our fonts from this site, and we do not use advertising or analytics cookies.</p>
""")
    prose("terms.html", "Terms and Conditions | Blush and Blue", "Terms and conditions", "The terms that apply when you order from Blush and Blue.", f"""
<p>Last updated: {UPDATED}</p>
<p>These terms apply when you use this website or order from Blush and Blue. They do not limit your rights under the Consumer Protection Act 68 of 2008 or the Electronic Communications and Transactions Act 25 of 2002.</p>
<h2>How an order works</h2>
<p>Sending your bag on WhatsApp is a request to buy, not a completed sale. We confirm stock and send an invoice. The sale is concluded when you pay that invoice, and we dispatch once payment reflects.</p>
<h2>Prices and availability</h2>
<p>Prices are in South African rand. The price on your invoice is the one that applies. If an item is out of stock or a price on the site is clearly wrong, we will tell you before you pay, and you may cancel at no cost.</p>
<h2>Payment</h2>
<p>Payment details appear on your invoice. Please use your order reference when you pay. Invoices that are not paid within 48 hours may lapse so that stock can be released.</p>
<h2>Delivery</h2>
<p>We deliver across South Africa by courier or PostNet. See <a href="delivery-returns.html">delivery and returns</a> for fees and timing. Delivery dates are estimates, and we will let you know of any significant delay.</p>
<h2>Returns and faulty goods</h2>
<p>You may return unworn items within 14 days of delivery. Faulty goods may be returned for a repair, replacement or refund within six months, as the Consumer Protection Act provides. The full process is on our <a href="delivery-returns.html">delivery and returns</a> page.</p>
<h2>Using this website</h2>
<p>Photos are as accurate as we can make them, but colours may look slightly different on your screen. The content on this site belongs to Blush and Blue and may not be reused without permission.</p>
<h2>Contact and law</h2>
<p>South African law applies to these terms. Questions are welcome on {wa_link}.</p>
""")
    prose("delivery-returns.html", "Delivery and Returns | Blush and Blue", "Delivery and returns", "Courier and PostNet delivery fees, timing and how returns work at Blush and Blue.", f"""
<h2>Delivery</h2>
<ul><li><strong>Door-to-door courier:</strong> R 120, usually 2 to 4 working days</li><li><strong>PostNet to PostNet:</strong> R 109, usually 2 to 3 working days</li><li><strong>Free delivery</strong> on orders over R 1 500</li></ul>
<p>Parcels go out once your invoice has been paid. We will send you tracking details on WhatsApp.</p>
<h2>Returns</h2>
<p>Changed your mind or need another size? Unworn items with their packaging can be returned within 14 days of delivery. Message us first on {wa_link} with your order reference, and we will arrange an exchange or refund.</p>
<p>Unless an item is faulty, the cost of sending it back is yours. For hygiene reasons, earrings cannot be returned unless faulty.</p>
<h2>Faulty items</h2>
<p>If something arrives damaged or develops a fault within six months, let us know and we will repair, replace or refund it, including the cost of returning it to us.</p>
""")
    write("size-guide.html", head("", "Size Guide | Blush and Blue", "Shoe and clothing size conversions for ladies and men at Blush and Blue.", "size-guide.html") + top("", "size-guide.html") + f"""<main id="main" class="wrap">
<div class="page-head"><h1>Size guide</h1><p>Between sizes? Message us on WhatsApp and we will help you choose. For shoes, go up a size if you are between two.</p></div>
<div class="size-tables">
  <div><h2>Ladies shoes</h2><table class="size-table"><thead><tr><th>SA / UK</th><th>EU</th><th>Foot length</th></tr></thead><tbody>
    <tr><td>3</td><td>36</td><td>23 cm</td></tr><tr><td>4</td><td>37</td><td>23.5 cm</td></tr><tr><td>5</td><td>38</td><td>24 cm</td></tr><tr><td>6</td><td>39</td><td>25 cm</td></tr><tr><td>7</td><td>40</td><td>25.5 cm</td></tr><tr><td>8</td><td>41</td><td>26.5 cm</td></tr></tbody></table></div>
  <div><h2>Mens shoes</h2><table class="size-table"><thead><tr><th>SA / UK</th><th>EU</th><th>Foot length</th></tr></thead><tbody>
    <tr><td>6</td><td>40</td><td>25 cm</td></tr><tr><td>7</td><td>41</td><td>26 cm</td></tr><tr><td>8</td><td>42</td><td>26.5 cm</td></tr><tr><td>9</td><td>43</td><td>27.5 cm</td></tr><tr><td>10</td><td>44</td><td>28 cm</td></tr><tr><td>11</td><td>45</td><td>29 cm</td></tr></tbody></table></div>
  <div><h2>Ladies clothing</h2><table class="size-table"><thead><tr><th>Size</th><th>SA</th><th>Bust</th><th>Waist</th></tr></thead><tbody>
    <tr><td>XS</td><td>30</td><td>80 cm</td><td>62 cm</td></tr><tr><td>S</td><td>32</td><td>85 cm</td><td>67 cm</td></tr><tr><td>M</td><td>34</td><td>90 cm</td><td>72 cm</td></tr><tr><td>L</td><td>36</td><td>96 cm</td><td>78 cm</td></tr><tr><td>XL</td><td>38</td><td>102 cm</td><td>84 cm</td></tr></tbody></table></div>
  <div><h2>Mens clothing</h2><table class="size-table"><thead><tr><th>Size</th><th>Chest</th><th>Waist</th></tr></thead><tbody>
    <tr><td>S</td><td>92 cm</td><td>78 cm</td></tr><tr><td>M</td><td>98 cm</td><td>84 cm</td></tr><tr><td>L</td><td>104 cm</td><td>90 cm</td></tr><tr><td>XL</td><td>110 cm</td><td>96 cm</td></tr><tr><td>XXL</td><td>116 cm</td><td>102 cm</td></tr></tbody></table></div>
</div></main>""" + bottom(""))
    ld = {"@context": "https://schema.org", **{k: v for k, v in ORG.items()}}
    write("contact.html", head("", "Contact | Blush and Blue", f"Chat to Blush and Blue on WhatsApp or call {PHONE_DISPLAY} about sizing, stock or your order.", "contact.html", ld=ld) + top("", "contact.html") + f"""<main id="main" class="wrap">
<div class="page-head"><h1>Talk to us</h1><p>Ask about sizing, stock or an order you have placed.</p></div>
<div class="contact-grid">
  <div class="contact-card"><h2>WhatsApp</h2><p>The fastest way to reach us. It is also how every order is placed.</p><a class="btn btn--wa" href="https://wa.me/{WA}" target="_blank" rel="noopener">{ic('whatsapp-logo')}{PHONE_DISPLAY}</a></div>
  <div class="contact-card"><h2>Call</h2><p>Prefer to speak to someone? Give us a ring on the same number.</p><a class="btn btn--ghost" href="tel:{PHONE_INTL}">{ic('phone')}{PHONE_DISPLAY}</a></div>
</div></main>""" + bottom(""))
    base = SITE
    write("404.html", head(base, "Page not found | Blush and Blue", "This page could not be found.", "404.html", noindex=True) + top(base, "404") + f"""<main id="main" class="wrap notfound"><h1>This page has moved on</h1><p>The link may be old. The full range is one click away.</p><div><a class="btn" href="{base}shop.html">Go to the shop</a></div></main>""" + bottom(base))


def og_images():
    out = ROOT / "assets/img/og"
    out.mkdir(parents=True, exist_ok=True)
    W, H = 1200, 630
    mono = Image.open(ROOT / "assets/img/brand/monogram-on-dark.png")
    word = Image.open(ROOT / "assets/img/brand/wordmark-on-dark.png")
    MIDNIGHT = (11, 19, 36)
    # Home card: the Blue hero with the logo in its empty left side
    hero = Image.open(ROOT / "assets/img/editorial/hero-blue.webp").convert("RGB")
    s = max(W / hero.width, H / hero.height)
    hero = hero.resize((round(hero.width * s), round(hero.height * s)), Image.LANCZOS)
    c = hero.crop((hero.width - W, hero.height - H, hero.width, hero.height)).convert("RGBA")
    m = mono.copy(); m.thumbnail((250, 170), Image.LANCZOS)
    wd = word.copy(); wd.thumbnail((470, 60), Image.LANCZOS)
    c.alpha_composite(m, (70 + (470 - m.width) // 2, 180))
    c.alpha_composite(wd, (70, 180 + m.height + 40))
    c.convert("RGB").save(out / "home.jpg", quality=86, optimize=True)
    # Product cards: photo on blush, logo on midnight
    tile = (243, 224, 219)
    for p in PRODUCTS:
        c = Image.new("RGBA", (W, H), MIDNIGHT + (255,))
        ph = Image.open(ROOT / f"assets/img/products/{p['images'][0]}.webp").convert("RGB").resize((H, H), Image.LANCZOS)
        if p["images"][0] not in PHOTOS:
            ph = ImageChops.multiply(Image.new("RGB", (H, H), tile), ph)
        c.paste(ph, (W - H, 0))
        m = mono.copy(); m.thumbnail((210, 150), Image.LANCZOS)
        wd = word.copy(); wd.thumbnail((430, 50), Image.LANCZOS)
        left = W - H
        c.alpha_composite(m, ((left - m.width) // 2, 215))
        c.alpha_composite(wd, ((left - wd.width) // 2, 215 + m.height + 34))
        c.convert("RGB").save(out / f"{p['slug']}.jpg", quality=84, optimize=True)


def meta_files():
    data = [{k: p[k] for k in ("slug", "name", "dept", "cat", "price", "colours", "sizes", "images")} for p in PRODUCTS]
    write("assets/js/products.js", "window.BB_PRODUCTS=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")
    urls = ["", "shop.html", "contact.html", "size-guide.html", "delivery-returns.html", "privacy.html", "terms.html"] + [f"products/{p['slug']}.html" for p in PRODUCTS]
    sm = "".join(f"<url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /tools/\nDisallow: /checkout.html\n\nSitemap: {SITE}sitemap.xml\n")
    write("site.webmanifest", json.dumps({
        "name": NAME, "short_name": NAME, "description": "Ladies and mens clothing, shoes and accessories. Order on WhatsApp.",
        "start_url": "./", "scope": "./", "display": "standalone", "background_color": "#0b1324", "theme_color": "#0b1324",
        "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"}, {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}],
    }, indent=2))
    write(".nojekyll", "")


if __name__ == "__main__":
    home(); shop(); checkout(); pages()
    for p in PRODUCTS:
        product(p)
    meta_files(); og_images()
    print("built", len(PRODUCTS), "products")
