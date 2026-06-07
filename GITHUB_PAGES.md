# Rose Empire — GitHub Pages hosting

**Live preview:** https://9say9.github.io/roseempire/  
**Custom domain (after DNS):** https://www.roseempire.co.uk  
**Repo:** https://github.com/9say9/roseempire

---

## Deploy site changes

```powershell
git add .
git commit -m "Update site"
git push origin main
```

Or double-click **`deploy-github.bat`**.

GitHub Pages rebuilds in 1–2 minutes. No Netlify required.

---

## Point roseempire.co.uk at GitHub (GoDaddy)

Open **`GODADDY_LIVE_NOW.html`** in your browser — partner checklist with exact DNS values.

| Type | Name | Value |
|------|------|--------|
| **A** | @ | `185.199.108.153` (+ `.109`, `.110`, `.111` if GoDaddy allows) |
| **CNAME** | www | `9say9.github.io` |

Remove old Netlify records: A `75.2.60.5`, CNAME `say9.netlify.app`.

**Do not delete** MX / TXT (email).

GitHub Pages settings: https://github.com/9say9/roseempire/settings/pages  
Custom domain should show **www.roseempire.co.uk**.

---

## Alex & Sarah chat (replaces Netlify function)

GitHub Pages is static — chat runs on a **free Cloudflare Worker**:

1. `npm install -g wrangler` then `wrangler login`
2. Double-click **`deploy_chat_worker.bat`**
3. `wrangler secret put GEMINI_API_KEY` (paste key from `.env`)
4. Copy the `*.workers.dev` URL into **`site-config.js`** → `cloudflareChatApi`
5. Run **`deploy-github.bat`** to publish

Local testing: **`start_chat_server.bat`** → http://127.0.0.1:5000

---

## Leave Netlify

1. Update GoDaddy DNS (above)
2. Confirm https://www.roseempire.co.uk loads from GitHub
3. Netlify → **Domain management** → remove `roseempire.co.uk` / `www` from site **say9** (optional)

Netlify deploy scripts (`deploy-live.bat`, `netlify deploy`) are no longer used.
