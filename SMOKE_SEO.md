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
| `/holiday-lets.html` | holiday lets / student / B&B | invented social handles |
| `/student-accommodation.html` | student / PBSA / halls protectors | invented delivery promises |

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

Bing: same money URLs + sitemap if GSC was updated (`SEO_BACKLINKS.md` weekly list).

## 4. IndexNow (optional, after deploy)

1. Confirm the key file is live: `https://www.roseempire.co.uk/f8c2a19e4b3d6075ae9210c4d5e6f7a8.txt` (HTTP 200, body = key only).
2. From repo root (operator only — do not run in CI): `node scripts/indexnow-ping.js`  
   Submits all `<loc>` URLs from `sitemap.xml` to `https://api.indexnow.org/indexnow` with `host=www.roseempire.co.uk`.
3. Or pass explicit URLs: `node scripts/indexnow-ping.js https://www.roseempire.co.uk/student-accommodation.html`

## 5. Local link check (before commit)

`node scripts/check-internal-links.js` — verifies every local `href`/`src` in HTML files resolves on disk.
