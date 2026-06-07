# Put Rose Empire live for FREE

Your website is **static** (HTML/CSS/JS only) — no server, no database, no monthly hosting bill.

---

## What is free vs what costs money

| Item | Cost |
|------|------|
| **Hosting** (Netlify, Cloudflare Pages, GitHub Pages, Vercel) | **£0 / month** |
| **HTTPS** (padlock in browser) | **Free** included |
| **Preview URL** e.g. `rose-empire.netlify.app` | **Free** |
| **Domain** `roseempire.co.uk` | **~£8–15 / year** (only if you buy/register it) |

You can go live **today at £0** using a free `.netlify.app` or `.pages.dev` address.  
Connect `roseempire.co.uk` later when you buy the domain — still **no hosting fee**.

---

## Easiest method — Netlify (recommended)

You already used Netlify Drop for your partner. Same thing, but keep the site permanently.

### Step 1 — Zip the site

1. Open `C:\Users\ADLSH\Documents\antigravity`
2. Select (Ctrl+click):
   - `index.html`, `styles.css`, `app.js`, `site-config.js`
   - `quote-pricing.js`, `quote-shipping.js`, `quote-pdf.js`
   - `robots.txt`, `sitemap.xml`, `404.html`
   - folder **`assets`**
3. Right-click → **Send to** → **Compressed (zipped) folder**

**Do not include** `linkedin-outreach` (sales scripts — keep on your PC only).

### Step 2 — Deploy

1. Go to **[https://app.netlify.com](https://app.netlify.com)** → sign up free (email or Google)
2. **Add new site** → **Deploy manually** (or drag zip on [netlify.com/drop](https://app.netlify.com/drop))
3. Upload your zip
4. You get a live URL like: `https://lucky-name-123456.netlify.app`

**That URL is live on the internet.** Send it to customers, LinkedIn, etc.

### Step 3 — Rename the free URL (optional)

Netlify → **Site configuration** → **Domain management** → **Options** → **Edit site name**

Pick something like: `rose-empire-wholesale.netlify.app`

### Step 4 — Connect roseempire.co.uk (when you own the domain)

1. Buy the domain from [Namecheap](https://www.namecheap.com), [123-reg](https://www.123-reg.co.uk), or your registrar
2. Netlify → **Domain management** → **Add custom domain** → enter `roseempire.co.uk`
3. Netlify shows DNS records — copy them into your domain registrar
4. Wait 1–24 hours — HTTPS is automatic and free

---

## Alternative — Cloudflare Pages (also 100% free)

1. Sign up at **[https://dash.cloudflare.com](https://dash.cloudflare.com)**
2. **Workers & Pages** → **Create** → **Pages** → **Upload assets**
3. Upload the same zip
4. Live at `https://rose-empire.pages.dev` (you can rename)

Good if you later buy the domain through Cloudflare (often at cost price).

---

## Alternative — GitHub Pages (free, slightly more technical)

1. Create a free GitHub account
2. New repository → upload site files
3. Settings → Pages → deploy from `main` branch
4. Live at `https://yourusername.github.io/repo-name`

---

## After you go live — update 2 things

### 1. LinkedIn

Set website to your new live URL (Netlify or custom domain).

### 2. Site files (only if using free Netlify URL for now)

If your live URL is **not** `https://www.roseempire.co.uk` yet, search `index.html` and `site-config.js` for `roseempire.co.uk` — social previews and canonical URLs can stay as-is until the domain is connected (Netlify will redirect when domain is added).

When `roseempire.co.uk` is connected, no code change needed if DNS points to Netlify.

---

## Free tier limits (you will be fine)

- **Bandwidth:** hundreds of GB/month free — plenty for a B2B catalog
- **Quote PDF:** runs in the visitor’s browser — no server cost
- **No credit card** required on Netlify/Cloudflare free plans

---

## Quick checklist

- [ ] Zip site files (no `linkedin-outreach`)
- [ ] Upload to Netlify or Cloudflare Pages
- [ ] Open live URL — test products, quote cart, PDF download
- [ ] Share link with partner
- [ ] Add URL to LinkedIn profile
- [ ] Buy `roseempire.co.uk` when ready → connect in Netlify (still £0 hosting)

---

## Need help?

Tell Cursor: *“Walk me through Netlify deploy”* or *“Update site for my Netlify URL: https://....netlify.app”*
