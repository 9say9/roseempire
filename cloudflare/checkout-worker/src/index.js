/**
 * Rose Empire — Stripe Checkout Cloudflare Worker
 * Secrets: STRIPE_SECRET_KEY
 * Optional env: SITE_URL
 */

const SHIPPING_REGIONS = {
  mainland: {
    id: "mainland",
    label: "UK Mainland (Standard Freight)",
    flatUpTo: 50,
    flatFee: 15,
    perPackOver: 0.5,
  },
  highlands: {
    id: "highlands",
    label: "Scottish Highlands (Extended Route)",
    flatUpTo: 50,
    flatFee: 28,
    perPackOver: 0.85,
  },
  northern_ireland: {
    id: "northern_ireland",
    label: "Northern Ireland (Sea Freight)",
    flatUpTo: 50,
    flatFee: 55,
    perPackOver: 1.2,
  },
};

const ALLOWED_ORIGINS = new Set([
  "https://www.roseempire.co.uk",
  "https://roseempire.co.uk",
  "http://127.0.0.1:5000",
  "http://localhost:5000",
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

function logisticsCost(regionId, totalPacks) {
  const region = SHIPPING_REGIONS[regionId] || SHIPPING_REGIONS.mainland;
  if (totalPacks <= 0) return { cost: 0, label: region.label };
  let cost = region.flatFee;
  if (totalPacks > region.flatUpTo) {
    cost += (totalPacks - region.flatUpTo) * region.perPackOver;
  }
  return { cost, label: region.label };
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
  const { cost: logistics, label: regionLabel } = logisticsCost(shippingRegion, totalPacks);
  const netExVat = productNet + logistics;
  const vatAmount = netExVat * 0.2;
  const grandTotalIncVat = netExVat + vatAmount;

  return {
    items: cleaned,
    totalPacks,
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
        message: "Enter a valid email in the quote form before checkout.",
      },
    };
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
  const params = new URLSearchParams();
  params.set("mode", "payment");
  params.set("success_url", `${domain}/?checkout=success`);
  params.set("cancel_url", `${domain}/?checkout=cancel`);
  params.set("customer_email", email);
  params.set("allow_promotion_codes", "true");
  params.set("metadata[source]", "rose-empire-site");
  params.set("metadata[shipping_region]", shippingRegion);
  params.set("metadata[total_packs]", String(totals.totalPacks));
  params.set("metadata[grand_total_inc_vat]", totals.grandTotalIncVat.toFixed(2));

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
      `UK logistics — ${totals.regionLabel}`
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
      return json({ status: "ok", stripe_configured: configured }, 200, origin);
    }

    if (url.pathname === "/api/checkout/config" && request.method === "GET") {
      const configured = !isPlaceholderKey((env.STRIPE_SECRET_KEY || "").trim());
      return json(
        {
          status: "success",
          enabled: configured,
          currency: "GBP",
          message: configured
            ? "Stripe ready."
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
