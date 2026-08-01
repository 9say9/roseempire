# Sarah AI (website chat + inbound email)

Sarah is the **Rose Empire wholesale representative** on the site — black/gold circular orb (bottom-right) plus the **Ask Sarah** header button.

## How she works for customers

1. **Engage** — greets trade buyers and asks what they need  
2. **Answer** — products, MOQ (20/size), volume discounts, certs, UK delivery, from live `catalog-data.json`  
3. **Qualify** — collects facility type, email, volume, products, business name naturally  
4. **Close** — steers buyers to **Get A Quote** / checkout and logs emails via the Cloudflare lead API  

Widget file: `sarah-widget.js` (deployed with GitHub Pages).  
Lead / owner API: `https://rose-empire-sarah.adeelcolchester.workers.dev`

## Inbound email auto-reply (trade enquiries)

When a buyer emails `info@roseempire.co.uk` asking for catalogue / price list / MOQ / lead times / freight / payment / private label, Sarah can **auto-reply** with a short branded answer + wholesale catalog PDF.

Code lives in the fleet folder (`d:\ai\antigravity`):

1. One-time login: `py -3 ms365_graph_auth.py` (as `info@roseempire.co.uk`)  
2. Test: `py -3 sarah_inbound_auto.py --dry-run`  
3. Live once: `py -3 sarah_inbound_auto.py`  
4. Schedule every 10 min: `setup_sarah_inbound_task.bat`

Only **trade-style** enquiries are answered (keyword match). Newsletters / Stripe / noreply are skipped. Each message is replied to once (logged in `crm.db`).

## Tiny yellow grammar dot (not Sarah)

A small solid yellow dot is usually **QuillBot**, not Rose Empire. Disable it for this site if it confuses you.
