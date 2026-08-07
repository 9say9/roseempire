/**
 * Rose Empire — Stripe Checkout Cloudflare Worker
 * Secrets:
 *   STRIPE_SECRET_KEY            (required — live sk_live_… for production)
 *   STRIPE_WEBHOOK_SECRET        (required — live whsec_… for production)
 *   ZAPIER_WEBHOOK_URL           (Catch Hook → Email + WhatsApp)
 * Optional:
 *   STRIPE_SECRET_KEY_TEST       (sk_test_… — expands test Checkout sessions)
 *   STRIPE_WEBHOOK_SECRET_TEST   (whsec_… from Stripe Test mode webhook)
 *   SITE_URL
 *   OWNER_NOTIFY_EMAIL           (default info@roseempire.co.uk)
 *   RESEND_API_KEY               (optional direct owner email)
 *   RESEND_FROM_EMAIL            (default Rose Empire <orders@roseempire.co.uk>)
 *
 * Shipping per trade box: Mainland £10 · Scotland & Northern Ireland £15.
 */

const PIECES_PER_BOX = 20;
const FEE_PER_BOX_DEFAULT = 10;
// Prefer personal Gmail — info@ is Cloudflare Email Routing (forward + Sarah).
const DEFAULT_OWNER_EMAIL = "adeelcolchester@gmail.com";

const SHIPPING_REGIONS = {
  mainland: { id: "mainland", label: "UK Mainland", feePerBox: 10 },
  highlands: { id: "highlands", label: "Scotland", feePerBox: 15 },
  northern_ireland: { id: "northern_ireland", label: "Northern Ireland", feePerBox: 15 },
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
    if (qty <= 0) return n;
    const perBox = Math.max(1, parseInt(item.piecesPerBox, 10) || 20);
    return n + Math.ceil(qty / perBox);
  }, 0);
}

function feePerBox(regionId) {
  const region = SHIPPING_REGIONS[regionId] || SHIPPING_REGIONS.mainland;
  return Number(region.feePerBox) || FEE_PER_BOX_DEFAULT;
}

function logisticsCost(regionId, items) {
  const region = SHIPPING_REGIONS[regionId] || SHIPPING_REGIONS.mainland;
  const boxes = boxCountFromItems(items);
  const fee = feePerBox(regionId);
  if (boxes <= 0) return { cost: 0, label: region.label, boxes: 0, feePerBox: fee };
  return {
    cost: boxes * fee,
    label: region.label,
    boxes,
    feePerBox: fee,
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
      piecesPerBox: Math.max(1, parseInt(item.piecesPerBox, 10) || 20),
    });
    totalPacks += qty;
    gross += qty * unit;
  }
  if (!cleaned.length) throw new Error("No valid line items.");

  const discountPct = discountPercent(totalPacks);
  const discountAmount = gross * (discountPct / 100);
  const productNet = gross - discountAmount;
  const { cost: logistics, label: regionLabel, boxes, feePerBox: shipFee } = logisticsCost(
    shippingRegion,
    cleaned
  );
  const netExVat = productNet + logistics;
  const vatAmount = netExVat * 0.2;
  const grandTotalIncVat = netExVat + vatAmount;

  return {
    items: cleaned,
    totalPacks,
    boxCount: boxes,
    feePerBox: shipFee,
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

/** Public-safe hint only — never returns the key itself. */
function secretKeyHint(key) {
  const k = String(key || "").trim();
  if (!k) return "empty";
  if (k.startsWith("sk_live_")) return "sk_live";
  if (k.startsWith("sk_test_")) return "sk_test";
  if (k.startsWith("rk_live_")) return "rk_live";
  if (k.startsWith("rk_test_")) return "rk_test";
  if (k.startsWith("pk_live_") || k.startsWith("pk_test_")) return "publishable_key_wrong_slot";
  if (k.startsWith("whsec_")) return "webhook_secret_wrong_slot";
  if (k.startsWith('"') || k.startsWith("'")) return "quoted_value_remove_quotes";
  return "unexpected_format";
}

function timingSafeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let out = 0;
  for (let i = 0; i < a.length; i += 1) out |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return out === 0;
}

