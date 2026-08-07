# Sarah AI (website chat + inbound email)

Sarah is the **Rose Empire wholesale representative** on the site — black/gold circular orb (bottom-right) plus the **Ask Sarah** header button.

## How she works for customers

1. **Engage** — greets trade buyers and asks what they need  
2. **Answer** — products, MOQ (20/size), volume discounts, certs, UK delivery, from live `catalog-data.json`  
3. **Qualify** — collects facility type, email, volume, products, business name naturally  
4. **Close** — steers buyers to **Get A Quote** / checkout, or **WhatsApp handoff** to Adeel (`wa.me`) when asked / unsure / fully qualified  
5. **Hard questions** — falls back to Gemini via `rose-empire-chat` worker  
6. **CRM** — chat emails go to Cloudflare lead API; Company HQ pulls them into `crm.db` (`POST /api/crm/sync-website`)  

Widget file: `sarah-widget.js` (deployed with GitHub Pages).  
Lead / owner API: `https://rose-empire-sarah.adeelcolchester.workers.dev`  
Chat LLM: `https://rose-empire-chat.adeelcolchester.workers.dev/api/chat`  
Company HQ: `http://127.0.0.1:5050` — set `SARAH_ADMIN_TOKEN` in `D:\ai\antigravity\.env` to sync website leads.

## Email (free) — Cloudflare Email Routing

`info@roseempire.co.uk` is on **Cloudflare Email Routing** (not GoDaddy / Microsoft paid mail).

| Piece | Setup |
|--------|--------|
| Domain DNS | Cloudflare nameservers |
| Inbound | MX → `route*.mx.cloudflare.net` |
| Your inbox | Forward to `adeelcolchester@gmail.com` |
| Sarah auto-reply | Worker `rose-empire-sarah-inbox` (trade keywords) |
| Website chat Sarah | Unchanged — `sarah-widget.js` + `rose-empire-sarah` worker |

### Deploy / wire Sarah inbox worker

```powershell
cd "d:\rose empire main\cloudflare\sarah-inbox-worker"
.\deploy-and-wire.ps1
```

Or manually: `npx wrangler deploy`, then point the Email Routing rule for `info@` to worker `rose-empire-sarah-inbox`.

### Send mail *as* info@ from Gmail (outbound)

1. Gmail → Settings → Accounts → **Send mail as** → Add `info@roseempire.co.uk`  
2. Use Cloudflare / Gmail verification when prompted  
3. Set as default if you want replies from `info@`

### Old Microsoft Graph scripts (optional / legacy)

`d:\ai\antigravity\ms365_graph_auth.py` + `sarah_inbound_auto.py` need a live Microsoft mailbox. Prefer the Cloudflare worker above for free inbound Sarah.

## Tiny yellow grammar dot (not Sarah)

A small solid yellow dot is usually **QuillBot**, not Rose Empire. Disable it for this site if it confuses you.
