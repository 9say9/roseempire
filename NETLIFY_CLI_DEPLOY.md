# Netlify CLI — one-command deploy (Rose Empire)

Connect this folder to **say9** on Netlify (custom domain **roseempire.co.uk**).

## Quick deploy (after HTML/CSS/JS changes)

From this folder in PowerShell or Cursor terminal:

```powershell
netlify deploy --prod --dir .
```

Or: **`deploy-live.bat`** (double-click) · **`npm run deploy`**

---

## Setup status (this machine)

| Step | Status |
|------|--------|
| Netlify CLI | Installed (`netlify-cli` global) |
| `netlify login` | Done (adeelcolchester@gmail.com) |
| `netlify link --name say9` | Done → https://roseempire.co.uk |

Run `netlify status` anytime to confirm.

## One-time setup (new machine only)

### 1. Install CLI

Global (recommended for Roo Code / terminal anywhere):

```powershell
npm install -g netlify-cli
```

Or install only in this project (used by `deploy-live.bat`):

```powershell
cd C:\Users\ADLSH\Documents\antigravity
npm install
```

### 2. Log in (browser — click **Authorize**)

In PowerShell or Cursor terminal, from this folder:

```powershell
netlify login
```

A browser tab opens. Sign in to Netlify, then click **Authorize** when prompted. Return to the terminal when it says you are logged in.

### 3. Link this folder to your live site

```powershell
netlify link --name say9
```

If asked, confirm site **say9** (preview: https://say9.netlify.app, domain: roseempire.co.uk).

Check link:

```powershell
netlify status
```

## Deploy after HTML/CSS/JS changes

**Production** (updates www.roseempire.co.uk):

```powershell
netlify deploy --prod --dir .
```

Or double-click **`deploy-live.bat`**, or:

```powershell
npm run deploy
```

**Draft preview** (safe test URL, not production):

```powershell
npm run deploy:preview
```

## Roo Code / Cursor instruction

When website files change (`index.html`, `styles.css`, `app.js`, `assets/`, quote scripts), run production deploy from `C:\Users\ADLSH\Documents\antigravity`:

```text
netlify deploy --prod --dir .
```

Do not upload zips manually unless CLI is unavailable.

## Files included in deploy

`.netlifyignore` excludes `linkedin-outreach/`, zip files, Python scripts, and docs. Site files match `create_deploy_zip.py` (HTML, CSS, JS, `assets/`, `robots.txt`, `sitemap.xml`).

## Troubleshooting

| Issue | Fix |
|--------|-----|
| `netlify` not recognized | `npm install -g netlify-cli` or `npm install` in this folder |
| Not logged in | `netlify login` |
| Not linked | `netlify link --name say9` |
| Wrong site | Delete `.netlify` folder, run `netlify link` again |

Netlify dashboard: https://app.netlify.com/projects/say9