function bytesToHex(buf) {
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function stripeKeyMode(key) {
  const k = String(key || "").trim();
  if (k.startsWith("sk_live_") || k.startsWith("rk_live_") || k.startsWith("pk_live_")) return "live";
  if (k.startsWith("sk_test_") || k.startsWith("rk_test_") || k.startsWith("pk_test_")) return "test";
  return "unknown";
}

function webhookSecrets(env) {
  const secrets = [];
  const primary = String(env.STRIPE_WEBHOOK_SECRET || "").trim();
  const test = String(env.STRIPE_WEBHOOK_SECRET_TEST || "").trim();
  if (primary.startsWith("whsec_")) secrets.push(primary);
  if (test.startsWith("whsec_") && test !== primary) secrets.push(test);
  return secrets;
}

function stripeSecretForEvent(env, livemode) {
  const live = String(env.STRIPE_SECRET_KEY || "").trim();
  const test = String(env.STRIPE_SECRET_KEY_TEST || "").trim();
  if (livemode === false) {
    if (test && !isPlaceholderKey(test)) return test;
    if (live && stripeKeyMode(live) === "test") return live;
    return test || live;
  }
  if (live && stripeKeyMode(live) === "live") return live;
  if (live && !isPlaceholderKey(live)) return live;
  return live || test;
}

async function verifyStripeSignature(rawBody, signatureHeader, webhookSecret) {
  if (!signatureHeader || !webhookSecret) return false;
  const parts = {};
  for (const piece of signatureHeader.split(",")) {
    const [k, ...rest] = piece.trim().split("=");
    if (!k || !rest.length) continue;
    const v = rest.join("=");
    if (!parts[k]) parts[k] = [];
    parts[k].push(v);
  }
  const timestamp = parts.t && parts.t[0];
  const candidates = parts.v1 || [];
  if (!timestamp || !candidates.length) return false;

  const age = Math.abs(Math.floor(Date.now() / 1000) - Number(timestamp));
  if (!Number.isFinite(age) || age > 300) return false;

  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(webhookSecret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const signed = await crypto.subtle.sign(
    "HMAC",
    key,
    encoder.encode(`${timestamp}.${rawBody}`)
  );
  const expected = bytesToHex(signed);
  return candidates.some((sig) => timingSafeEqual(sig, expected));
}

async function verifyStripeSignatureAny(rawBody, signatureHeader, secrets) {
  for (const secret of secrets) {
    if (await verifyStripeSignature(rawBody, signatureHeader, secret)) return true;
  }
  return false;
}

function moneyFromStripe(amount, currency) {
  const major = (Number(amount) || 0) / 100;
  const code = String(currency || "gbp").toUpperCase();
  if (code === "GBP") return `£${major.toFixed(2)}`;
  return `${major.toFixed(2)} ${code}`;
}

function buildOrderAlert(session) {
  const meta = session.metadata || {};
  const email = session.customer_details?.email || session.customer_email || "";
  const name =
    session.customer_details?.name ||
    meta.ship_name ||
    session.shipping_details?.name ||
    "";
  const phone =
    meta.ship_phone ||
    session.customer_details?.phone ||
    session.shipping_details?.phone ||
    "";
  const ship = {
    name: meta.ship_name || name,
    company: meta.ship_company || "",
    phone,
    line1: meta.ship_line1 || session.shipping_details?.address?.line1 || "",
    line2: meta.ship_line2 || session.shipping_details?.address?.line2 || "",
    city: meta.ship_city || session.shipping_details?.address?.city || "",
    postcode: meta.ship_postcode || session.shipping_details?.address?.postal_code || "",
    full: meta.ship_address_full || "",
  };
  const lineItems = (session.line_items?.data || []).map((li) => ({
    name: li.description || li.price?.product?.name || "Item",
    quantity: li.quantity || 0,
    amount: moneyFromStripe(li.amount_total, session.currency),
  }));
  const total = moneyFromStripe(session.amount_total, session.currency);
  const linesText = lineItems.length
    ? lineItems.map((li) => `• ${li.quantity}× ${li.name} — ${li.amount}`).join("\n")
    : "(See Stripe Dashboard for line items)";
  const addressText =
    ship.full ||
    [ship.name, ship.company, ship.line1, ship.line2, ship.city, ship.postcode, ship.phone]
      .filter(Boolean)
      .join(", ");

  const whatsapp_message = [
    "🛒 *Rose Empire — NEW ORDER*",
    `Total: ${total}`,
    `Email: ${email}`,
    `Name: ${name || ship.name || "—"}`,
    `Phone: ${phone || "—"}`,
    `Region: ${meta.shipping_region || "—"}`,
    `Boxes: ${meta.box_count || "—"} · Pieces: ${meta.total_packs || "—"}`,
    "",
    "Items:",
    linesText,
    "",
    `Deliver to: ${addressText || "—"}`,
    `Stripe: ${session.id}`,
  ].join("\n");

  const email_subject = `New Rose Empire order — ${total}`;
  const email_body = [
    "A wholesale order was paid on roseempire.co.uk.",
    "",
    `Total (inc VAT): ${total}`,
    `Customer email: ${email}`,
    `Customer name: ${name || ship.name || "—"}`,
    `Phone: ${phone || "—"}`,
    `Shipping region: ${meta.shipping_region || "—"}`,
    `Trade boxes: ${meta.box_count || "—"}`,
    `Pieces: ${meta.total_packs || "—"}`,
    "",
    "Items:",
    linesText,
    "",
    "Delivery address:",
    addressText || "—",
    "",
    `Checkout session: ${session.id}`,
    `Payment intent: ${session.payment_intent || "—"}`,
    "Open Stripe Dashboard → Payments for full details.",
  ].join("\n");

  return {
    event: "rose_empire.order_paid",
    source: "rose-empire-checkout-webhook",
    session_id: session.id,
    payment_intent: session.payment_intent || "",
    payment_status: session.payment_status || "",
    amount_total: (Number(session.amount_total) || 0) / 100,
    currency: session.currency || "gbp",
    amount_formatted: total,
    customer_email: email,
    customer_name: name || ship.name,
    shipping: ship,
    metadata: meta,
    line_items: lineItems,
    whatsapp_message,
    email_subject,
    email_body,
  };
}

async function expandCheckoutSession(secret, sessionId) {
  const url =
    `https://api.stripe.com/v1/checkout/sessions/${encodeURIComponent(sessionId)}` +
    "?expand[]=line_items";
  const resp = await fetch(url, {
    headers: { Authorization: `Bearer ${secret}` },
  });
  const data = await resp.json();
  if (!resp.ok) {
    throw new Error((data.error && data.error.message) || "Could not load Checkout Session");
  }
  return data;
}

async function notifyCrmIngest(env, payload) {
  const url = String(env.CRM_INGEST_URL || "").trim();
  const token = String(env.CRM_INGEST_TOKEN || "").trim();
  if (!url || !/^https?:\/\//i.test(url) || !token) {
    return { skipped: true, reason: "CRM_INGEST_URL / CRM_INGEST_TOKEN not set" };
  }
  try {
    const resp = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CRM-Token": token,
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        email: payload.customer_email || "",
        name: payload.customer_name || payload.company || "",
        phone: payload.phone || "",
        source: payload.lead_type === "quick_enquiry" ? "quick_enquiry" : "rfq",
        notes: payload.email_body || payload.whatsapp_message || "",
        website: payload.page_source || "https://www.roseempire.co.uk",
        address: payload.address || "",
      }),
    });
    const text = await resp.text();
    return { ok: resp.ok, status: resp.status, body: text.slice(0, 200) };
  } catch (err) {
    return { ok: false, error: String(err && err.message ? err.message : err) };
  }
}

