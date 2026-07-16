"""Rose Empire — local static site server + Stripe Checkout API."""
from __future__ import annotations

import os
import re
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parent

SHIPPING_REGIONS = {
    "mainland": {
        "id": "mainland",
        "label": "UK Mainland (Standard Freight)",
        "flat_up_to": 50,
        "flat_fee": 15.0,
        "per_pack_over": 0.5,
    },
    "highlands": {
        "id": "highlands",
        "label": "Scottish Highlands (Extended Route)",
        "flat_up_to": 50,
        "flat_fee": 28.0,
        "per_pack_over": 0.85,
    },
    "northern_ireland": {
        "id": "northern_ireland",
        "label": "Northern Ireland (Sea Freight)",
        "flat_up_to": 50,
        "flat_fee": 55.0,
        "per_pack_over": 1.2,
    },
}

ALLOWED_ORIGINS = {
    "http://127.0.0.1:5000",
    "http://localhost:5000",
    "https://www.roseempire.co.uk",
    "https://roseempire.co.uk",
}

PLACEHOLDER_KEY = re.compile(
    r"your_|placeholder|example|xxx|change.?me",
    re.I,
)


def _load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return
    for raw in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


_load_dotenv()

PORT = int(os.environ.get("CHAT_PORT") or os.environ.get("PORT") or "5000")
HOST = os.environ.get("CHAT_HOST", "127.0.0.1")

app = Flask(__name__, static_folder=None)


def _origin_allowed(origin: str) -> bool:
    if not origin:
        return True
    if origin in ALLOWED_ORIGINS:
        return True
    if origin.endswith(".github.io") and origin.startswith("https://"):
        return True
    return False


@app.after_request
def _cors(response):
    origin = request.headers.get("Origin", "")
    if _origin_allowed(origin):
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


def _stripe_secret() -> str:
    key = (os.environ.get("STRIPE_SECRET_KEY") or "").strip()
    if not key or PLACEHOLDER_KEY.search(key) or not key.startswith("sk_"):
        return ""
    return key


def _discount_percent(total_packs: int) -> int:
    if total_packs >= 200:
        return 20
    if total_packs >= 50:
        return 10
    return 0


def _logistics_cost(region_id: str, total_packs: int) -> tuple[float, str]:
    region = SHIPPING_REGIONS.get(region_id) or SHIPPING_REGIONS["mainland"]
    if total_packs <= 0:
        return 0.0, region["label"]
    cost = float(region["flat_fee"])
    if total_packs > region["flat_up_to"]:
        extra = total_packs - region["flat_up_to"]
        cost += extra * float(region["per_pack_over"])
    return cost, region["label"]


def _build_totals(items: list, shipping_region: str) -> dict:
    cleaned = []
    total_packs = 0
    gross = 0.0
    for item in items:
        qty = max(0, int(item.get("quantity") or 0))
        unit = float(item.get("unitPrice") or 0)
        if qty < 1 or unit <= 0:
            continue
        title = str(item.get("title") or "Rose Empire product").strip()
        size = str(item.get("sizeName") or "Trade size").strip()
        cleaned.append(
            {
                "title": title,
                "sizeName": size,
                "quantity": qty,
                "unitPrice": unit,
                "productId": str(item.get("productId") or ""),
            }
        )
        total_packs += qty
        gross += qty * unit

    if not cleaned:
        raise ValueError("No valid line items.")

    discount_percent = _discount_percent(total_packs)
    discount_amount = gross * (discount_percent / 100.0)
    product_net = gross - discount_amount
    logistics, region_label = _logistics_cost(shipping_region, total_packs)
    net_ex_vat = product_net + logistics
    vat_amount = net_ex_vat * 0.2
    grand_total = net_ex_vat + vat_amount

    return {
        "items": cleaned,
        "totalPacks": total_packs,
        "grossSubtotal": gross,
        "discountPercent": discount_percent,
        "discountAmount": discount_amount,
        "productNet": product_net,
        "logisticsCost": logistics,
        "regionLabel": region_label,
        "netExVat": net_ex_vat,
        "vatAmount": vat_amount,
        "grandTotalIncVat": grand_total,
    }


