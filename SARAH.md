# Sarah AI (website chat)

Sarah is the **Rose Empire wholesale representative** on the site — black/gold circular orb (bottom-right) plus the **Ask Sarah** header button.

## How she works for customers

1. **Engage** — greets trade buyers and asks what they need  
2. **Answer** — products, MOQ (20/size), volume discounts, certs, UK delivery, from live `catalog-data.json`  
3. **Qualify** — collects facility type, email, volume, products, business name naturally  
4. **Close** — steers buyers to **Get A Quote** / checkout and logs emails via the Cloudflare lead API  

Widget file: `sarah-widget.js` (deployed with GitHub Pages).  
Lead / owner API: `https://rose-empire-sarah.adeelcolchester.workers.dev`

## Tiny yellow grammar dot (not Sarah)

A small solid yellow dot is usually **QuillBot**, not Rose Empire. Disable it for this site if it confuses you.