async function notifyZapier(env, payload) {
  const hook = String(env.ZAPIER_WEBHOOK_URL || "").trim();
  if (!hook || !/^https:\/\//i.test(hook)) {
    return { skipped: true, reason: "ZAPIER_WEBHOOK_URL not set" };
  }
  const resp = await fetch(hook, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const text = await resp.text();
  if (!resp.ok) {
    return { ok: false, status: resp.status, body: text.slice(0, 300) };
  }
  return { ok: true, status: resp.status };
}

async function notifyOwnerEmail(env, payload) {
  const apiKey = String(env.RESEND_API_KEY || "").trim();
  if (!apiKey) {
    return { skipped: true, reason: "RESEND_API_KEY not set (Zapier email can cover this)" };
  }
  const to = String(env.OWNER_NOTIFY_EMAIL || DEFAULT_OWNER_EMAIL).trim();
  const from = String(env.RESEND_FROM_EMAIL || "Rose Empire <orders@roseempire.co.uk>").trim();
  const resp = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      from,
      to: [to],
      subject: payload.email_subject,
      text: payload.email_body,
    }),
  });
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    return { ok: false, status: resp.status, error: data };
  }
  return { ok: true, id: data.id };
}

function buildLeadAlert(body) {
  const clean = (v, max = 500) => String(v || "").trim().slice(0, max);
  const leadType = clean(body.leadType) === "quick_enquiry" ? "quick_enquiry" : "rfq";
  const name = clean(body.name, 120);
  const company = clean(body.company, 160);
  const email = clean(body.email, 160);
  const phone = clean(body.phone, 40);
  const address = clean(body.address, 600);
  const notes = clean(body.notes, 1500);
  const source = clean(body.source, 120) || "roseempire.co.uk";
  const regionLabel = clean(body.shippingLabel, 60);

  const items = Array.isArray(body.items) ? body.items.slice(0, 40) : [];
  const lineItems = items.map((i) => ({
    name: `${clean(i.title, 160)}${i.sizeName ? ` (${clean(i.sizeName, 60)})` : ""}`,
    quantity: Math.max(0, parseInt(i.quantity, 10) || 0),
    amount: `£${(Number(i.unitPrice) || 0).toFixed(2)}/pc`,
  }));
  const linesText = lineItems.length
    ? lineItems.map((li) => `• ${li.quantity}× ${li.name} — ${li.amount}`).join("\n")
    : "(No line items — general enquiry)";

  const totals = body.totals && typeof body.totals === "object" ? body.totals : {};
  const totalLine = totals.grandTotalIncVat
    ? `Est. total inc VAT: £${(Number(totals.grandTotalIncVat) || 0).toFixed(2)}`
    : "";

  const heading = leadType === "quick_enquiry" ? "QUICK ENQUIRY" : "QUOTE REQUEST (RFQ)";
  const email_subject = `Rose Empire ${leadType === "quick_enquiry" ? "enquiry" : "quote request"} — ${company || name || email}`;
  const email_body = [
    `New ${heading} from ${source}.`,
    "",
    `Name: ${name || "—"}`,
    `Company: ${company || "—"}`,
    `Email: ${email || "—"}`,
    `Phone: ${phone || "—"}`,
    `Delivery address: ${address || "To be confirmed"}`,
    regionLabel ? `Shipping region: ${regionLabel}` : "",
    "",
    "Items:",
    linesText,
    totalLine,
    "",
    `Notes: ${notes || "—"}`,
  ]
    .filter((l) => l !== "")
    .join("\n");

  const whatsapp_message = [
    `📩 *Rose Empire — ${heading}*`,
    `Name: ${name || "—"} (${company || "no company"})`,
    `Email: ${email || "—"} · Phone: ${phone || "—"}`,
    "",
    linesText,
    totalLine,
    notes ? `Notes: ${notes.slice(0, 300)}` : "",
  ]
    .filter(Boolean)
    .join("\n");

  return {
    event: leadType === "quick_enquiry" ? "rose_empire.quick_enquiry" : "rose_empire.rfq_submitted",
    source: "rose-empire-rfq-endpoint",
    lead_type: leadType,
    customer_email: email,
    customer_name: name,
    company,
    phone,
    address,
    notes,
    page_source: source,
    line_items: lineItems,
    totals,
    email_subject,
    email_body,
    whatsapp_message,
  };
}

