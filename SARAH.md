# Sarah AI (website chat)

Sarah is loaded from the Cloudflare worker on public pages:

```
https://rose-empire-sarah.adeelcolchester.workers.dev
```

## Floating orb

The yellow floating launcher orb is **hidden on purpose** — it was covering the quote cart and blocking Stripe/email clicks.

Customers open Sarah with the **Ask Sarah** button in the site header (homepage). That triggers the normal Sarah chat panel.

## Owner mode

Owner/admin mode uses an admin token stored only as a Cloudflare Worker secret — never commit tokens to git.
