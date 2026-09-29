const SITE_PAGES = `
SITE (https://www.roseempire.co.uk):
- Home catalog + quote cart + Secure Stripe checkout (same flow on all sector pages).
- Wholesale mattress protectors: /wholesale-mattress-protectors.html
- Wholesale pillows: /wholesale-pillows.html
- Sectors: /hotels.html, /care-homes.html, /holiday-lets.html, /student-accommodation.html
- Shipping & returns: /shipping-and-returns.html — UK mainland £10/box, Scotland & NI £15/box; VAT on products and shipping.
- Sample pack: request via quote form — credited on first wholesale box order (no fake retail pricing).
- Contact: info@roseempire.co.uk, +44 7999 988450, WhatsApp wa.me/447999988450. Warehouse: 5 Sagar Street, Manchester M8 8EU. Do not quote opening/closing hours — offer phone, WhatsApp, or email and say the team responds as soon as possible.
`.trim();

export function formatCatalogForBots(catalog) {
  const lines = [];
  if (!catalog) {
    return "(Catalog unavailable — ask customer to check roseempire.co.uk or email info@roseempire.co.uk)";
  }

  const w = catalog.wholesale || {};
  lines.push("WHOLESALE FACTS (from live catalog-data.json):");
  lines.push("- MOQ: " + (w.moqPerSize || 20) + " pieces per product size (" + (w.boxLabel || "full trade boxes only") + ").");
  lines.push("- Pillows: 5 pieces per box. Value line (microfibre shell): vacuum packed, GBP 7.00/pc duck or goose. Premium line (cotton shell): Rose Empire branded zip bag, GBP 8.00/pc duck or goose. Pillow-cover protector boxes: 40 pieces.");
  if (w.volumeDiscounts && w.volumeDiscounts.length) {
    for (const d of w.volumeDiscounts) lines.push("- Volume discount: " + d.label + ".");
  }
  if (w.tradeNote) lines.push("- " + w.tradeNote);
  if (w.quoteNote) lines.push("- " + w.quoteNote);
  if (w.shippingNote) lines.push("- Shipping: " + w.shippingNote);
  const c = catalog.contact || {};
  lines.push("- Contact: " + (c.email || "info@roseempire.co.uk") + ", " + (c.phoneDisplay || "+44 7999 988450"));
  lines.push("- Catalog last updated: " + (catalog.updatedAt || "unknown"));
  lines.push("");
  lines.push("LIVE PRODUCT CATALOG (prices GBP per piece at trade MOQ — never invent other prices):");

  for (const p of catalog.products || []) {
    const sizes = (p.sizes || [])
      .map((s) => s.name + ": GBP " + Number(s.price).toFixed(2) + "/pc (MOQ " + (s.moq || p.moq) + ")")
      .join("; ");
    lines.push("- " + p.title + " [id: " + p.id + ", " + p.category + "]");
    lines.push("  " + (p.desc || "").replace(/\n/g, " "));
    if (sizes) lines.push("  Sizes/prices: " + sizes);
    if (p.highlights && p.highlights.length) lines.push("  Highlights: " + p.highlights.join(", ") + ".");
    lines.push("  Order: add sizes on https://www.roseempire.co.uk/ then Stripe checkout or RFQ quote PDF.");
  }
  return lines.join("\n");
}

export function buildSystemPrompt(context, rules, catalog) {
  const base = rules[context] || rules.sarah;
  return [base, "", "---", SITE_PAGES, "", formatCatalogForBots(catalog)].join("\n");
}
