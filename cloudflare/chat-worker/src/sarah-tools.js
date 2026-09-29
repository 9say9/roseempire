/** Sarah sales tools — run inside Cloudflare Worker (catalog-grounded, no hallucination). */

export const SARAH_TOOL_DECLARATIONS = [
  {
    name: "search_catalog",
    description: "Search Rose Empire wholesale products by keyword (protector, pillow, terry, wqmp, size).",
    parameters: {
      type: "object",
      properties: {
        query: { type: "string", description: "Search terms e.g. waterproof king terry pillow" },
      },
      required: ["query"],
    },
  },
  {
    name: "get_product",
    description: "Get full trade details for one product id (wqmp, qmp, terry, pillows).",
    parameters: {
      type: "object",
      properties: {
        product_id: { type: "string", description: "Product id from catalog" },
      },
      required: ["product_id"],
    },
  },
  {
    name: "moq_and_discounts",
    description: "Return MOQ, volume discount tiers, and trade box rules.",
    parameters: { type: "object", properties: {} },
  },
  {
    name: "shipping_info",
    description: "UK shipping rates per trade box and VAT note.",
    parameters: {
      type: "object",
      properties: {
        region: {
          type: "string",
          description: "mainland, scotland, northern_ireland, or uk",
        },
      },
    },
  },
  {
    name: "recommend_for_facility",
    description: "Suggest best product lines for a facility type (hotel, care home, student accommodation, guest house, retailer).",
    parameters: {
      type: "object",
      properties: {
        facility_type: { type: "string", description: "hotel, care home, student accommodation, guest house, retailer, distributor" },
      },
      required: ["facility_type"],
    },
  },
  {
    name: "qualify_lead_summary",
    description: "Summarise captured lead fields and next step (RFQ or WhatsApp).",
    parameters: {
      type: "object",
      properties: {
        business: { type: "string" },
        facility_type: { type: "string" },
        email: { type: "string" },
        volume: { type: "string" },
        products: { type: "string", description: "Comma-separated product interests" },
        region: { type: "string" },
      },
    },
  },
];

function norm(s) {
  return String(s || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function searchCatalog(catalog, query) {
  const q = norm(query);
  const products = catalog?.products || [];
  const hits = products.filter((p) => {
    const blob = norm([p.id, p.title, p.category, p.desc, ...(p.highlights || [])].join(" "));
    return q.split(/\s+/).every((w) => w.length < 2 || blob.includes(w));
  });
  return hits.slice(0, 5).map((p) => ({
    id: p.id,
    title: p.title,
    category: p.category,
    moq: p.moq,
    basePrice: p.basePrice,
    stockStatus: p.stockStatus,
    sizes: (p.sizes || []).slice(0, 6).map((s) => ({
      name: s.name,
      price: s.price,
    })),
  }));
}

function getProduct(catalog, productId) {
  const id = norm(productId).replace(/\s+/g, "");
  const p = (catalog?.products || []).find(
    (x) => norm(x.id) === id || norm(x.id).includes(id) || norm(x.title).includes(id)
  );
  if (!p) return { ok: false, error: "Product not found in catalog" };
  return {
    ok: true,
    product: {
      id: p.id,
      title: p.title,
      desc: p.desc,
      specs: p.specs,
      moq: p.moq,
      basePrice: p.basePrice,
      highlights: p.highlights,
      sizes: p.sizes,
      stockStatus: p.stockStatus,
    },
  };
}

const FACILITY_REC = {
  hotel: ["wqmp", "pillows"],
  "care home": ["terry", "wqmp"],
  "student accommodation": ["wqmp", "pillows"],
  "guest house": ["wqmp", "qmp"],
  retailer: ["wqmp", "terry", "pillows"],
  distributor: ["wqmp", "terry", "qmp", "pillows"],
};

export function executeSarahTool(name, args, catalog) {
  const n = String(name || "").trim();
  const a = args && typeof args === "object" ? args : {};

  if (n === "search_catalog") {
    const results = searchCatalog(catalog, a.query || "");
    return { ok: true, results, count: results.length };
  }

  if (n === "get_product") {
    return getProduct(catalog, a.product_id || "");
  }

  if (n === "moq_and_discounts") {
    const w = catalog?.wholesale || {};
    return {
      ok: true,
      moqPerSize: w.moqPerSize || 20,
      boxLabel: w.boxLabel || "1 trade box",
      volumeDiscounts: w.volumeDiscounts || [],
      quoteNote: w.quoteNote || "Formal quotes confirmed within 24 hours.",
    };
  }

  if (n === "shipping_info") {
    const w = catalog?.wholesale || {};
    const region = norm(a.region || "uk");
    const mainland = "£10 per trade box (England & Wales)";
    const remote = "£15 per trade box (Scotland & Northern Ireland)";
    let rate = `${mainland}; ${remote}`;
    if (/scotland|highland|ni|northern/.test(region)) rate = remote;
    else if (/mainland|england|wales/.test(region)) rate = mainland;
    return {
      ok: true,
      shippingNote: w.shippingNote || rate,
      vatNote: "VAT applies to products and shipping.",
      contact: catalog?.contact || {},
    };
  }

  if (n === "recommend_for_facility") {
    const ft = norm(a.facility_type);
    let key = "hotel";
    if (/student|pbsa|hall|university/.test(ft)) key = "student accommodation";
    else if (/care|nursing/.test(ft)) key = "care home";
    else if (/guest|bnb|airbnb|holiday/.test(ft)) key = "guest house";
    else if (/retail|shop/.test(ft)) key = "retailer";
    else if (/distrib/.test(ft)) key = "distributor";
    const ids = FACILITY_REC[key] || FACILITY_REC.hotel;
    const picks = ids.map((id) => getProduct(catalog, id)).filter((r) => r.ok).map((r) => r.product);
    return { ok: true, facility_type: key, recommendations: picks };
  }

  if (n === "qualify_lead_summary") {
    const fields = {
      business: a.business || "",
      facility_type: a.facility_type || "",
      email: a.email || "",
      volume: a.volume || "",
      products: a.products || "",
      region: a.region || "",
    };
    const missing = [];
    if (!fields.facility_type) missing.push("facility type");
    if (!fields.email) missing.push("business email");
    if (!fields.volume && !fields.products) missing.push("volume or products");
    return {
      ok: true,
      lead: fields,
      qualified: missing.length === 0,
      missing,
      next_step:
        missing.length === 0
          ? "Invite Request a quote on site or WhatsApp Adeel +44 7999 988450"
          : `Collect: ${missing.join(", ")}`,
    };
  }

  return { ok: false, error: `Unknown tool: ${n}` };
}
