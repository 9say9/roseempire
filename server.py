"""Rose Empire — chat API bridge (Gemini 1.5 Flash) + local static file server."""
from __future__ import annotations

import json
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

_PROMPTS_PATH = ROOT / "chat-prompts.json"
SYSTEM_PROMPTS = json.loads(_PROMPTS_PATH.read_text(encoding="utf-8"))

from email_agent import send_email

app = Flask(__name__, static_folder=str(ROOT), static_url_path="")


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    # Prevent connection hanging by adding a Keep-Alive header
    response.headers["Connection"] = "keep-alive"
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
        "systemInstruction": {"parts": [{"text": build_system_prompt(context, rules)}]},
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
            timeout=(5, 30),
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


@app.route("/api/send-email", methods=["POST"])
def api_send_email():
    data = request.get_json(silent=True) or {}
    recipient = data.get("recipient")
    subject = data.get("subject")
    body = data.get("body")

    if not recipient or not subject or not body:
        return jsonify({"error": "Recipient, subject, and body are required."}), 400

    success = send_email(recipient, subject, body)
    if success:
        return jsonify({"status": "success", "message": f"Email sent to {recipient}"})
    else:
        return jsonify({"status": "error", "message": "Failed to send email"}), 500


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
