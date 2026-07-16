# Rose Empire Wholesale

Public wholesale website for [roseempire.co.uk](https://www.roseempire.co.uk) — catalog, quote cart, Stripe checkout, and Sarah AI chat.

## Local run

1. Copy `.env.example` → `.env` and set real Stripe **test** keys (`sk_test_…` / `pk_test_…`).
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

## Stripe (live)

1. Deploy the checkout worker:

```powershell
cd cloudflare\checkout-worker
npm install
npx wrangler secret put STRIPE_SECRET_KEY
npx wrangler deploy
```

2. Confirm `site-config.js` points at your worker URL (default: `rose-empire-checkout.adeelcolchester.workers.dev`).

Checkout totals include volume discount, UK logistics, and 20% VAT (same rules as the on-page estimate). Payment confirmation webhooks are not wired yet — treat success as acknowledgment and confirm orders by email.

## Deploy (GitHub Pages)

Push to `main`. The workflow copies only public site files into `site/` and deploys that folder.
