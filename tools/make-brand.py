"""Cut the monogram and wordmark out of Logo.jpeg and build every brand asset."""
from pathlib import Path
from PIL import Image, ImageChops
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
logo = Image.open(ROOT / "Logo.jpeg").convert("RGB")
OUT = ROOT / "assets/img/brand"
MIDNIGHT = np.array([13, 22, 41], dtype=float)  # --blue-ink, the logo's ivory on blush

def cut(box, dark_ink=None):
    """Return RGBA from a black-background crop: luminance becomes alpha, colour is un-premultiplied."""
    a = np.asarray(logo.crop(box), dtype=float)
    alpha = a.max(axis=2) / 255.0
    alpha = np.clip((alpha - 0.06) / 0.86, 0, 1)
    rgb = np.where(alpha[..., None] > 0.01, a / np.maximum(a.max(axis=2, keepdims=True), 1) * 255, 0)
    sat = (a.max(axis=2) - a.min(axis=2)) / np.maximum(a.max(axis=2), 1)
    if dark_ink is not None:  # ivory strokes turn midnight, gold strokes deepen so they hold on blush
        gold = sat > 0.16
        rgb = np.where(gold[..., None], np.array([116.0, 82.0, 36.0]), dark_ink)
    out = np.dstack([rgb, alpha * 255]).astype("uint8")
    im = Image.fromarray(out, "RGBA")
    return im.crop(im.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox())

MONO = (440, 100, 1100, 515)
WORD = (90, 570, 1460, 700)
cut(MONO).save(OUT / "monogram-on-dark.png", optimize=True)
cut(MONO, MIDNIGHT).save(OUT / "monogram-on-light.png", optimize=True)
cut(WORD).resize((1000, int(1000 * cut(WORD).height / cut(WORD).width)), Image.LANCZOS).save(OUT / "wordmark-on-dark.png", optimize=True)
w = cut(WORD, MIDNIGHT)
w.resize((1000, int(1000 * w.height / w.width)), Image.LANCZOS).save(OUT / "wordmark-on-light.png", optimize=True)

# App icons: gold and ivory monogram on the midnight of the Blue theme.
mono = cut(MONO)
def icon(size, pad=0.17, bg=(13, 22, 41, 255)):
    c = Image.new("RGBA", (size, size), bg)
    box = int(size * (1 - 2 * pad))
    m = mono.copy(); m.thumbnail((box, box), Image.LANCZOS)
    c.alpha_composite(m, ((size - m.width) // 2, (size - m.height) // 2))
    return c
for name, size, pad in [("icon-192.png", 192, .17), ("icon-512.png", 512, .17), ("apple-touch-icon.png", 180, .16), ("icon-maskable-512.png", 512, .26)]:
    icon(size, pad).convert("RGB").save(ROOT / name, optimize=True)
icon(256, .10).save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
icon(96, .10).convert("RGB").save(ROOT / "favicon-96.png", optimize=True)
