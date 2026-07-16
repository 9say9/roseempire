# Rose Empire Wholesale

Public wholesale website for [roseempire.co.uk](https://www.roseempire.co.uk) — catalog, quote cart, Stripe checkout, and Sarah AI chat.

## Do not break (live site)

These rules keep payments and chat working:

1. **Checkout URL** — `site-config.js` must stay on the live Cloudflare worker  
   `https://rose-empire-checkout.adeelcolchester.workers.dev` (local preview uses the same URL).
2. **Cart + Sarah** — when the quote cart is open, Sarah is hidden on purpose. Do not remove `body.cart-drawer-open` hiding of `#sarah-widget` or live checkout buttons stop receiving clicks.
3. **Secrets** — never commit `.env`, Stripe `sk_` / `pk_` keys, or Sarah admin tokens. Tokens live only in Cloudflare secrets.
4. **Pages deploy** — only the public `site/` allowlist is published; do not change the workflow to deploy the whole repo.
5. **Cache bust** — after cart/checkout/CSS/JS fixes, bump `?v=` on assets in `index.html`.

After any live change:

```powershell
py -3 scripts/check_secrets.py
py -3 scripts/check_site_config.py
py -3 scripts/smoke_live.py
```

## Local run

1. Optional: copy `.env.example` → `.env` only if you want the local Flask Stripe path (test keys). Default local preview still uses the live checkout worker via `site-config.js`.
2. Double-click `START_LOCAL.bat`, or:

```powershell
py -3 -m pip install -r requirements.txt
py -3 server.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Sarah chat

The site loads Sarah from the Cloudflare worker:

`https://rose-empire-sarah.adeelcolchester.workers.dev`

Owner mode uses an admin token stored only in Cloudflare secrets — never commit that token to git. Rotate it if it was ever published.

A yellow floating grammar dot in the browser is usually a **browser extension** (e.g. QuillBot), not Sarah. Sarah is the black/gold chat orb.

## Stripe (live)

1. Deploy the checkout worker only when intentionally updating it (secrets must already be set):

```powershell
cd cloudflare\checkout-worker
npm install
npx wrangler secret put STRIPE_SECRET_KEY
npx wrangler deploy
```

2. Confirm `site-config.js` still points at `rose-empire-checkout.adeelcolchester.workers.dev`.

Checkout totals include volume discount, UK logistics, and 20% VAT (same rules as the on-page estimate). Payment confirmation webhooks are not wired yet — treat success as acknowledgment and confirm orders by email.

## Deploy (GitHub Pages)

Push to `main`. The workflow scans secrets, validates catalog + site-config URLs, copies only public site files into `site/`, and deploys that folder.
