# Blush and Blue

Sample online store for Blush and Blue: ladies and mens clothing, shoes and accessories in South Africa.
Shoppers fill a bag and check out on WhatsApp. The business confirms stock and sends an invoice.

Live: https://obsidianstudiodesigns.github.io/Blush-and-Blue/

Static site, no build step on the server. Hosted on GitHub Pages from `main`.

## Load the real range
1. Replace the entries in `tools/catalogue.json`.
2. Put square product photos in `assets/img/products/` named after each image in the catalogue (`.webp`).
3. Run `python tools/build.py` (needs Pillow). It rewrites every page, the sitemap and each product's WhatsApp preview image.
4. Remove the "Preview catalogue" line in the footer in `tools/build.py`.

Site by [Obsidian Studio Designs](https://obsidianstudiodesigns.co.za/).
