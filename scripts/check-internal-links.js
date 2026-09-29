#!/usr/bin/env node
/**
 * Crawl local HTML files and verify internal href/src paths exist on disk.
 * Usage: node scripts/check-internal-links.js
 */
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const HTML_GLOB_DIRS = [ROOT];
const SKIP_HREF = /^(https?:|mailto:|tel:|javascript:|#|data:|blob:)/i;

function listHtmlFiles(dir) {
  const out = [];
  for (const name of fs.readdirSync(dir)) {
    const full = path.join(dir, name);
    const stat = fs.statSync(full);
    if (stat.isDirectory()) {
      if (name === "node_modules" || name === "company-hq" || name === "site" || name === ".git" || name === "assets") continue;
      out.push(...listHtmlFiles(full));
    } else if (name.endsWith(".html") && !full.includes("company-hq")) {
      out.push(full);
    }
  }
  return out;
}

function extractUrls(html) {
  const urls = [];
  const re = /\b(?:href|src)\s*=\s*["']([^"']+)["']/gi;
  let m;
  while ((m = re.exec(html))) urls.push(m[1]);
  return urls;
}

function resolveLocal(file, url) {
  const clean = url.split("?")[0].split("#")[0];
  if (!clean || SKIP_HREF.test(clean)) return null;
  if (clean.startsWith("//")) return null;
  let target;
  if (clean.startsWith("/")) {
    target = path.join(ROOT, clean.replace(/^\//, ""));
  } else {
    target = path.join(path.dirname(file), clean);
  }
  return path.normalize(target);
}

const files = listHtmlFiles(ROOT);
const missing = [];

for (const file of files) {
  const html = fs.readFileSync(file, "utf8");
  for (const url of extractUrls(html)) {
    const local = resolveLocal(file, url);
    if (!local) continue;
    if (!fs.existsSync(local)) {
      missing.push({ file: path.relative(ROOT, file), url, expected: path.relative(ROOT, local) });
    }
  }
}

if (missing.length) {
  console.error("Missing internal links/assets:\n");
  for (const m of missing) {
    console.error(`  ${m.file}: ${m.url} → ${m.expected}`);
  }
  process.exit(1);
}
console.log(`OK — ${files.length} HTML files, no missing local href/src targets.`);
