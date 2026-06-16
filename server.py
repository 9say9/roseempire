"""Rose Empire ? chat API bridge (OpenAI GPT-4o-mini or Gemini) + static file server."""
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
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_BASE = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1").rstrip("/")

_PROMPTS_PATH = ROOT / "chat-prompts.json"
SYSTEM_PROMPTS = json.loads(_PROMPTS_PATH.read_text(encoding="utf-8"))

from catalog_prompt import build_system_prompt
from email_agent import send_email


def _chat_provider() -> str:
    if OPENAI_API_KEY:
        return "openai"
    if GEMINI_API_KEY:
        return "gemini"
    return ""


def _chat_openai(system: str, history: list, message: str) -> str:
    messages = [{"role": "system", "content": system}]
    for turn in history[-10:]:
        role = turn.get("role", "user")
        content = (turn.get("content") or "").strip()
        if not content:
            continue
        messages.append({"role": "user" if role == "user" else "assistant", "content": content})
    messages.append({"role": "user", "content": message})
    resp = requests.post(
        f"{OPENAI_API_BASE}/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
        json={"model": OPENAI_MODEL, "messages": messages, "temperature": 0.7, "max_tokens": 1024},
        timeout=(5, 60),
    )
    resp.raise_for_status()
    reply = (resp.json().get("choices") or [{}])[0].get("message", {}).get("content", "").strip()
    if not reply:
        raise RuntimeError("OpenAI returned an empty response.")
    return reply


def _chat_gemini(system: str, history: list, message: str) -> str:
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
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1024},
    }
    resp = requests.post(GEMINI_URL, params={"key": GEMINI_API_KEY}, json=payload, timeout=(5, 30))
    resp.raise_for_status()
    body = resp.json()
    candidates = body.get("candidates") or []
    if not candidates:
        raise RuntimeError("Gemini returned no response.")
    parts = candidates[0].get("content", {}).get("parts") or []
    reply = "".join(p.get("text", "") for p in parts).strip()
    if not reply:
        raise RuntimeError("Gemini returned an empty response.")
    return reply


app = Flask(__name__, static_folder=str(ROOT), static_url_path="")


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Connection"] = "keep-alive"
    return response


@app.route("/api/chat", methods=["OPTIONS"])
def chat_options():
    return "", 204


@app.route("/api/chat", methods=["POST"])
def chat():
    provider = _chat_provider()
    if not provider:
        return jsonify({"error": "Set OPENAI_API_KEY or GEMINI_API_KEY in .env, then restart."}), 503

    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    context = (data.get("context") or "sarah").lower()\n    if context == "alex":\n        context = "adeel"
    history = data.get("history") or []

    if not message:
        return jsonify({"error": "Message is required."}), 400
    if context not in SYSTEM_PROMPTS:
        return jsonify({"error": "Invalid context. Use 'adeel' or 'sarah'."}), 400

    system = build_system_prompt(context)
    try:
        if provider == "openai":
            reply = _chat_openai(system, history, message)
        else:
            reply = _chat_gemini(system, history, message)
        return jsonify({"reply": reply, "context": context, "provider": provider})
    except requests.HTTPError as err:
        detail = ""
        try:
            detail = err.response.json().get("error", {}).get("message", str(err))
        except Exception:
            detail = str(err)
        return jsonify({"error": f"AI API error: {detail}"}), 502
    except requests.RequestException as err:
        return jsonify({"error": f"Could not reach AI API: {err}"}), 502
    except RuntimeError as err:
        return jsonify({"error": str(err)}), 502


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
    return jsonify({"status": "error", "message": "Failed to send email"}), 500


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "port": PORT,
        "model": OPENAI_MODEL if OPENAI_API_KEY else GEMINI_MODEL,
        "provider": _chat_provider() or "none",
        "openai_configured": bool(OPENAI_API_KEY),
        "gemini_configured": bool(GEMINI_API_KEY),
    })


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
    prov = _chat_provider() or "none"
    model = OPENAI_MODEL if OPENAI_API_KEY else GEMINI_MODEL
    print("\n" + "=" * 52)
    print(f"  Rose Empire Chat Server ? {url}")
    print(f"  AI provider: {prov} | Model: {model}")
    print("  Open the site at the URL above to test the chat widget.")
    print("=" * 52 + "\n")
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False, threaded=True)

