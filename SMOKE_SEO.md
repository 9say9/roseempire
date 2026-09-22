# Smoke-check SEO after deploy

Use this after GitHub Pages (or CDN) has the new commit live. Takes about 10 minutes.

## 1. Live HTML (View Source)

Open each money URL and confirm:

| URL | Title / H1 check | Must not contain |
| --- | --- | --- |
| `/` | Hotels & care in title; H1 includes UK | vacuum-pack pillows; fake star ratings |
| `/wholesale-mattress-protectors.html` | WQMP / QMP / Terry | invented review counts |
| `/wholesale-pillows.html` | cotton zip-bag | vacuum-only packing |
| `/hotels.html` | protectors & pillows | — |
| `/care-homes.html` | OEKO-TEX / care protectors | “tier discounts (50+ / 200+)” |

Also confirm on each page:

- `rel="canonical"` is the `https://www.roseempire.co.uk/...` URL for that page
- `hreflang="en-gb"` and `hreflang="x-default"`
- JSON-LD has **no** `aggregateRating`
- WQMP Product `@id` is `https://www.roseempire.co.uk/#product-wqmp`
- Pillow Product `@id` is `https://www.roseempire.co.uk/#product-pillow-feather-down`
- Phone CTAs use `tel:+447999988450` / display `+44 7999 988450`

`https://www.roseempire.co.uk/robots.txt` should allow `/` and list `Sitemap: https://www.roseempire.co.uk/sitemap.xml`.
`https://www.roseempire.co.uk/sitemap.xml` should return HTTP 200.

## 2. Google Search Console — URL Inspection

For each of the five money URLs:

1. Paste the full `https://www.roseempire.co.uk/...` URL into **URL Inspection**.
2. Click **Test live URL**.
3. Check: page allowed, canonical matches, detected title/description match View Source.
4. If the **indexed** version is older than this deploy, click **Request indexing**.

Then **Sitemaps** → submit or resubmit `https://www.roseempire.co.uk/sitemap.xml`.

## 3. Optional rich-results check

[Rich Results Test](https://search.google.com/test/rich-results) on `/` (FAQPage + Product) and `/wholesale-pillows.html` (Product). Expect **no** review stars.

## Pass

Live HTML matches this repo; GSC live test shows the new title; sitemap HTTP 200; indexing requested if the cached version was stale.

Bing: same five URLs + sitemap if GSC was updated (`SEO_BACKLINKS.md` weekly list).
