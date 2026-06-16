"""Build Sarah/Adeel prompts from catalog-data.json + chat-rules (mirrors Cloudflare worker)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RULES_PATH = ROOT / "cloudflare" / "chat-worker" / "src" / "chat-rules.json"
CATALOG_PATH = ROOT / "catalog-data.json"


def load_rules() -> dict:
    return json.loads(RULES_PATH.read_text(encoding="utf-8"))


def load_catalog() -> dict | None:
    if not CATALOG_PATH.is_file():
        return None
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def format_catalog_for_bots(catalog: dict | None) -> str:
    if not catalog:
        return "(Catalog unavailable — ask customer to check roseempire.co.uk or email info@roseempire.co.uk)"

    lines = ["WHOLESALE FACTS:"]
    w = catalog.get("wholesale", {})
    lines.append(f"- MOQ: {w.get('moqPerSize', 20)} pieces per product size ({w.get('boxLabel', '1 trade box')}).")
    for d in w.get("volumeDiscounts", []):
        lines.append(f"- Volume discount: {d.get('label', '')}.")
    if w.get("quoteNote"):
        lines.append(f"- {w['quoteNote']}")
    c = catalog.get("contact", {})
    lines.append(f"- Contact: {c.get('email', '')}, {c.get('phoneDisplay', c.get('phone', ''))}")
    lines.append(f"- Catalog last updated: {catalog.get('updatedAt', 'unknown')}")
    lines.append("")
    lines.append("LIVE PRODUCT CATALOG (website source of truth):")

    for p in catalog.get("products", []):
        sizes = "; ".join(
            f"{s['name']}: GBP {float(s['price']):.2f}/pc" for s in p.get("sizes", [])
        )
        lines.append(f"- {p.get('title')} [{p.get('category')}, stock: {p.get('stockStatus', 'In stock')}]")
        lines.append(f"  {(p.get('desc') or '').replace(chr(10), ' ')}")
        if sizes:
            lines.append(f"  Sizes/prices: {sizes}. MOQ {p.get('moq', 20)} pieces.")
        highlights = p.get("highlights") or []
        if highlights:
            lines.append(f"  Highlights: {', '.join(highlights)}.")
    return "\n".join(lines)


def build_system_prompt(context: str, rules: dict | None = None, catalog: dict | None = None) -> str:
    rules = rules or load_rules()
    catalog = catalog if catalog is not None else load_catalog()
    base = rules.get(context) or rules.get("sarah", "")
    return f"{base}\n\n---\n{format_catalog_for_bots(catalog)}"

