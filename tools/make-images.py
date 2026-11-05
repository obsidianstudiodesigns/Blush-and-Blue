"""Turn workspace product photos and generated editorial photos into web assets."""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "Products"
GEN = ROOT / "tools/source-images"
PROD = ROOT / "assets/img/products"
ED = ROOT / "assets/img/editorial"
P = "WhatsApp Image 2026-11-05 at "

def whiten(im, floor=None):
    """Push a light studio backdrop to pure white and fade the edges, so it melts into the blush tile."""
    a = np.asarray(im.convert("RGB"), dtype=float)
    h, w, _ = a.shape
    k = max(8, w // 40)
    corners = [a[:k, :k], a[:k, -k:], a[-k:, :k], a[-k:, -k:]]
    auto = min(float(np.median(x)) for x in corners)
    floor = min(floor or 255, max(auto - 3, 200))
    a = np.clip(a * (255.0 / floor), 0, 255)
    band = max(1, w // 14)
    ramp = lambda n: np.minimum(np.minimum(np.arange(n), np.arange(n)[::-1]) / band, 1)
    mask = np.outer(ramp(h), ramp(w))[..., None]
    bright = np.clip((a.min(axis=2, keepdims=True) - 205) / 35, 0, 1)  # only the backdrop fades, never skin or product
    mask = 1 - (1 - mask) * bright
    a = a * mask + 255 * (1 - mask)
    return Image.fromarray(a.astype("uint8"))

def square(im, size=1000):
    w, h = im.size
    s = min(w, h)
    im = im.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2))
    if s < size:
        im = im.resize((size, size), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.6, 60, 2))
    elif s > size:
        im = im.resize((size, size), Image.LANCZOS)
    return im

WORKSPACE = {
    "sahara-slingback-sandal": ("12.14.11 (1).jpeg", 232, (150, 250, 1040, 1140)),
    "noir-twist-t-strap": ("12.14.11.jpeg", 252, None),
    "onyx-ring-thong": ("12.14.12.jpeg", 248, None),
    "onyx-ring-thong-2": ("12.14.12 (1).jpeg", None, None),
    "savanna-leopard-flip-flop": ("12.14.12 (2).jpeg", 248, None),
    "lagoon-ring-t-strap": ("12.14.13 (1).jpeg", 252, (20, 40, 880, 900)),
    "gilt-band-thong": ("12.14.13 (2).jpeg", 245, (0, 90, 372, 462)),
    "rose-dune-flip-flop": ("12.14.13.jpeg", None, (0, 0, 540, 540)),
}
for slug, (name, floor, box) in WORKSPACE.items():
    im = Image.open(SRC / (P + name)).convert("RGB")
    if box:
        im = im.crop(box)
    if floor:
        im = whiten(im, floor)
    square(im).save(PROD / f"{slug}.webp", quality=82, method=6)

def web(name, out, width, q=78):
    im = Image.open(GEN / f"{name}.png").convert("RGB")
    h = round(im.height * width / im.width)
    resample = im.resize((width, h), Image.LANCZOS)
    if width > im.width:
        resample = resample.filter(ImageFilter.UnsharpMask(1.4, 50, 2))
    resample.save(ED / f"{out}.webp", quality=q, method=6)

def hero_wide(name, lift=1.0):
    """Add mirrored backdrop on the left so the shoes clear the headline on wide screens."""
    im = Image.open(GEN / f"{name}.png").convert("RGB")
    pad = 420
    wide = Image.new("RGB", (im.width + pad, im.height))
    wide.paste(im.crop((0, 0, pad, im.height)).transpose(Image.FLIP_LEFT_RIGHT), (0, 0))
    wide.paste(im, (pad, 0))
    h = round(wide.height * 2200 / wide.width)
    wide = wide.resize((2200, h), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.4, 40, 2))
    if lift != 1.0:
        wide = ImageEnhance.Brightness(wide).enhance(lift)
    wide.save(ED / f"{name}.webp", quality=80, method=6)
    print(name, wide.size)

hero_wide("hero-blush", 1.07)
hero_wide("hero-blue")
m = Image.open(GEN / "hero-blush-m.png").convert("RGB")
ImageEnhance.Brightness(m).enhance(1.07).save(ED / "hero-blush-m.webp", quality=78, method=6)
web("hero-blue-m", "hero-blue-m", 848, 78)
for n, w in [("ladies", 848), ("mens", 848), ("clothing", 848), ("accessories", 1264), ("coast", 1600)]:
    web(n, n, w)

FLOOR = {"aurelia-strappy-heel": 228}
for f in GEN.glob("p-*"):
    im = Image.open(f).convert("RGB")
    if f.stem == "p-midnight-tailored-chino":  # Canva added a text panel on the left; keep only the trousers, recentred
        clean = Image.new("RGB", im.size, (255, 255, 255))
        clean.paste(im.crop((510, 0, 1080, 1080)), (510 - 180, 0))
        im = clean
    square(whiten(im, FLOOR.get(f.stem[2:], 248))).save(PROD / f"{f.stem[2:]}.webp", quality=82, method=6)
print(sum(p.stat().st_size for p in ED.glob("*")) // 1024, "KB editorial", len(list(PROD.glob("*"))), "products")
