#!/usr/bin/env node
/**
 * POST URLs to IndexNow (Bing/Yandex). Does not run automatically — operator runs after deploy.
 * Usage:
 *   node scripts/indexnow-ping.js
 *   node scripts/indexnow-ping.js https://www.roseempire.co.uk/student-accommodation.html
 */
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const HOST = "www.roseempire.co.uk";
const INDEXNOW_API = "https://api.indexnow.org/indexnow";

function findKeyFile() {
  const keys = fs.readdirSync(ROOT).filter((f) => /^[a-f0-9]{32}\.txt$/i.test(f));
  if (!keys.length) throw new Error("No IndexNow key file (<32-hex>.txt) in repo root.");
  const keyFile = keys[0];
  const key = fs.readFileSync(path.join(ROOT, keyFile), "utf8").trim();
  if (!key || key.length > 128) throw new Error("Invalid key in " + keyFile);
  return { key, keyFile };
}

function urlsFromSitemap() {
  const xml = fs.readFileSync(path.join(ROOT, "sitemap.xml"), "utf8");
  const locs = [];
  const re = /<loc>([^<]+)<\/loc>/g;
  let m;
  while ((m = re.exec(xml))) locs.push(m[1].trim());
  return locs;
}

async function main() {
  const { key, keyFile } = findKeyFile();
  const urlList = process.argv.slice(2).length ? process.argv.slice(2) : urlsFromSitemap();
  const body = {
    host: HOST,
    key,
    keyLocation: `https://${HOST}/${keyFile}`,
    urlList,
  };
  const res = await fetch(INDEXNOW_API, {
    method: "POST",
    headers: { "Content-Type": "application/json; charset=utf-8" },
    body: JSON.stringify(body),
  });
  const text = await res.text();
  console.log("IndexNow", res.status, text || "(empty body)");
  console.log("Submitted", urlList.length, "URL(s). Key file:", keyFile);
  if (!res.ok) process.exit(1);
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
