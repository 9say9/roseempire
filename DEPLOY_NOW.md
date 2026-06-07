# Deploy NOW — follow these steps in order

## STEP 1 — Upload (you should see Netlify Drop + your zip file)

1. Browser opened: **https://app.netlify.com/drop**
2. If asked → **Sign up free** (Google or email)
3. **Drag** `rose-empire-website-deploy.zip` onto the Netlify page
4. Wait ~30 seconds → site is **Published**

## STEP 2 — Copy your Netlify link

After upload you'll see a URL like:

`https://random-words-123.netlify.app`

**Open it** — test products + quote PDF.

Then rename it:

1. **Site configuration** → **Domain management** → **Options** → **Edit site name**
2. Try: `rose-empire-wholesale`  
   → `https://rose-empire-wholesale.netlify.app`

---

## STEP 3 — Add your real domain

**Domain management** → **Add a domain** → type:

```
roseempire.co.uk
```

Then **Add domain alias**:

```
www.roseempire.co.uk
```

Netlify shows DNS records. **Screenshot that page** — your partner needs it.

Typical records (yours may differ — use Netlify's values):

| Type | Host / Name | Value |
|------|-------------|--------|
| **A** | `@` | `75.2.60.5` |
| **CNAME** | `www` | `rose-empire-wholesale.netlify.app` |

---

## STEP 4 — Partner updates DNS (5 min)

Partner logs into **where domain was bought** → **DNS** / **Manage DNS**

### ADD / UPDATE (website):
- **A** record: `@` → Netlify IP from Step 3
- **CNAME**: `www` → your `*.netlify.app` site name

### DO NOT DELETE:
- **MX** records (keeps info@roseempire.co.uk working)
- **TXT** records for email (SPF/DKIM)

Save → wait 15 min to 2 hours.

---

## STEP 5 — Set primary domain

Back in Netlify → **Domain management** → on `www.roseempire.co.uk` → **Set as primary**

Wait for **HTTPS** green check on both domains.

**Live site:** https://www.roseempire.co.uk

---

## STEP 6 — Quick test

- [ ] Site loads with padlock
- [ ] Add 20 pieces to quote → PDF downloads
- [ ] Email test: send to info@roseempire.co.uk and reply

---

## Stuck?

Reply in Cursor with:
- Your Netlify URL after upload, OR
- Registrar name (GoDaddy, 123-reg, etc.)

We'll do exact DNS clicks for that provider.
