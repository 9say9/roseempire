# Cloudflare cache headers (optional — add if roseempire.co.uk uses Cloudflare proxy)

If your domain uses **Cloudflare** in front of GitHub Pages, create a **Cache Rule**:

| Match | Cache TTL |
|-------|-----------|
| URI Path contains `/assets/` | 1 year |
| URI Path ends with `.css` or `.js` | 1 month |
| URI Path ends with `.webp` | 1 year |

This fixes PageSpeed **"Use efficient cache lifetimes"** (GitHub Pages alone sets ~10 min cache).

Without Cloudflare, scores above ~85 on mobile are still achievable; cache audit may stay orange.
