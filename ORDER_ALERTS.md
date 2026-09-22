# Rose Empire — order alerts (email + WhatsApp + CRM)

When a customer pays on the website, Stripe hits our checkout worker webhook. The worker then:

1. Builds an order summary (items, total, delivery address, boxes)
2. POSTs it to your **Zapier Catch Hook** → Email + WhatsApp
3. Optionally emails you via **Resend** if `RESEND_API_KEY` is set
4. POSTs the **full paid order** to Company HQ CRM (`/api/crm/orders/ingest`)

RFQ / enquiry leads still use the separate lead ingest (`CRM_INGEST_URL`). Paid orders must not go through that lead-shaped body.

Webhook URL (already in the worker):

`https://rose-empire-checkout.adeelcolchester.workers.dev/api/stripe/webhook`

---

## 1. Stripe webhook (required)

### Live mode (production orders)

1. Open [Stripe Webhooks](https://dashboard.stripe.com/webhooks) (**live** mode)
2. **Add endpoint** → paste the URL above
3. Listen to: **`checkout.session.completed`**
4. Copy **Signing secret** (`whsec_…`)
5. Save it on the worker:

```powershell
cd "d:\rose empire main\cloudflare\checkout-worker"
npx wrangler secret put STRIPE_WEBHOOK_SECRET
```

### Test mode (sandbox / “Send test webhook”)

Stripe Test mode uses a **different** signing secret. If you keep a Test endpoint on the same URL, also set:

```powershell
cd "d:\rose empire main\cloudflare\checkout-worker"
npx wrangler secret put STRIPE_WEBHOOK_SECRET_TEST
```

Paste the **Test** endpoint signing secret (`whsec_…` from Stripe → Test mode → Webhooks).

Optional (only if you run test Checkout and need line-item expand):

```powershell
npx wrangler secret put STRIPE_SECRET_KEY_TEST
```

Paste `sk_test_…`.

Check readiness:

```powershell
Invoke-RestMethod "https://rose-empire-checkout.adeelcolchester.workers.dev/health"
```

You want `webhook_secret_set: true`. For Test webhooks also `webhook_test_secret_set: true`.

If you do **not** need Test webhooks, delete the Test endpoint in Stripe Dashboard instead — that also stops the failure emails.
---

## 2. Zapier Zap (email + WhatsApp)

### Create Catch Hook

1. [zapier.com](https://zapier.com) → Create Zap
2. Trigger: **Webhooks by Zapier** → **Catch Hook**
3. Copy the Custom Webhook URL (`https://hooks.zapier.com/hooks/catch/...`)
4. Save on the worker:

```powershell
cd "d:\rose empire main\cloudflare\checkout-worker"
npx wrangler secret put ZAPIER_WEBHOOK_URL
```

### Action A — Email to you

- **Email by Zapier** → Send Outbound Email  
  **or** Gmail / Outlook → Send Email  
- To: `info@roseempire.co.uk`  
- Subject: map field `email_subject`  
- Body: map field `email_body`

### Action B — WhatsApp

- **WhatsApp Notifications** → Send Message  
  (or WhatsApp Business / Twilio WhatsApp if you already use that)  
- Message: map field `whatsapp_message`

Turn the Zap **ON**.

### Fields the worker sends

| Field | Use |
|--------|-----|
| `email_subject` | Email subject |
| `email_body` | Full email text |
| `whatsapp_message` | Ready WhatsApp text |
| `amount_formatted` | e.g. £123.45 |
| `customer_email` | Buyer email |
| `customer_name` | Buyer name |
| `shipping` | Address object |
| `line_items` | Product lines |
| `metadata` | boxes, region, postcode, etc. |
| `session_id` | Stripe session id |

---

## 3. Company HQ CRM (paid orders)

HQ is adding `POST /api/crm/orders/ingest` (sibling repo `rose-empire-company-hq`). The checkout worker posts the paid order there **in parallel** with Zapier and Resend. Do **not** remove Zapier/Resend.

### Worker secrets

```powershell
cd "d:\rose empire main\cloudflare\checkout-worker"
npx wrangler secret put CRM_ORDERS_INGEST_URL
npx wrangler secret put CRM_INGEST_TOKEN
```

Example URL (replace with the live HQ host):

`https://<hq-host>/api/crm/orders/ingest`

Auth (same as lead ingest): send the token as both `X-CRM-Token` and `Authorization: Bearer`.

### Fallback if you only have the HQ base URL

If `CRM_ORDERS_INGEST_URL` is unset, the worker can derive the orders path from `CRM_INGEST_URL`:

| `CRM_INGEST_URL` value | Orders POST goes to |
|------------------------|---------------------|
| `https://<hq-host>` (base / origin only) | `https://<hq-host>/api/crm/orders/ingest` |
| `https://<hq-host>/api/crm/ingest` or `/api/crm/leads/ingest` | rewritten to `/api/crm/orders/ingest` |
| already `/api/crm/orders/ingest` | used as-is |
| any other path | **skipped** — set `CRM_ORDERS_INGEST_URL` explicitly |

The lead endpoint (`notifyCrmIngest` on `/api/rfq`) is unchanged: it still POSTs the lead-shaped body to `CRM_INGEST_URL`.

### Payload (idempotent on Stripe session id)

The CRM body is the full order, not a lead. Key fields:

| Field | Use |
|--------|-----|
| `session_id` / `stripe_session_id` / `idempotency_key` | Stripe Checkout Session id — **idempotency key** |
| `payment_intent` | Stripe PaymentIntent id |
| `livemode` | `true` live / `false` test |
| `created` / `created_iso` | Stripe session timestamp |
| `amount_total` / `currency` / `amount_formatted` | Paid total |
| `customer_name` / `customer_email` / `customer_phone` | Buyer |
| `shipping` | Delivery address object |
| `line_items` | `{ name, quantity, amount }` |
| `box_count` / `total_packs` / `shipping_region` / `summary` | Boxes + short print line |
| `email_subject` / `email_body` | Same text as the owner email |

`GET /health` shows `crm_orders_ingest_configured` (URL resolvable + token set). The webhook JSON includes `notified.crm`.

---

## 4. Optional: Resend (direct email without Zapier)

If you prefer email from the worker as well:

```powershell
npx wrangler secret put RESEND_API_KEY
npx wrangler secret put OWNER_NOTIFY_EMAIL
# optional: RESEND_FROM_EMAIL  e.g. Rose Empire <orders@roseempire.co.uk>
```

---

## 5. Deploy after code changes

```powershell
cd "d:\rose empire main\cloudflare\checkout-worker"
npx wrangler deploy
```

Check: `https://rose-empire-checkout.adeelcolchester.workers.dev/health`  
Should show `webhook_secret_set` and `zapier_webhook_set` as `true` once secrets are set. After CRM secrets: `crm_orders_ingest_configured: true`.

---

## Quick test

1. Stripe Dashboard → Webhooks → your endpoint → **Send test webhook** (`checkout.session.completed`), **or**
2. Stripe CLI (forwards a signed event to the live or local worker):

```powershell
stripe listen --forward-to https://rose-empire-checkout.adeelcolchester.workers.dev/api/stripe/webhook
# other terminal:
stripe trigger checkout.session.completed
```

Use Test-mode CLI with `STRIPE_WEBHOOK_SECRET_TEST` (and optionally `STRIPE_SECRET_KEY_TEST`) so live/test dual secrets stay intact.

3. Place a small live/test order

You should get Zapier email + WhatsApp within seconds. Customer still gets the Stripe receipt email separately.

**CRM check:** the worker webhook JSON should include `notified.crm` (`ok: true` or `skipped` with a reason). Company HQ should create a **paid order** (session id, line items, shipping, totals) — not a lead. Re-sending the same `checkout.session.completed` must not duplicate the order (`session_id` is the idempotency key).