/** Simple per-isolate rate limit for public lead endpoint (best-effort). */
const rfqHits = new Map();
function rfqRateLimited(ip) {
  const key = String(ip || "unknown").slice(0, 64);
  const now = Date.now();
  const windowMs = 60_000;
  const max = 8;
  let bucket = rfqHits.get(key);
  if (!bucket || now - bucket.start > windowMs) {
    bucket = { start: now, count: 0 };
    rfqHits.set(key, bucket);
  }
  bucket.count += 1;
  // Cap map growth
  if (rfqHits.size > 5000) {
    for (const [k, v] of rfqHits) {
      if (now - v.start > windowMs) rfqHits.delete(k);
    }
  }
  return bucket.count > max;
}

function originAllowed(origin) {
  if (!origin) return true; // same-origin navigations / some clients omit Origin
  return ALLOWED_ORIGINS.has(origin) || origin.endsWith(".github.io");
}

async function handleRfqLead(request, env, origin) {
  if (!originAllowed(origin)) {
    return json({ status: "error", message: "Origin not allowed." }, 403, origin);
  }

  const ip =
    request.headers.get("CF-Connecting-IP") ||
    request.headers.get("X-Forwarded-For") ||
    "unknown";
  if (rfqRateLimited(ip)) {
    return json({ status: "error", message: "Too many requests. Try again shortly." }, 429, origin);
  }

  const contentType = String(request.headers.get("Content-Type") || "");
  if (contentType && !contentType.toLowerCase().includes("application/json")) {
    return json({ status: "error", message: "Content-Type must be application/json." }, 415, origin);
  }

  const raw = await request.text();
  if (raw.length > 20_000) {
    return json({ status: "error", message: "Payload too large." }, 413, origin);
  }

  let body = {};
  try {
    body = JSON.parse(raw);
  } catch {
    return json({ status: "error", message: "Invalid JSON body." }, 400, origin);
  }
  if (!body || typeof body !== "object" || Array.isArray(body)) {
    return json({ status: "error", message: "Invalid JSON body." }, 400, origin);
  }

  const email = String(body.email || "").trim();
  const name = String(body.name || "").trim();
  if (!email || email.length > 200 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return json({ status: "error", message: "A valid email is required." }, 400, origin);
  }
  if (!name || name.length > 120) {
    return json({ status: "error", message: "Your name is required." }, 400, origin);
  }
  // Honeypot: bots fill every field.
  if (String(body.website || "").trim()) {
    return json({ status: "success", delivered: { spam: true } }, 200, origin);
  }

  const payload = buildLeadAlert(body);
  const [zapier, ownerEmail, crmIngest] = await Promise.all([
    notifyZapier(env, payload),
    notifyOwnerEmail(env, payload),
    notifyCrmIngest(env, payload),
  ]);

  console.log("rfq lead", {
    lead_type: payload.lead_type,
    email: payload.customer_email,
    zapier,
    ownerEmail,
    crmIngest,
  });

  const deliveredSomewhere =
    (zapier && zapier.ok) || (ownerEmail && ownerEmail.ok);
  if (!deliveredSomewhere) {
    return json(
      { status: "error", message: "Lead delivery is temporarily unavailable. Please email info@roseempire.co.uk." },
      502,
      origin
    );
  }
  return json({ status: "success", delivered: true }, 200, origin);
}

