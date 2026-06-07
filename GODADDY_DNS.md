# GoDaddy DNS → Netlify (roseempire.co.uk)

Use this **after** your site is uploaded to Netlify.

Replace `YOUR-SITE-NAME` below with your actual Netlify site name  
(e.g. if your link is `https://rose-empire-wholesale.netlify.app`, use `rose-empire-wholesale`).

---

## Before you start

1. Site is **Published** on Netlify
2. In Netlify → **Domain management** → already added:
   - `roseempire.co.uk`
   - `www.roseempire.co.uk`
3. **Screenshot** all GoDaddy DNS records first (backup)

---

## Step 1 — Log into GoDaddy

1. Go to **[https://dcc.godaddy.com](https://dcc.godaddy.com)** (or godaddy.com → Sign In)
2. **My Products**
3. Find **roseempire.co.uk** → click **DNS** (or **Manage DNS**)

You should see a table: Type | Name | Value | TTL

---

## Step 2 — Turn OFF GoDaddy forwarding (if on)

If you see **Forwarding** section with a website URL:

- **Remove** or **Turn off** domain forwarding  
- Otherwise it overrides Netlify

Email forwarding is OK to keep if you use it.

---

## Step 3 — Keep EMAIL records (do not delete)

Find records with type **MX** — they look like:

| Type | Name | Value |
|------|------|--------|
| MX | @ | mailstore1.secureserver.net (example) |
| MX | @ | smtp.secureserver.net (example) |

**Leave all MX records exactly as they are.**

Also keep **TXT** records used for email (SPF), e.g.:

| Type | Name | Value |
|------|------|--------|
| TXT | @ | v=spf1 include:secureserver.net ... |

Do **not** delete these.

---

## Step 4 — Fix the ROOT domain (@)

Find existing **A** record where **Name** is `@`:

| Old (GoDaddy parking) | New (Netlify) |
|-------------------------|---------------|
| Points to GoDaddy IP e.g. `184.168.131.1` | **`75.2.60.5`** |

**Action:** Click **Edit** (pencil) on the `@` A record → change **Value** to:

```
75.2.60.5
```

TTL: **1 Hour** (or default)

If there is **no** A record for `@`, click **Add** → **A**:

| Field | Value |
|-------|--------|
| Type | A |
| Name | @ |
| Value | 75.2.60.5 |
| TTL | 1 Hour |

> Netlify may show a different IP in your dashboard — if so, use **Netlify’s IP**, not this one.

---

## Step 5 — Set up WWW

Find **CNAME** where **Name** is `www`:

**Edit** it to:

| Field | Value |
|-------|--------|
| Type | CNAME |
| Name | www |
| Value | `YOUR-SITE-NAME.netlify.app` |
| TTL | 1 Hour |

Example: `rose-empire-wholesale.netlify.app`

**Important:** Only the site name — **no** `https://` and **no** trailing slash.

If no `www` CNAME exists → **Add** → **CNAME** with values above.

---

## Step 6 — Remove conflicts (optional)

Delete or edit these **only if they exist** and point to old parking/hosting:

- Extra **A** records on `@` (keep only one → Netlify IP)
- **CNAME** on `@` (GoDaddy rarely allows this — if present, remove per GoDaddy/Netlify docs)

Do **not** delete MX or email TXT records.

Click **Save** / changes save automatically on GoDaddy.

---

## Step 7 — Verify in Netlify

1. Netlify → **Domain management**
2. Wait 15–60 minutes (sometimes up to 48h)
3. Both domains should show **Verified** + **HTTPS** enabled
4. **Set primary domain:** `www.roseempire.co.uk` → **Set as primary**

---

## Step 8 — Test

| Test | Expected |
|------|----------|
| https://www.roseempire.co.uk | Your Rose Empire site |
| https://roseempire.co.uk | Redirects to www (or works) |
| Send email **to** info@roseempire.co.uk | Still arrives |
| Send email **from** info@roseempire.co.uk | Still sends |
| Quote PDF on live site | Downloads |

---

## GoDaddy + Netlify quick reference

| Type | Name | Points to | Purpose |
|------|------|-----------|---------|
| **A** | @ | `75.2.60.5` | Website (root) |
| **CNAME** | www | `YOUR-SITE-NAME.netlify.app` | Website (www) |
| **MX** | @ | *(unchanged)* | Email |
| **TXT** | @ | *(unchanged)* | Email SPF |

---

## Troubleshooting GoDaddy

**“Site not found” after 24h**

- Confirm CNAME value is exactly `yoursite.netlify.app`
- Confirm only one A record on `@` → Netlify IP
- Disable **Forwarding** in GoDaddy

**Email stopped working**

- Restore MX records from screenshot
- GoDaddy Support → “Restore DNS” or re-add MX from **Email & Office** product settings

**Netlify says “Pending DNS verification”**

- GoDaddy DNS can take 1–2 hours
- In Netlify → Domain management → **Verify DNS configuration**

**SSL / HTTPS not working**

- Wait until DNS is verified; Netlify auto-issues certificate (can take 24h after DNS)

---

## GoDaddy email (info@roseempire.co.uk)

If email is **GoDaddy Professional Email** or **Microsoft 365 from GoDaddy**, MX records stay on GoDaddy servers — website DNS changes above do not affect them if MX is untouched.

---

## Need the exact Netlify CNAME?

Paste your Netlify URL in Cursor, e.g.:

`https://rose-empire-wholesale.netlify.app`

We’ll fill in Step 5 for you word-for-word.