@app.route("/api/checkout/config", methods=["GET", "OPTIONS"])
def api_checkout_config():
    if request.method == "OPTIONS":
        return "", 204
    publishable = (os.environ.get("STRIPE_PUBLISHABLE_KEY") or "").strip()
    enabled = bool(_stripe_secret()) and bool(publishable) and publishable.startswith("pk_")
    mode = "unset"
    if publishable.startswith("pk_test_"):
        mode = "test"
    elif publishable.startswith("pk_live_"):
        mode = "live"
    return jsonify(
        {
            "status": "success",
            "enabled": enabled,
            "currency": "GBP",
            "mode": mode,
            "message": (
                "Stripe ready."
                if enabled
                else "Set real STRIPE_SECRET_KEY and STRIPE_PUBLISHABLE_KEY in .env."
            ),
        }
    )


@app.route("/api/checkout/create", methods=["POST", "OPTIONS"])
def api_checkout_create():
    if request.method == "OPTIONS":
        return "", 204

    secret = _stripe_secret()
    if not secret:
        return jsonify(
            {
                "status": "error",
                "message": (
                    "Stripe is not configured. Add real STRIPE_SECRET_KEY and "
                    "STRIPE_PUBLISHABLE_KEY to .env (not placeholders), then restart."
                ),
            }
        ), 503

    data = request.get_json(silent=True) or {}
    items = data.get("items") or []
    if not items:
        return jsonify({"status": "error", "message": "Cart is empty."}), 400

    email = (data.get("customerEmail") or "").strip()
    if not email or "@" not in email:
        return jsonify(
            {"status": "error", "message": "Enter a valid email in the quote form before checkout."}
        ), 400

    shipping_region = (data.get("shippingRegion") or "mainland").strip()
    try:
        totals = _build_totals(items, shipping_region)
    except ValueError as exc:
        return jsonify({"status": "error", "message": str(exc)}), 400

    try:
        import stripe
    except Exception as exc:
        return jsonify({"status": "error", "message": f"Stripe SDK missing: {exc}"}), 500

    stripe.api_key = secret
    domain = (data.get("domain") or os.environ.get("SITE_URL") or request.host_url).rstrip("/")

    discount_factor = 1.0 - (totals["discountPercent"] / 100.0)
    line_items = []
    for item in totals["items"]:
        unit_amount = int(round(item["unitPrice"] * discount_factor * 100))
        if unit_amount < 1:
            continue
        line_items.append(
            {
                "price_data": {
                    "currency": "gbp",
                    "product_data": {
                        "name": f"{item['title']} ({item['sizeName']})",
                        "metadata": {
                            "product_id": item["productId"],
                            "size": item["sizeName"],
                        },
                    },
                    "unit_amount": unit_amount,
                },
                "quantity": item["quantity"],
            }
        )

    logistics_pence = int(round(totals["logisticsCost"] * 100))
    if logistics_pence > 0:
        line_items.append(
            {
                "price_data": {
                    "currency": "gbp",
                    "product_data": {
                        "name": f"UK logistics — {totals['regionLabel']}",
                    },
                    "unit_amount": logistics_pence,
                },
                "quantity": 1,
            }
        )

    vat_pence = int(round(totals["vatAmount"] * 100))
    if vat_pence > 0:
        line_items.append(
            {
                "price_data": {
                    "currency": "gbp",
                    "product_data": {"name": "UK VAT (20%)"},
                    "unit_amount": vat_pence,
                },
                "quantity": 1,
            }
        )

    if not line_items:
        return jsonify({"status": "error", "message": "No valid line items."}), 400

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,
            success_url=f"{domain}/?checkout=success",
            cancel_url=f"{domain}/?checkout=cancel",
            customer_email=email,
            metadata={
                "source": "rose-empire-site",
                "shipping_region": shipping_region,
                "total_packs": str(totals["totalPacks"]),
                "grand_total_inc_vat": f"{totals['grandTotalIncVat']:.2f}",
            },
            allow_promotion_codes=True,
        )
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500

    return jsonify({"status": "success", "url": session.url})


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "port": PORT,
            "stripe_configured": bool(_stripe_secret()),
        }
    )


@app.route("/")
def index():
    return send_from_directory(ROOT, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    if filename.startswith("api/"):
        return jsonify({"error": "Not found"}), 404
    target = ROOT / filename
    if target.is_file():
        return send_from_directory(ROOT, filename)
    return send_from_directory(ROOT, "404.html"), 404


if __name__ == "__main__":
    url = f"http://{HOST}:{PORT}"
    print("\n" + "=" * 52)
    print(f"  Rose Empire local server -> {url}")
    print(f"  Stripe: {'configured' if _stripe_secret() else 'not configured (add keys to .env)'}")
    print("=" * 52 + "\n")
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False, threaded=True)
