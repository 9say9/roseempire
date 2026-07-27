# Rose Empire — order alerts (email + WhatsApp)

When a customer pays on the website, Stripe hits our checkout worker webhook. The worker then:

1. Builds an order summary (items, total, delivery address, boxes)
2. POSTs it to your **Zapier Catch Hook** → Email + WhatsApp
3. Optionally emails you via **Resend** if `RESEND_API_KEY` is set

Webhook URL (already in the worker):

`https://rose-empire-checkout.adeelcolchester.workers.dev/api/stripe/webhook`

---

## 1. Stripe webhook (required)

1. Open [Stripe Webhooks](https://dashboard.stripe.com/webhooks) (live mode)
2. **Add endpoint** → paste the URL above
3. Listen to: **`checkout.session.completed`**
4. Copy **Signing secret** (`whsec_…`)
5. Save it on the worker:

```powershell
cd "d:\rose empire main\cloudflare\checkout-worker"
npx wrangler secret put STRIPE_WEBHOOK_SECRET
```

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

## 3. Optional: Resend (direct email without Zapier)

If you prefer email from the worker as well:

```powershell
npx wrangler secret put RESEND_API_KEY
npx wrangler secret put OWNER_NOTIFY_EMAIL
# optional: RESEND_FROM_EMAIL  e.g. Rose Empire <orders@roseempire.co.uk>
```

---

## 4. Deploy after code changes

```powershell
cd "d:\rose empire main\cloudflare\checkout-worker"
npx wrangler deploy
```

Check: `https://rose-empire-checkout.adeelcolchester.workers.dev/health`  
Should show `webhook_secret_set` and `zapier_webhook_set` as `true` once secrets are set.

---

## Quick test

1. Stripe Dashboard → Webhooks → your endpoint → **Send test webhook** (`checkout.session.completed`), **or**
2. Place a small live/test order

You should get Zapier email + WhatsApp within seconds. Customer still gets the Stripe receipt email separately.
