# Connect roseempire.co.uk + keep info@roseempire.co.uk email

Your partner owns the **domain** and **email**. The **website** still needs to be uploaded to free hosting (Netlify), then the domain is pointed at it.

**Important:** Website and email use **different DNS records**. You can add the website without breaking email — **do not delete MX records**.

---

## What you need from your partner (5 minutes)

Ask them for:

1. **Where the domain was bought** — e.g. 123-reg, GoDaddy, Namecheap, Ionos, Cloudflare, etc.
2. **Login** to that account (or ask them to add DNS records — see Step 3)
3. **Confirm email works** — can they send/receive at `info@roseempire.co.uk` already?

---

## Step 1 — Deploy the website (free, ~10 min)

### A. Create the zip

1. Open `C:\Users\ADLSH\Documents\antigravity`
2. Select these only:
   - `index.html`, `styles.css`, `app.js`, `site-config.js`
   - `quote-pricing.js`, `quote-shipping.js`, `quote-pdf.js`
   - `robots.txt`, `sitemap.xml`, `404.html`
   - folder **`assets`**
3. Right-click → **Send to** → **Compressed (zipped) folder**

Do **not** include `linkedin-outreach`.

### B. Upload to Netlify

1. Go to **[https://app.netlify.com](https://app.netlify.com)** → sign up (free)
2. **Add new site** → **Deploy manually** → upload the zip
3. Wait until status is **Published**
4. Test the temporary link (e.g. `https://xyz.netlify.app`) — products, quote, PDF

---

## Step 2 — Add your domain in Netlify

1. Netlify → your site → **Domain management**
2. **Add a domain** → enter: `roseempire.co.uk` → Verify
3. **Add domain alias** → enter: `www.roseempire.co.uk`
4. Netlify shows **DNS instructions** — keep this page open

Netlify will want something like:

| Type | Name | Value |
|------|------|--------|
| **A** | `@` (or blank) | `75.2.60.5` |
| **CNAME** | `www` | `your-site-name.netlify.app` |

*(IPs can change — always use the values Netlify shows you, not this table.)*

---

## Step 3 — Update DNS at your domain registrar

Log in where **roseempire.co.uk** was purchased → **DNS** / **Manage DNS**.

### DO NOT TOUCH (email keeps working)

Leave these **exactly as they are**:

- **MX** records (mail delivery)
- **TXT** records for email (SPF, DKIM, DMARC if present)

If you're unsure, take a screenshot of all DNS records **before** changing anything.

### ADD or UPDATE (website only)

**For `www.roseempire.co.uk`:**

| Type | Host | Points to |
|------|------|-----------|
| CNAME | `www` | `your-site-name.netlify.app` |

**For `roseempire.co.uk` (no www):**

| Type | Host | Points to |
|------|------|-----------|
| A | `@` | Netlify’s IP (from Netlify dashboard) |

Some registrars use **ANAME/ALIAS** instead of A for the root — follow Netlify’s instructions for your registrar.

### Remove conflicts (if any)

- Delete old **A** or **CNAME** on `@` or `www` that point to a parking page or old host
- **Never delete MX records**

Save DNS. Propagation can take **15 minutes to 48 hours** (often under 1 hour).

---

## Step 4 — HTTPS (automatic)

Netlify issues a free SSL certificate once DNS is correct. In **Domain management**, wait until both domains show **HTTPS enabled**.

Your site will work at:

- **https://www.roseempire.co.uk**
- **https://roseempire.co.uk** (Netlify redirects one to the other — pick primary in Netlify settings)

---

## Step 5 — Set primary domain in Netlify

**Domain management** → **Options** on `www.roseempire.co.uk` → **Set as primary domain**

Recommended: use **`https://www.roseempire.co.uk`** as primary (matches what’s already in your site code).

---

## Step 6 — Test everything

- [ ] https://www.roseempire.co.uk loads with padlock
- [ ] Product images show
- [ ] Quote cart + PDF download works
- [ ] **Email still works** — send a test to and from `info@roseempire.co.uk`
- [ ] Phone links and mailto on site open correctly

---

## Step 7 — LinkedIn + Google

1. **LinkedIn profile** → Contact info → Website: `https://www.roseempire.co.uk`
2. **LinkedIn Post Inspector:** [linkedin.com/post-inspector](https://www.linkedin.com/post-inspector/) → paste URL → check preview image
3. **Google Search Console** (optional): add property + submit `https://www.roseempire.co.uk/sitemap.xml`

---

## Email FAQ

| Question | Answer |
|----------|--------|
| Do we pay for website hosting? | **No** — Netlify free tier is enough |
| Do we pay for email? | Whatever your partner already pays the registrar/email provider |
| Will the website break email? | **No**, if you only change A/CNAME for web and leave **MX** alone |
| Quote form — does email arrive automatically? | The site opens the user’s email app with a draft to `info@roseempire.co.uk`. They must click **Send**. You receive it in the inbox your partner set up. |

---

## If something breaks

**Website not loading**

- Wait up to 24h for DNS
- Check Netlify **Domain management** for DNS verification errors
- Confirm A/CNAME match Netlify exactly

**Email stopped working**

- Restore **MX** records from screenshot / registrar support
- Contact registrar — say you only added website A/CNAME records

**Partner’s registrar**

If you tell Cursor the registrar name (e.g. “123-reg”), steps can be narrowed to that panel’s exact clicks.

---

## Your site is already configured for this domain

These are already set in your code:

- `info@roseempire.co.uk`
- `+44 7999 988450`
- `https://www.roseempire.co.uk` in SEO, LinkedIn links, and quote PDFs

No code changes needed — just deploy + DNS.
