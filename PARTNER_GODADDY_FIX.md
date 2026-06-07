# FIX NOW — GoDaddy DNS for roseempire.co.uk

**Your website is LIVE here:** https://say9.netlify.app  
**Your domain still shows GoDaddy "Launching Soon"** — DNS must be updated once.

Give this sheet to your partner (GoDaddy login required).  
**~10 minutes. Email will keep working if they follow exactly.**

---

## What’s already done ✓

- Rose Empire website uploaded to Netlify
- Live preview: **https://say9.netlify.app**
- Email uses **Microsoft 365** (`info@roseempire.co.uk`) — MX must not be deleted

---

## What’s wrong now ✗

| URL | Shows |
|-----|--------|
| https://say9.netlify.app | ✓ Your real website |
| https://www.roseempire.co.uk | GoDaddy “Launching Soon” placeholder |
| https://roseempire.co.uk | Same placeholder |

Domain DNS still points to **GoDaddy Website Builder**, not Netlify.

---

## PART 1 — You (Netlify) — 2 minutes

1. Log in: https://app.netlify.com/projects/say9
2. **Domain management** → **Add a domain** → `roseempire.co.uk`
3. **Add domain alias** → `www.roseempire.co.uk`
4. Leave that page open — it shows DNS instructions

---

## PART 2 — Partner (GoDaddy) — copy these EXACT values

### Login

1. https://dcc.godaddy.com
2. **My Products** → **roseempire.co.uk** → **DNS**

### A) Turn OFF GoDaddy website / forwarding

- Find **Forwarding** or **Website Builder** / **Coming Soon**
- **Delete** or **Turn off** website forwarding for roseempire.co.uk
- This is why visitors see “Launching Soon”

### B) DO NOT DELETE (email — Microsoft 365)

Keep these records **unchanged**:

| Type | Name | Value |
|------|------|--------|
| **MX** | @ | `roseempire-co-uk.mail.protection.outlook.com` |
| **TXT** | @ | `v=spf1 include:secureserver.net -all` |
| **TXT** | @ | `NETORGFT20747441.onmicrosoft.com` |

### C) CHANGE website records

**1. A record (root domain)**

Edit the **A** record where Name = `@`:

| Field | Value |
|-------|--------|
| Type | A |
| Name | @ |
| Value | **`75.2.60.5`** |
| TTL | 1 Hour |

Delete any **second** A record on `@` that points to GoDaddy (e.g. `13.248.243.5` or `76.223.105.230`).

**2. CNAME record (www)**

Edit or add **CNAME** where Name = `www`:

| Field | Value |
|-------|--------|
| Type | CNAME |
| Name | www |
| Value | **`say9.netlify.app`** |
| TTL | 1 Hour |

No `https://` — just `say9.netlify.app`

### D) Save

GoDaddy saves automatically. Wait **30–90 minutes**.

---

## PART 3 — After DNS propagates

1. Netlify → **Domain management** → wait for **Verified** + **HTTPS**
2. **Set primary domain:** `www.roseempire.co.uk`
3. Test:
   - https://www.roseempire.co.uk → Rose Empire site
   - Email to/from info@roseempire.co.uk still works

---

## Quick test commands (optional)

After 1 hour, these should show Netlify (not GoDaddy parking):

- `www.roseempire.co.uk` → CNAME to `say9.netlify.app`
- `roseempire.co.uk` → A record `75.2.60.5`

---

## Share with customers NOW

While waiting for DNS, use:

**https://say9.netlify.app**

Same site — works worldwide today.

---

## If stuck

Send a **screenshot** of the full GoDaddy DNS table (hide passwords) — we can say exactly which rows to edit.

Netlify project: https://app.netlify.com/projects/say9
