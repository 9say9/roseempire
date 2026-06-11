export function formatCatalogForBots(catalog) {
  const lines = [];
  if (!catalog) return "(Catalog unavailable — ask customer to check roseempire.co.uk or email info@roseempire.co.uk)";

  lines.push("WHOLESALE FACTS:");
  lines.push("- MOQ: " + catalog.wholesale.moqPerSize + " pieces per product size (" + catalog.wholesale.boxLabel + ").");
  for (const d of catalog.wholesale.volumeDiscounts || []) {
    lines.push("- Volume discount: " + d.label + ".");
  }
  lines.push("- " + catalog.wholesale.quoteNote);
  lines.push("- Contact: " + catalog.contact.email + ", " + catalog.contact.phoneDisplay);
  lines.push("- Catalog last updated: " + catalog.updatedAt);
  lines.push("");
  lines.push("LIVE PRODUCT CATALOG (website source of truth):");

  for (const p of catalog.products || []) {
    const sizes = (p.sizes || []).map((s) => s.name + ": GBP " + Number(s.price).toFixed(2) + "/pc").join("; ");
    lines.push("- " + p.title + " [" + p.category + ", stock: " + (p.stockStatus || "In stock") + "]");
    lines.push("  " + (p.desc || "").replace(/\n/g, " "));
    if (sizes) lines.push("  Sizes/prices: " + sizes + ". MOQ " + p.moq + " pieces.");
    if (p.highlights && p.highlights.length) lines.push("  Highlights: " + p.highlights.join(", ") + ".");
  }
  return lines.join("\n");
}

export function buildSystemPrompt(context, rules, catalog) {
  const base = rules[context] || rules.sarah;
  return base + "\n\n---\n" + formatCatalogForBots(catalog);
}
