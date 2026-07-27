/**
 * Rose Empire — Stripe Checkout Cloudflare Worker
 * Secrets: STRIPE_SECRET_KEY
 * Optional env: SITE_URL
 *
 * Shipping: £10 per trade box (20 pieces). Delivery address required from the site
 * and also collected again on Stripe Checkout for confirmation.
 */

const PIECES_PER_BOX = 20;
const FEE_PER_BOX = 10;

const SHIPPING_REGIONS = {
  mainland: { id: "mainland", label: "UK Mainland" },
  highlands: { id: "highlands", label: "Scottish Highlands" },
  northern_ireland: { id: "northern_ireland", label: "Northern Ireland" },
};

const ALLOWED_ORIGINS = new Set([
  "https://www.roseempire.co.uk",
  "https://roseempire.co.uk",
  "http://127.0.0.1:5000",
  "http://localhost:5000",
  "http://127.0.0.1:5500",
  "http://localhost:5500",
]);

function corsHeaders(origin) {
  const headers = {
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
  if (origin && (ALLOWED_ORIGINS.has(origin) || origin.endsWith(".github.io"))) {
    headers["Access-Control-Allow-Origin"] = origin;
    headers["Vary"] = "Origin";
  }
  return headers;
}

function json(data, status, origin) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...corsHeaders(origin),
    },
  });
}

function discountPercent(totalPacks) {
  if (totalPacks >= 200) return 20;
  if (totalPacks >= 50) return 10;
  return 0;
}

function boxCountFromItems(items) {
  return items.reduce((n, item) => {
    const qty = Math.max(0, parseInt(item.quantity, 10) || 0);
    return n + (qty > 0 ? Math.ceil(qty / PIECES_PER_BOX) : 0);
  }, 0);
}

function logisticsCost(regionId, items) {
  const region = SHIPPING_REGIONS[regionId] || SHIPPING_REGIONS.mainland;
  const boxes = boxCountFromItems(items);
  if (boxes <= 0) return { cost: 0, label: region.label, boxes: 0 };
  return {
    cost: boxes * FEE_PER_BOX,
    label: region.label,
    boxes,
  };
}

function normalizeAddress(raw) {
  const src = raw && typeof raw === "object" ? raw : {};
  const clean = (v) => String(v || "").trim();
  return {
    name: clean(src.name),
    company: clean(src.company),
    phone: clean(src.phone),
    line1: clean(src.line1),
    line2: clean(src.line2),
    city: clean(src.city),
    postcode: clean(src.postcode).toUpperCase(),
  };
}

function validateAddress(addr) {
  if (!addr.name) return "Delivery contact name is required.";
  if (!addr.phone || addr.phone.length < 7) return "Delivery phone number is required.";
  if (!addr.line1) return "Delivery address line 1 is required.";
  if (!addr.city) return "Town / city is required.";
  if (!addr.postcode || addr.postcode.length < 5) return "A valid UK postcode is required.";
  return "";
}

function buildTotals(items, shippingRegion) {
  const cleaned = [];
  let totalPacks = 0;
  let gross = 0;
  for (const item of items || []) {
    const qty = Math.max(0, parseInt(item.quantity, 10) || 0);
    const unit = Number(item.unitPrice) || 0;
    if (qty < 1 || unit <= 0) continue;
    cleaned.push({
      title: String(item.title || "Rose Empire product").trim(),
      sizeName: String(item.sizeName || "Trade size").trim(),
      quantity: qty,
      unitPrice: unit,
      productId: String(item.productId || ""),
    });
    totalPacks += qty;
    gross += qty * unit;
  }
  if (!cleaned.length) throw new Error("No valid line items.");

  const discountPct = discountPercent(totalPacks);
  const discountAmount = gross * (discountPct / 100);
  const productNet = gross - discountAmount;
  const { cost: logistics, label: regionLabel, boxes } = logisticsCost(shippingRegion, cleaned);
  const netExVat = productNet + logistics;
  const vatAmount = netExVat * 0.2;
  const grandTotalIncVat = netExVat + vatAmount;

  return {
    items: cleaned,
    totalPacks,
    boxCount: boxes,
    discountPercent: discountPct,
    logisticsCost: logistics,
    regionLabel,
    vatAmount,
    grandTotalIncVat,
  };
}

function isPlaceholderKey(key) {
  return !key || !key.startsWith("sk_") || /your_|placeholder|example|xxx/i.test(key);
}

