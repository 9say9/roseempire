# FIX NOW — GoDaddy DNS for roseempire.co.uk (GitHub Pages)

**Website host:** GitHub Pages (free) — not Netlify  
**Preview (live now):** https://9say9.github.io/roseempire/  
**Target domain:** https://www.roseempire.co.uk  

Give this sheet to your partner (GoDaddy login required).  
**~10 minutes. Email will keep working if they follow exactly.**

See also: **`GODADDY_LIVE_NOW.html`** (same steps in browser).

---

## DNS values — copy exactly

| Type | Name | Value |
|------|------|--------|
| **A** | @ | `185.199.108.153` |
| **A** | @ | `185.199.109.153` |
| **A** | @ | `185.199.110.153` |
| **A** | @ | `185.199.111.153` |
| **CNAME** | www | `9say9.github.io` |

**Remove old Netlify records:** A `75.2.60.5`, CNAME `say9.netlify.app`

### Do NOT delete (email — Microsoft 365)

| Type | Name | Value |
|------|------|--------|
| **MX** | @ | `roseempire-co-uk.mail.protection.outlook.com` |
| **TXT** | @ | SPF / Microsoft rows — leave unchanged |

---

## Partner steps (GoDaddy)

1. https://dcc.godaddy.com → **roseempire.co.uk** → **DNS**
2. Turn off **Website Builder** / **Forwarding** / “Launching Soon” if still on
3. Update **A** on `@` to GitHub IPs above (delete Netlify `75.2.60.5`)
4. Update **www** CNAME to `9say9.github.io` (delete `say9.netlify.app`)
5. Wait 30–90 min → test https://www.roseempire.co.uk

---

## GitHub (already configured)

- Repo: https://github.com/9say9/roseempire  
- Pages: branch **main**, custom domain **www.roseempire.co.uk**  
- Settings: https://github.com/9say9/roseempire/settings/pages  

---

## After domain works

- [ ] Remove `roseempire.co.uk` from Netlify site **say9** (optional)
- [ ] Deploy chat worker: `deploy_chat_worker.bat` (replaces Netlify function)
- [ ] Test quote PDF on live domain

Full guide: **`GITHUB_PAGES.md`**
