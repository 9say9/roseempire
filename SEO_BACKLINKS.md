# SEO backlinks checklist (owned actions only)

Honest, owned actions for Rose Empire wholesale indexing — **no spam link schemes, PBNs, or paid link farms**.

## Weekly checklist (Adeel — ~15 minutes)

Run every Monday. Tick in a notes file or spreadsheet.

1. **Google Search Console** — open Pages / Coverage. Note any new 404s or “Crawled – currently not indexed”. If money pages or `sitemap.xml` changed this week, resubmit `https://www.roseempire.co.uk/sitemap.xml`. URL Inspection (Test live URL, then Request indexing if stale) on:
   - `https://www.roseempire.co.uk/`
   - `https://www.roseempire.co.uk/wholesale-mattress-protectors.html`
   - `https://www.roseempire.co.uk/wholesale-pillows.html`
   - `https://www.roseempire.co.uk/hotels.html`
   - `https://www.roseempire.co.uk/care-homes.html`
2. **Bing Webmaster Tools** — import/verify if needed, then resubmit the same sitemap after a GSC resubmit. Spot-check the five URLs.
3. **Google Business Profile** — website still `https://www.roseempire.co.uk`; NAP matches 5 Sagar Street, Manchester M8 8EU, `+44 7999 988450`; category Bedding supplier / Wholesaler; hours Mon–Fri 09:00–17:00. Reply to real questions only. **Do not add fake reviews.**
4. **LinkedIn Company Page** — website field is `https://www.roseempire.co.uk` on [Rose Empire Wholesale Home Textiles](https://www.linkedin.com/company/rose-empire-wholesale-home-textiles). Optional: one true trade post (stock, catalog, hotel/care offer) — no invented ratings.
5. **2–3 UK B2B / hospitality directories** — confirm the listings you already claimed are live and NAP-identical. Do not buy bulk links.

Done when: sitemap last-read date is current, money URLs show “URL is on Google” (or indexing requested), GBP + LinkedIn website match the canonical.

See `SMOKE_SEO.md` for the after-deploy URL Inspection steps.

## First-time submit & verify

1. **Google Search Console** — verify `https://www.roseempire.co.uk` (if not already), submit `https://www.roseempire.co.uk/sitemap.xml`.
2. **Bing Webmaster Tools** — import GSC or verify, submit the same sitemap.
3. **Google Business Profile** — claim/update Manchester NAP (5 Sagar Street, M8 8EU), set website to `https://www.roseempire.co.uk`.

## Brand / company profiles (website field only)

4. **LinkedIn Company Page** — confirm website URL is `https://www.roseempire.co.uk`; keep About text en-GB and trade-focused (no fake review counts).
5. Optional: **Companies House** filing / website field if applicable for the trading entity.

## UK B2B / hospitality directories (2–3 quality listings)

Pick **two or three** reputable UK B2B or hospitality directories where you already qualify; use real NAP and the canonical site URL. Examples of *owned* listing types (create/claim only — do not buy bulk links):

- A UK hospitality buyer directory or hotel-supplier listing (e.g. regional hospitality association supplier page).
- A care / facilities management supplier directory used by NHS/care procurement teams (only if membership or free claim is legitimate).
- A Manchester / North West business directory with editorial review (chamber of commerce or Invest in Manchester style listing).

For each listing: same business name, address, phone `+44 7999 988450`, email `info@roseempire.co.uk`, website `https://www.roseempire.co.uk`.

## Do not do

- Guest-post / marketplace link packages, PBNs, forum spam, or reciprocal “link exchange” blasts.
- Fake aggregate ratings or review schema.
- Creating eBay listings solely for backlinks.

## After deploy

- Re-fetch sitemap in GSC/Bing; confirm HTTP 200 (not 5xx).
- Spot-check money-page titles/meta in rich results tester; Product `@id` should match homepage anchors (`#product-wqmp`, `#product-pillow-feather-down`).
- Follow `SMOKE_SEO.md`.