async function createStripeSession(env, body) {
  const secret = (env.STRIPE_SECRET_KEY || "").trim();
  if (isPlaceholderKey(secret)) {
    return {
      status: 503,
      data: {
        status: "error",
        message:
          "Stripe is not configured on the checkout worker. Set STRIPE_SECRET_KEY via wrangler secret.",
      },
    };
  }

  const items = body.items || [];
  if (!items.length) {
    return { status: 400, data: { status: "error", message: "Cart is empty." } };
  }

  const email = String(body.customerEmail || "").trim();
  if (!email || !email.includes("@")) {
    return {
      status: 400,
      data: {
        status: "error",
        message: "Enter a valid email before checkout.",
      },
    };
  }

  const shippingAddress = normalizeAddress(body.shippingAddress);
  const addressError = validateAddress(shippingAddress);
  if (addressError) {
    return { status: 400, data: { status: "error", message: addressError } };
  }

  const shippingRegion = String(body.shippingRegion || "mainland").trim();
  let totals;
  try {
    totals = buildTotals(items, shippingRegion);
  } catch (err) {
    return { status: 400, data: { status: "error", message: err.message } };
  }

  const domain = String(body.domain || env.SITE_URL || "https://www.roseempire.co.uk").replace(
    /\/$/,
    ""
  );
  const discountFactor = 1 - totals.discountPercent / 100;
  const addressBlock = [
    shippingAddress.name,
    shippingAddress.company,
    shippingAddress.line1,
    shippingAddress.line2,
    shippingAddress.city,
    shippingAddress.postcode,
    shippingAddress.phone ? `Tel: ${shippingAddress.phone}` : "",
  ]
    .filter(Boolean)
    .join(", ");

  const params = new URLSearchParams();
  params.set("mode", "payment");
  params.set("success_url", `${domain}/?checkout=success`);
  params.set("cancel_url", `${domain}/?checkout=cancel`);
  params.set("customer_email", email);
  params.set("allow_promotion_codes", "true");
  params.set("billing_address_collection", "required");
  params.set("shipping_address_collection[allowed_countries][0]", "GB");
  params.set("phone_number_collection[enabled]", "true");
  params.set("metadata[source]", "rose-empire-site");
  params.set("metadata[shipping_region]", shippingRegion);
  params.set("metadata[total_packs]", String(totals.totalPacks));
  params.set("metadata[box_count]", String(totals.boxCount));
  params.set("metadata[shipping_fee_per_box]", String(FEE_PER_BOX));
  params.set("metadata[grand_total_inc_vat]", totals.grandTotalIncVat.toFixed(2));
  params.set("metadata[ship_name]", shippingAddress.name.slice(0, 450));
  params.set("metadata[ship_company]", shippingAddress.company.slice(0, 450));
  params.set("metadata[ship_phone]", shippingAddress.phone.slice(0, 100));
  params.set("metadata[ship_line1]", shippingAddress.line1.slice(0, 450));
  params.set("metadata[ship_line2]", shippingAddress.line2.slice(0, 450));
  params.set("metadata[ship_city]", shippingAddress.city.slice(0, 200));
  params.set("metadata[ship_postcode]", shippingAddress.postcode.slice(0, 20));
  params.set("metadata[ship_address_full]", addressBlock.slice(0, 450));
  params.set(
    "payment_intent_data[metadata][ship_address_full]",
    addressBlock.slice(0, 450)
  );
  params.set("payment_intent_data[metadata][ship_postcode]", shippingAddress.postcode.slice(0, 20));
  params.set("payment_intent_data[metadata][ship_phone]", shippingAddress.phone.slice(0, 100));

  let idx = 0;
  for (const item of totals.items) {
    const unitAmount = Math.round(item.unitPrice * discountFactor * 100);
    if (unitAmount < 1) continue;
    params.set(`line_items[${idx}][price_data][currency]`, "gbp");
    params.set(
      `line_items[${idx}][price_data][product_data][name]`,
      `${item.title} (${item.sizeName})`
    );
    params.set(`line_items[${idx}][price_data][unit_amount]`, String(unitAmount));
    params.set(`line_items[${idx}][quantity]`, String(item.quantity));
    idx += 1;
  }

  const logisticsPence = Math.round(totals.logisticsCost * 100);
  if (logisticsPence > 0) {
    params.set(`line_items[${idx}][price_data][currency]`, "gbp");
    params.set(
      `line_items[${idx}][price_data][product_data][name]`,
      `UK shipping — ${totals.boxCount} box${totals.boxCount === 1 ? "" : "es"} × £${FEE_PER_BOX} (${totals.regionLabel})`
    );
    params.set(`line_items[${idx}][price_data][unit_amount]`, String(logisticsPence));
    params.set(`line_items[${idx}][quantity]`, "1");
    idx += 1;
  }

  const vatPence = Math.round(totals.vatAmount * 100);
  if (vatPence > 0) {
    params.set(`line_items[${idx}][price_data][currency]`, "gbp");
    params.set(`line_items[${idx}][price_data][product_data][name]`, "UK VAT (20%)");
    params.set(`line_items[${idx}][price_data][unit_amount]`, String(vatPence));
    params.set(`line_items[${idx}][quantity]`, "1");
  }

  const resp = await fetch("https://api.stripe.com/v1/checkout/sessions", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${secret}`,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: params.toString(),
  });
  const data = await resp.json();
  if (!resp.ok) {
    return {
      status: 500,
      data: {
        status: "error",
        message: (data.error && data.error.message) || "Stripe session failed.",
      },
    };
  }
  return { status: 200, data: { status: "success", url: data.url } };
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(origin) });
    }

    if (url.pathname === "/health" && request.method === "GET") {
      const configured = !isPlaceholderKey((env.STRIPE_SECRET_KEY || "").trim());
      return json({ status: "ok", stripe_configured: configured, shipping: "£10/box" }, 200, origin);
    }

    if (url.pathname === "/api/checkout/config" && request.method === "GET") {
      const configured = !isPlaceholderKey((env.STRIPE_SECRET_KEY || "").trim());
      return json(
        {
          status: "success",
          enabled: configured,
          currency: "GBP",
          shippingPerBox: FEE_PER_BOX,
          piecesPerBox: PIECES_PER_BOX,
          message: configured
            ? "Stripe ready. Shipping £10 per box (20 pieces)."
            : "Set STRIPE_SECRET_KEY on the checkout worker.",
        },
        200,
        origin
      );
    }

    if (url.pathname === "/api/checkout/create" && request.method === "POST") {
      let body = {};
      try {
        body = await request.json();
      } catch {
        return json({ status: "error", message: "Invalid JSON body." }, 400, origin);
      }
      const result = await createStripeSession(env, body);
      return json(result.data, result.status, origin);
    }

    return json({ status: "error", message: "Not found" }, 404, origin);
  },
};
