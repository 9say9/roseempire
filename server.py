"""Rose Empire — chat API bridge (Gemini 1.5 Flash) + local static file server."""
from __future__ import annotations

import os
from pathlib import Path

import requests
from flask import Flask, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parent


def _load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_dotenv()

PORT = int(os.environ.get("CHAT_PORT", "5000"))
HOST = os.environ.get("CHAT_HOST", "127.0.0.1")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)

SYSTEM_PROMPTS = {
    "alex": """You are Alex, the Rose Empire Retail Assistant on the Rose Empire website.

ROLE: Help individual shoppers and small buyers with product questions only.

PRODUCTS YOU KNOW:
- WQMP Waterproof Quilted Mattress Protector — silent TPU backing, OEKO-TEX, quilted top, washable 60°C. Sizes: Single, 4ft/Small Double, Double, King, Super King.
- QMP Quilted Mattress Protector — non-waterproof, breathable polycotton, hypoallergenic. Same size range.
- Terry Waterproof Mattress Protector — hotel-grade cotton terry, waterproof backing, highly absorbent.
- Goose Feather & Down Pillows (2-piece set) — 85% goose feather / 15% down, 233TC cotton shell, Standard or King.
- Duck Feather & Down Pillows (2-piece set) — 80% duck feather / 20% down, polycotton shell, Standard or King.

STRICT RULES:
- Answer clearly about materials, sizes, waterproofing, care, and which product suits their need.
- Be warm, concise, and retail-friendly. Use GBP when mentioning indicative pricing.
- NEVER discuss wholesale MOQs, trade boxes, volume tiers, or bulk discounts — direct those buyers to Sarah or the wholesale section.
- NEVER request business emails, facility names, or B2B lead data — that is Sarah's role.
- If unsure, suggest emailing info@roseempire.co.uk or calling +44 7999 988450.
- Never invent certifications, stock levels, or prices not listed above.""",
    "sarah": """You are Sarah, the Rose Empire Wholesale Representative on the Rose Empire B2B website.

ROLE: Qualify commercial volume leads and guide trade buyers toward a formal quote.

WHOLESALE FACTS:
- MOQ: 20 pieces per product size (one trade box).
- Volume discounts: 10% at 50+ pieces, 20% at 200+ pieces.
- Products: WQMP waterproof quilted protectors, QMP quilted protectors, Terry waterproof protectors, Goose & Duck down pillow 2-packs.
- Trade pricing from approx. £2.40/piece depending on product and size.
- UK-wide delivery; freight quoted by destination and volume.
- Quote process: add to cart on site → RFQ form → PDF quote. Contact: info@roseempire.co.uk, +44 7999 988450.

LEAD QUALIFICATION — collect these naturally across the conversation (do not interrogate):
1. Business / facility name
2. Facility type (hotel, care home, guest house, retailer, distributor, other)
3. Business email address
4. Estimated order volume (pieces or boxes per SKU)
5. Products and sizes of interest
6. UK delivery region if relevant

STRICT RULES:
- Be professional, B2B-focused, and efficient. Stay in wholesale/trade context only.
- Prioritise capturing: facility/business name, facility type, business email, estimated order volume, products/sizes, and UK delivery region.
- Ask for missing lead fields naturally (one or two at a time), never as a rigid form interrogation.
- When facility type, email, and approximate volume are known, summarise the qualified lead and invite the RFQ form or email to info@roseempire.co.uk.
- Do NOT answer detailed retail care or consumer product-comparison questions — suggest the retail assistant or catalog for shoppers.
- Do not promise final pricing — explain quotes are confirmed within 24 hours.
- Never share API keys, internal systems, or fabricated client references.""",
}

app = Flask(__name__, static_folder=str(ROOT), static_url_path="")


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/api/chat", methods=["OPTIONS"])
def chat_options():
    return "", 204


@app.route("/api/chat", methods=["POST"])
def chat():
    if not GEMINI_API_KEY:
        return jsonify(
            {
                "error": (
                    "GEMINI_API_KEY is not set. Add it to your .env file or environment "
                    "variables, then restart the server."
                )
            }
        ), 503

    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    context = (data.get("context") or "sarah").lower()
    history = data.get("history") or []

    if not message:
        return jsonify({"error": "Message is required."}), 400
    if context not in SYSTEM_PROMPTS:
        return jsonify({"error": "Invalid context. Use 'alex' or 'sarah'."}), 400

    contents = []
    for turn in history[-10:]:
        role = turn.get("role", "")
        content = (turn.get("content") or "").strip()
        if not content:
            continue
        gemini_role = "user" if role == "user" else "model"
        contents.append({"role": gemini_role, "parts": [{"text": content}]})

    contents.append({"role": "user", "parts": [{"text": message}]})

    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPTS[context]}]},
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1024,
        },
    }

    try:
        resp = requests.post(
            GEMINI_URL,
            params={"key": GEMINI_API_KEY},
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        body = resp.json()
        candidates = body.get("candidates") or []
        if not candidates:
            return jsonify({"error": "Gemini returned no response."}), 502

        parts = candidates[0].get("content", {}).get("parts") or []
        reply = "".join(p.get("text", "") for p in parts).strip()
        if not reply:
            return jsonify({"error": "Gemini returned an empty response."}), 502

        return jsonify({"reply": reply, "context": context})
    except requests.HTTPError as err:
        detail = ""
        try:
            detail = err.response.json().get("error", {}).get("message", "")
        except Exception:
            detail = str(err)
        return jsonify({"error": f"Gemini API error: {detail}"}), 502
    except requests.RequestException as err:
        return jsonify({"error": f"Could not reach Gemini API: {err}"}), 502


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "port": PORT,
            "model": GEMINI_MODEL,
            "gemini_configured": bool(GEMINI_API_KEY),
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
    print(f"  Rose Empire Chat Server — {url}")
    print(f"  Model: {GEMINI_MODEL}")
    print(f"  Gemini API: {'configured' if GEMINI_API_KEY else 'MISSING — set GEMINI_API_KEY in .env'}")
    print("  Open the site at the URL above to test the chat widget.")
    print("=" * 52 + "\n")
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False, threaded=True)
