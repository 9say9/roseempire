# Fix HTTPS on roseempire.co.uk (Netlify)

**Diagnosis:** Your site IS live. HTTP works. HTTPS has a broken SSL certificate.

| URL | Status |
|-----|--------|
| http://roseempire.co.uk | OK (200) |
| http://www.roseempire.co.uk | Redirects to apex |
| https://roseempire.co.uk | SSL certificate error |
| https://www.roseempire.co.uk | SSL certificate error |
| https://say9.netlify.app | OK (backup URL) |

Browsers block HTTPS when the certificate is invalid — that is why it looks "not working".

---

## Fix in Netlify (5 minutes)

1. Open: https://app.netlify.com/projects/say9/domain-management

2. Under **Domain management**, confirm both domains are listed:
   - `roseempire.co.uk`
   - `www.roseempire.co.uk`

3. Click **Verify DNS configuration** on each (should show green check)

4. Scroll to **HTTPS** section:
   - Click **Verify DNS configuration** again if needed
   - Click **Provision certificate** or **Renew certificate**
   - Wait 5–15 minutes for Let's Encrypt to issue cert

5. When HTTPS shows **Netlify certificate** (green):
   - Enable **Force HTTPS**
   - Set **Primary domain** to `www.roseempire.co.uk`

6. Test in Incognito:
   - https://www.roseempire.co.uk
   - https://roseempire.co.uk (should redirect to www)

---

## If certificate keeps failing

- Ensure domain uses Netlify nameservers OR correct A/CNAME records
- Current DNS shows Netlify nameservers (nsone.net) — good
- Remove any duplicate domain entries in Netlify
- Contact Netlify support if stuck after 24h

---

## Temporary workaround (share with customers now)

Use **http://roseempire.co.uk** (works today) or **https://say9.netlify.app** (HTTPS works)

---

## Browser cache

After SSL is fixed, hard refresh: **Ctrl+Shift+R** to clear old GoDaddy "Launching Soon" page.
