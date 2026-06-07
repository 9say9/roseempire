# Rose Empire — What’s left (you + partner)

**Checked:** live status of website, domain, email, and LinkedIn assets.

---

## Status right now

| Item | Status | URL / note |
|------|--------|------------|
| Website on Netlify | **DONE** | https://say9.netlify.app |
| Custom domain | **LIVE (SSL may need refresh)** | https://www.roseempire.co.uk — DNS on Netlify |
| Ollama AI (local) | **DONE** | qwen2.5-coder:7b + 1.5b running; use `start_ollama.bat` |
| VS Code Continue config | **DONE** | `C:\Users\ADLSH\.continue\config.yaml` |
| Cloud API keys (Claude/Gemini/GPT) | **YOU** | Add in Continue → Settings → Secrets |
| Email info@roseempire.co.uk | **OK** | Microsoft 365 MX intact |
| LinkedIn profile photos/text | **YOU** | Manual upload (helper script below) |
| LinkedIn outreach leads | **READY** | 20 leads in CSV + draft scripts |

---

# PARTNER — Do today/tomorrow (GoDaddy)

**Time:** ~15 minutes  
**Guide:** `PARTNER_GODADDY_FIX.md`

### Checklist

- [ ] Log in: https://dcc.godaddy.com → **roseempire.co.uk** → **DNS**
- [ ] **Turn OFF** GoDaddy Website Builder / “Launching Soon” / domain forwarding
- [ ] **Add A record** `@` → **`75.2.60.5`** (currently MISSING — site returns 503)
- [ ] **Edit CNAME** `www` → **`say9.netlify.app`** (currently points to roseempire.co.uk — wrong)
- [ ] **Do NOT delete** MX: `roseempire-co-uk.mail.protection.outlook.com`
- [ ] **Do NOT delete** TXT records (email SPF / Microsoft)
- [ ] Wait 30–90 min → test https://www.roseempire.co.uk

### You (Netlify) — if not done yet

- [ ] https://app.netlify.com/projects/say9 → **Domain management**
- [ ] Add `roseempire.co.uk` + `www.roseempire.co.uk`
- [ ] Set **www.roseempire.co.uk** as primary when HTTPS is green

### After domain works

- [ ] Test quote PDF on live domain
- [ ] Update LinkedIn website field to `https://www.roseempire.co.uk`
- [ ] LinkedIn Post Inspector: https://www.linkedin.com/post-inspector/

---

# YOU — LinkedIn pictures & profile

**I cannot change LinkedIn for you** — LinkedIn blocks automated profile edits.  
**Python can only open the right pages** — you click Upload.

### Images on your PC

```
C:\Users\ADLSH\Documents\antigravity\linkedin-outreach\profile-assets\
```

| File | Use on LinkedIn |
|------|-----------------|
| `linkedin-banner-rose-empire.png` | Personal profile **background banner** |
| `linkedin-logo-rose-empire.png` | **Company page logo** + Featured thumbnail |
| **Your own headshot** | **Profile photo** (face — not the logo) |

### Easiest way — run helper

1. Double-click **`run_linkedin_profile_setup.bat`**
2. Log in if asked (or run `run_linkedin_login.bat` first)
3. Browser opens each edit page — upload images + paste text from **`LINKEDIN_PROFILE_EDIT_GUIDE.md`**

### LinkedIn checklist

- [ ] Profile photo (your headshot)
- [ ] Background banner (`linkedin-banner-rose-empire.png`)
- [ ] Headline + About (copy from guide)
- [ ] Contact: website `https://say9.netlify.app` → change to roseempire.co.uk when DNS fixed
- [ ] Featured link to catalog
- [ ] Company page: name, logo, banner, website
- [ ] Launch post from **`LINKEDIN_LAUNCH_POST.md`**

---

# Website — nothing broken; only domain left

The site itself is **ready**. No code changes required before go-live.

Optional later (not blocking):

- Compress large product PNGs for speed
- Swap say9.netlify.app → roseempire.co.uk in posts after DNS

---

# Sales — after profile + domain

- [ ] `run_draft_messages.bat` — draft connection messages
- [ ] Send **5–10** connection requests/day manually
- [ ] Follow **`SALES_OUTREACH_PLAYBOOK.md`**

---

## Quick reference

| Who | Task | File / link |
|-----|------|-------------|
| **Partner** | Fix GoDaddy DNS | `PARTNER_GODADDY_FIX.md` |
| **You** | LinkedIn photos + text | `run_linkedin_profile_setup.bat` + `LINKEDIN_PROFILE_EDIT_GUIDE.md` |
| **You** | Post launch | `LINKEDIN_LAUNCH_POST.md` |
| **Both** | Test live site | https://say9.netlify.app → then www.roseempire.co.uk |

---

## Why Python can’t auto-upload LinkedIn photos

- LinkedIn has no public API for changing profile pictures
- Automated login/upload breaks their terms and triggers security blocks
- Your existing scripts are for **lead scraping** and **opening edit pages** — not replacing manual upload

This is normal for every business — upload takes ~15 minutes once.