async function handleStripeWebhook(request, env) {
  const secrets = webhookSecrets(env);
  if (!secrets.length) {
    return json(
      {
        status: "error",
        message:
          "Set STRIPE_WEBHOOK_SECRET (live whsec_…) and optionally STRIPE_WEBHOOK_SECRET_TEST.",
      },
      503
    );
  }

  const rawBody = await request.text();
  const signature = request.headers.get("Stripe-Signature") || "";
  const valid = await verifyStripeSignatureAny(rawBody, signature, secrets);
  if (!valid) {
    console.error("stripe webhook signature failed", {
      secrets_configured: secrets.length,
      has_test_secret: Boolean(String(env.STRIPE_WEBHOOK_SECRET_TEST || "").trim()),
      stripe_key_mode: stripeKeyMode(env.STRIPE_SECRET_KEY),
    });
    return json(
      {
        status: "error",
        message:
          "Invalid Stripe signature. If this is Test mode, set STRIPE_WEBHOOK_SECRET_TEST to the Test endpoint signing secret (whsec_…).",
      },
      400
    );
  }

  let event;
  try {
    event = JSON.parse(rawBody);
  } catch {
    return json({ status: "error", message: "Invalid JSON." }, 400);
  }

  // Always acknowledge verified events so Stripe does not disable the endpoint.
  try {
    if (event.type !== "checkout.session.completed") {
      return json({ status: "ignored", type: event.type }, 200);
    }

    const sessionStub = event.data && event.data.object;
    if (!sessionStub || !sessionStub.id) {
      return json({ status: "ignored", reason: "missing_session" }, 200);
    }
    if (sessionStub.payment_status && sessionStub.payment_status !== "paid") {
      return json(
        {
          status: "ignored",
          reason: "payment_status not paid",
          payment_status: sessionStub.payment_status,
        },
        200
      );
    }

    const apiSecret = stripeSecretForEvent(env, event.livemode);
    if (isPlaceholderKey(apiSecret)) {
      console.error("stripe webhook: no API secret for mode", { livemode: event.livemode });
      return json(
        {
          status: "ok",
          notified: false,
          reason: "stripe_secret_missing_for_mode",
          livemode: event.livemode,
          session_id: sessionStub.id,
        },
        200
      );
    }

    let session = sessionStub;
    try {
      session = await expandCheckoutSession(apiSecret, sessionStub.id);
    } catch (err) {
      console.error("expand session failed", {
        livemode: event.livemode,
        key_mode: stripeKeyMode(apiSecret),
        err: String(err && err.message ? err.message : err),
      });
    }

    const payload = buildOrderAlert(session);
    const [zapier, email] = await Promise.all([
      notifyZapier(env, payload),
      notifyOwnerEmail(env, payload),
    ]);

    console.log("order alert", {
      session_id: payload.session_id,
      livemode: event.livemode,
      zapier,
      email,
    });

    return json(
      {
        status: "ok",
        livemode: event.livemode,
        notified: { zapier, email },
        session_id: payload.session_id,
      },
      200
    );
  } catch (err) {
    console.error("stripe webhook handler error", err);
    return json(
      {
        status: "ok",
        acknowledged: true,
        processing_error: true,
        type: event && event.type,
      },
      200
    );
  }
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

  const requestedDomain = String(body.domain || env.SITE_URL || "https://www.roseempire.co.uk").replace(
    /\/$/,
    ""
  );
  const allowedDomains = new Set([
    "https://www.roseempire.co.uk",
    "https://roseempire.co.uk",
    "http://127.0.0.1:5000",
    "http://localhost:5000",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
  ]);
  const domain = allowedDomains.has(requestedDomain)
    ? requestedDomain
    : "https://www.roseempire.co.uk";
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
  params.set("payment_intent_data[receipt_email]", email);
  params.set("allow_promotion_codes", "true");
  params.set("billing_address_collection", "required");
  params.set("shipping_address_collection[allowed_countries][0]", "GB");
  params.set("phone_number_collection[enabled]", "true");
  params.set("metadata[source]", "rose-empire-site");
  params.set("metadata[shipping_region]", shippingRegion);
  params.set("metadata[total_packs]", String(totals.totalPacks));
  params.set("metadata[box_count]", String(totals.boxCount));
  params.set("metadata[shipping_fee_per_box]", String(totals.feePerBox));
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
      `UK shipping — ${totals.boxCount} box${totals.boxCount === 1 ? "" : "es"} × £${totals.feePerBox} (${totals.regionLabel})`
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
      const zapier = Boolean(String(env.ZAPIER_WEBHOOK_URL || "").trim());
      const webhook = Boolean(String(env.STRIPE_WEBHOOK_SECRET || "").trim());
      const webhookTest = Boolean(String(env.STRIPE_WEBHOOK_SECRET_TEST || "").trim());
      const secretTest = Boolean(String(env.STRIPE_SECRET_KEY_TEST || "").trim());
      return json(
        {
          status: "ok",
          stripe_configured: configured,
          stripe_key_mode: stripeKeyMode(env.STRIPE_SECRET_KEY),
          stripe_secret_hint: secretKeyHint(env.STRIPE_SECRET_KEY),
          webhook_secret_set: webhook,
          webhook_test_secret_set: webhookTest,
          stripe_test_key_set: secretTest,
          zapier_webhook_set: zapier,
          shipping: "Mainland £10 / Scotland & NI £15 per box",
        },
        200,
        origin
      );
    }

    if (url.pathname === "/api/checkout/config" && request.method === "GET") {
      const configured = !isPlaceholderKey((env.STRIPE_SECRET_KEY || "").trim());
      return json(
        {
          status: "success",
          enabled: configured,
          currency: "GBP",
          shippingPerBoxMainland: 10,
          shippingPerBoxScotlandNi: 15,
          piecesPerBox: PIECES_PER_BOX,
          message: configured
            ? "Stripe ready. Shipping: Mainland £10 / Scotland & NI £15 per box."
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

    if (url.pathname === "/api/rfq" && request.method === "POST") {
      return handleRfqLead(request, env, origin);
    }

    if (url.pathname === "/api/stripe/webhook") {
      if (request.method === "GET" || request.method === "HEAD") {
        const webhookReady = Boolean(String(env.STRIPE_WEBHOOK_SECRET || "").trim());
        const webhookTestReady = Boolean(String(env.STRIPE_WEBHOOK_SECRET_TEST || "").trim());
        const keyMode = stripeKeyMode(env.STRIPE_SECRET_KEY);
        let setup;
        if (!webhookReady && !webhookTestReady) {
          setup =
            "Run: npx wrangler secret put STRIPE_WEBHOOK_SECRET (paste whsec_… from Stripe — match Live/Test to your API key).";
        } else if (keyMode === "test" && !webhookTestReady) {
          setup =
            "Worker is on Test API keys. Stripe Test webhook failures usually mean STRIPE_WEBHOOK_SECRET does not match the Test endpoint. Re-copy Signing secret from Stripe (Test mode) → Webhooks → this URL, then: npx wrangler secret put STRIPE_WEBHOOK_SECRET";
        } else if (keyMode === "live" && !webhookTestReady) {
          setup =
            "Live secret is set. For Stripe Test mode webhooks on the same URL, also run: npx wrangler secret put STRIPE_WEBHOOK_SECRET_TEST";
        } else {
          setup =
            "Signing secrets are set for the configured modes. Send a test event from Stripe Dashboard → Webhooks.";
        }
        return json(
          {
            status: "ok",
            message:
              "This URL is a Stripe webhook endpoint. Open it only from Stripe Dashboard → Webhooks (POST). Do not open it in a browser tab.",
            method_required: "POST",
            webhook_secret_set: webhookReady,
            webhook_test_secret_set: webhookTestReady,
            stripe_key_mode: keyMode,
            listen_for: ["checkout.session.completed"],
            setup,
          },
          200,
          origin
        );
      }
      if (request.method === "POST") {
        return handleStripeWebhook(request, env);
      }
      return json({ status: "error", message: "Use POST from Stripe." }, 405, origin);
    }

    return json({ status: "error", message: "Not found" }, 404, origin);
  },
};
