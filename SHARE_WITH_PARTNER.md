# Share the Rose Empire website with your partner (before go-live)

Your site is static files on your PC — it is **not** on the internet yet until you upload it. Pick **one** option below.

---

## Option 1 — Netlify Drop (best if your partner is elsewhere)

**Free preview link in ~2 minutes. Works anywhere in the world.**

1. Open File Explorer → go to:
   ```
   C:\Users\ADLSH\Documents\antigravity
   ```
2. Select these files/folders (hold Ctrl and click each):
   - `index.html`
   - `styles.css`
   - `app.js`
   - `site-config.js`
   - `quote-pricing.js`
   - `quote-shipping.js`
   - `quote-pdf.js`
   - `robots.txt`
   - `sitemap.xml`
   - `404.html`
   - the whole **`assets`** folder
3. Right-click → **Send to** → **Compressed (zipped) folder**
4. Go to **[https://app.netlify.com/drop](https://app.netlify.com/drop)** in Chrome/Edge
5. Drag the `.zip` file onto the page
6. Netlify gives you a link like `https://random-name-123.netlify.app` — **send that to your partner**

They can open it on phone or laptop. No account required for a quick drop (you may be asked to sign up to keep the link longer — free tier is fine).

**Tip:** Test the quote PDF and cart on the preview link before you share it.

---

## Option 2 — Same WiFi / same house

If your partner is on the **same internet** as you:

1. Double-click **`share_preview.bat`** in this folder
2. A window shows a link like `http://192.168.x.x:8765`
3. Send that link to your partner (WhatsApp, text, etc.)
4. They open it on their phone/laptop **while your PC is on** and the window is open

**Does not work** if they are at a different location.

---

## Option 3 — Temporary public link from your PC (advanced)

If Netlify Drop is not an option and your partner is remote:

1. Run **`share_preview.bat`**
2. Install **[ngrok](https://ngrok.com/download)** (free account)
3. In a new terminal:
   ```
   ngrok http 8765
   ```
4. Copy the `https://....ngrok-free.app` URL and send it to your partner

Your PC must stay on while they browse.

---

## What to tell your partner to check

- Homepage and product images load
- Search and category filters work
- Open a product → add to quote (try **20 pieces**)
- Proceed to quote → fill form → download PDF
- Mobile view (open link on phone)
- LinkedIn links in footer (company page may 404 until you create it — that’s OK)

---

## After partner approval → go live

Follow **`GO_LIVE_CHECKLIST.md`** to upload to **roseempire.co.uk**.

The Netlify preview link is **temporary** — your real domain replaces it when you deploy.
