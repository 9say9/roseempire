# Switch Stripe account (Rose Empire)

Live checkout uses **only** the Cloudflare Worker secret `STRIPE_SECRET_KEY`.  
No Stripe keys are stored in the public website HTML/JS.

Worker: `https://rose-empire-checkout.adeelcolchester.workers.dev`

---

## 1. New Stripe account — get keys

1. Log into the **new** Stripe account (live mode)
2. [API keys](https://dashboard.stripe.com/apikeys) → copy **Secret key** (`sk_live_…`)
3. (Optional for local Flask only) also copy **Publishable key** (`pk_live_…`)

Do **not** commit keys to git or paste them into chat.

---

## 2. Put the new secret on the checkout worker

```powershell
cd "d:\rose empire main\cloudflare\checkout-worker"
npx wrangler secret put STRIPE_SECRET_KEY
```

Paste the **new** `sk_live_…` when prompted (old key is overwritten).

---

## 3. Webhook on the **new** account (required for order emails/WhatsApp)

1. New Stripe → [Webhooks](https://dashboard.stripe.com/webhooks) → **Add endpoint**
2. URL:

   `https://rose-empire-checkout.adeelcolchester.workers.dev/api/stripe/webhook`

3. Event: `checkout.session.completed`
4. Copy signing secret (`whsec_…`)

```powershell
cd "d:\rose empire main\cloudflare\checkout-worker"
npx wrangler secret put STRIPE_WEBHOOK_SECRET
```

Paste the **new** `whsec_…`.

If you also keep a **Test mode** webhook on the same URL, set its signing secret separately:

```powershell
npx wrangler secret put STRIPE_WEBHOOK_SECRET_TEST
```

---

## 4. New account settings (do once)

- [Customer emails](https://dashboard.stripe.com/settings/emails) → **Successful payments** ON  
- [Business details / branding](https://dashboard.stripe.com/settings/business) filled in  
- [Notifications](https://dashboard.stripe.com/settings/notifications) → payment emails to your inbox ON  

---

## 5. Remove the **old** Stripe account completely

On the **old** Stripe Dashboard:

1. Webhooks → delete the Rose Empire checkout endpoint (if any)
2. Do not use old `sk_live_` / `whsec_` anywhere again
3. If Zapier was connected to old Stripe → disconnect / reconnect to the **new** account

Local machine (if you ever used `.env`):

```text
STRIPE_SECRET_KEY=sk_live_NEW...
STRIPE_PUBLISHABLE_KEY=pk_live_NEW...
```

There is currently **no** committed `.env` in the repo (only `.env.example` placeholders).

---

## 6. Verify

```powershell
Invoke-RestMethod "https://rose-empire-checkout.adeelcolchester.workers.dev/health"
Invoke-RestMethod "https://rose-empire-checkout.adeelcolchester.workers.dev/api/checkout/config"
```

Both should show Stripe ready / configured.

Then place a small **live** test order (or £0.30 test) on https://www.roseempire.co.uk and confirm:

- Money lands in the **new** Stripe account  
- Customer receipt email arrives  
- Your Zapier / WhatsApp alert fires (if `ZAPIER_WEBHOOK_URL` is set)

---

## What you do **not** need to change

- `site-config.js` (same worker URL)
- Website HTML/JS (no embedded Stripe keys)
- Redeploy worker code (unless you also change code)

Only secrets + new-account webhook + old-account cleanup.
