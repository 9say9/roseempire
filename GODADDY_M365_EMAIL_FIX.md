# Fix Microsoft 365 email (GoDaddy)

SMTP is disabled and default Graph apps are blocked on your tenant.

## Option A — Enable SMTP (~5 min)

1. https://admin.microsoft.com → Users → info@roseempire.co.uk
2. Mail → Manage email apps → ON **Authenticated SMTP**
3. Test: py -3 manchester_sales_pipeline.py --limit 1 --send

## Option B — Register your own Graph app

1. https://portal.azure.com → App registrations → New
2. Redirect: http://localhost:8400 (public client)
3. Graph permissions: Mail.Send, User.Read → Admin consent
4. Add MS_GRAPH_CLIENT_ID to .env
5. Run: py -3 fix_ms365_graph_playwright.py
