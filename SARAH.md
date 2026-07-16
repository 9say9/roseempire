# Sarah AI (website chat)

Sarah is loaded from the Cloudflare worker on every public page:

```
https://rose-empire-sarah.adeelcolchester.workers.dev
```

A local mirror of the widget script is kept as `sarah-widget.js` for reference. Production pages load the worker URL, not the local file.

## Owner mode

Owner/admin mode is unlocked with an admin token configured as a **Cloudflare Worker secret** (not in this repo).

- Do not commit admin tokens, `?sarah_admin=…` links, or deploy scripts that embed them.
- If a token was ever published (chat, docs, GitHub), rotate it in the Sarah worker immediately.

Worker source lives outside this repository (sarah-widget-agent). Deploy that project with Wrangler when updating Sarah’s backend.
