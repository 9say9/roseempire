# Rose Empire — Go Live & LinkedIn Connection Guide

Use this checklist before pointing **roseempire.co.uk** at your site.

---

## Pre-launch audit (done in code)

| Item | Status |
|------|--------|
| SEO meta title & description | ✅ |
| Open Graph / LinkedIn link preview image | ✅ `assets/og-share.png` |
| JSON-LD structured data (Google + rich results) | ✅ |
| LinkedIn URL in footer, top bar & nav | ✅ |
| `sameAs` LinkedIn in schema | ✅ |
| Favicon | ✅ `assets/favicon.png` |
| `robots.txt` + `sitemap.xml` | ✅ |
| Mobile navigation menu | ✅ |
| Clickable phone & email | ✅ |
| 404 page | ✅ `404.html` |
| Quote cart, pricing, shipping, PDF | ✅ |

---

## Step 1 — Upload website files

Upload **everything** in this folder to your web host document root:

```
C:\Users\ADLSH\Documents\antigravity\
```

Required files:
- `index.html`, `styles.css`, `app.js`
- `site-config.js`, `quote-pricing.js`, `quote-shipping.js`, `quote-pdf.js`
- `robots.txt`, `sitemap.xml`, `404.html`
- `assets/` folder (all images)

**Do not upload** `linkedin-outreach/` — that folder is for your local sales scripts only.

### Host setup tips

- Enable **HTTPS** (free via Let's Encrypt on most hosts)
- Set **404** to `/404.html` (cPanel → Error Pages, or Netlify/Vercel auto-detect)
- Enable **gzip/brotli** compression if available
- Optional: add a CDN (Cloudflare free tier) for faster UK delivery

---

## Step 2 — Connect domain roseempire.co.uk

1. In your domain registrar, point **A record** or **CNAME** to your host
2. Wait for DNS propagation (up to 24–48 hours)
3. Open `https://www.roseempire.co.uk` and verify:
   - Homepage loads with images
   - Add a product → quote cart → PDF downloads
   - Email draft opens after submit

---

## Step 3 — Connect website ↔ LinkedIn

### A. On your LinkedIn profile (personal)

Follow **`linkedin-outreach/LINKEDIN_PROFILE_EDIT_GUIDE.md`**:

1. Set **Website** in Contact Info → `https://www.roseempire.co.uk`
2. Add **Featured** link → Rose Empire Wholesale Catalog → same URL
3. Use banner/logo from `linkedin-outreach/profile-assets/`
4. Publish the launch post linking to the site

### B. Create LinkedIn Company Page (recommended)

1. LinkedIn → **For Business** → **Create a Company Page**
2. Name: **Rose Empire Wholesale Home Textiles**
3. Website: `https://www.roseempire.co.uk`
4. Logo: `profile-assets/linkedin-logo-rose-empire.png`
5. Banner: `profile-assets/linkedin-banner-rose-empire.png`
6. Copy About text from the profile edit guide

### C. Update your LinkedIn URL on the website (if slug differs)

After creating the company page, LinkedIn gives you a URL like:
`https://www.linkedin.com/company/your-actual-slug`

Update it in **two places**:

1. **`site-config.js`** → `linkedInCompanyUrl`
2. **`index.html`** → search for `linkedin.com/company` (top bar, nav, footer, JSON-LD)

Or tell Cursor to update once you have the final URL.

### D. Verify link preview on LinkedIn

1. Go to [LinkedIn Post Inspector](https://www.linkedin.com/post-inspector/)
2. Enter `https://www.roseempire.co.uk`
3. Click **Inspect** — you should see title, description, and banner image

If the image does not appear, wait 24h after going live and inspect again.

### E. Google Search Console (optional but recommended)

1. Add property `https://www.roseempire.co.uk`
2. Submit sitemap: `https://www.roseempire.co.uk/sitemap.xml`

---

## Step 4 — Post-launch smoke test

Run through this on your phone and desktop:

- [ ] Homepage loads over HTTPS (padlock in browser)
- [ ] All product images visible
- [ ] Search & category filters work
- [ ] Add 50+ pieces → 10% discount shows
- [ ] Change shipping region → logistics updates
- [ ] Submit quote → PDF downloads + email opens
- [ ] LinkedIn links open your company page
- [ ] Mobile menu opens/closes
- [ ] Share site URL on LinkedIn → preview looks correct

---

## Known limitations (by design)

| Topic | Notes |
|-------|--------|
| **Quote submission** | No server — PDF downloads locally + opens email client. You receive quotes at info@roseempire.co.uk when buyers send them. |
| **Pricing** | Cart uses £25/piece baseline for estimates; product cards show size-specific unit prices. Final pricing confirmed by sales team. |
| **Image file sizes** | Product PNGs are ~600KB each. Consider compressing via [squoosh.app](https://squoosh.app) if load feels slow. |
| **Facebook / Instagram** | Removed placeholder `#` links — only LinkedIn is linked until you add other profiles. |

---

## Sales flow after launch

1. Finish LinkedIn profile + company page
2. Post launch announcement with site link
3. Run `linkedin-outreach/run_draft_messages.bat`
4. Send 5–10 connection requests per day (manual — do not auto-send)

---

## Quick support contacts on site

- **Phone:** +44 7999 988450  
- **Email:** info@roseempire.co.uk  
- **LinkedIn:** [Rose Empire company page](https://www.linkedin.com/company/rose-empire-wholesale-home-textiles)
