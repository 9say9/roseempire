"""Rose Empire — local AI Fleet Command dashboard (Flask).

For the website chat widget, run server.py instead (port 5000, Gemini 1.5 Flash).
"""
from __future__ import annotations

import os

from flask import Flask, jsonify, render_template, request

from fleet_ai import (
    analyze_leads_with_ollama,
    clean_leads_with_ollama,
    draft_email_pitch_with_ollama,
    ollama_available,
)
from fleet_scraper import scrape_all_leads

app = Flask(__name__)

PORT = int(os.environ.get("FLEET_PORT", "5050"))
HOST = os.environ.get("FLEET_HOST", "127.0.0.1")

INITIAL_AGENTS = [
    {
        "id": "lead_scraper",
        "name": "Sarah (Lead Scraper)",
        "role": "UK Mattress Lead Generation",
        "description": "Scrapes public data to identify independent UK B&Bs, boutique hotels, and guest houses.",
        "status": "Ready",
        "icon": "🔍",
    },
    {
        "id": "email_writer",
        "name": "James (Copywriter)",
        "role": "B2B Personalization",
        "description": "Drafts custom, high-converting cold pitches for premium waterproof mattress protectors.",
        "status": "Ready",
        "icon": "✍️",
    },
    {
        "id": "data_cleaner",
        "name": "Alex (Data Analyst)",
        "role": "Excel Operations",
        "description": "Organizes scraped lead tables, cleans bad records, and compiles down to spreadsheets.",
        "status": "Ready",
        "icon": "📊",
    },
]


@app.route("/health")
def health():
    return jsonify({"status": "ok", "port": PORT, "ollama": ollama_available()})


@app.route("/")
def home():
    return render_template("index.html", agents=INITIAL_AGENTS)


@app.route("/deploy-agent", methods=["POST"])
def deploy_agent():
    data = request.get_json(silent=True) or {}
    agent_id = data.get("agent_id")
    user_mission = (data.get("mission") or "").strip()

    if not agent_id:
        return jsonify({"status": "error", "message": "No agent selected."}), 400
    if not user_mission:
        return jsonify({"status": "error", "message": "Please enter mission targets first."}), 400

    if agent_id == "lead_scraper":
        try:
            leads = scrape_all_leads(user_mission, limit=5)
            if not leads:
                return jsonify(
                    {
                        "status": "success",
                        "message": (
                            "Sarah completed the web search but hit a temporary block. "
                            "Try: 'boutique hotels Manchester UK' or start Ollama with start_ollama.bat."
                        ),
                    }
                )

            raw_leads_text = "\n\n".join(leads)

            if ollama_available():
                try:
                    analysis = analyze_leads_with_ollama(user_mission, raw_leads_text)
                    return jsonify({"status": "success", "message": analysis})
                except Exception as ai_err:
                    return jsonify(
                        {
                            "status": "success",
                            "message": (
                                f"Sarah scraped live leads (AI analysis unavailable: {ai_err}):\n\n"
                                + raw_leads_text
                            ),
                        }
                    )

            return jsonify(
                {
                    "status": "success",
                    "message": (
                        "Sarah scraped live leads (start Ollama for AI ranking):\n\n" + raw_leads_text
                    ),
                }
            )
        except Exception as err:
            return jsonify(
                {"status": "error", "message": f"Sarah hit an operational error: {err}"}
            ), 500

    elif agent_id == "email_writer":
        try:
            if not ollama_available():
                return jsonify(
                    {
                        "status": "error",
                        "message": "James needs Ollama running. Start start_ollama.bat first.",
                    }
                ), 503
            pitch = draft_email_pitch_with_ollama(user_mission)
            return jsonify({"status": "success", "message": pitch})
        except Exception as err:
            return jsonify(
                {"status": "error", "message": f"James hit a processing error: {err}"}
            ), 500

    elif agent_id == "data_cleaner":
        try:
            if not ollama_available():
                return jsonify(
                    {
                        "status": "error",
                        "message": "Alex needs Ollama running. Start start_ollama.bat first.",
                    }
                ), 503
            table = clean_leads_with_ollama(user_mission)
            return jsonify({"status": "success", "message": table})
        except Exception as err:
            return jsonify(
                {"status": "error", "message": f"Alex hit an accounting parse error: {err}"}
            ), 500

    return jsonify(
        {
            "status": "success",
            "message": f"Directives routed to [{agent_id}]. Target mission verified: '{user_mission}'",
        }
    )


if __name__ == "__main__":
    url = f"http://{HOST}:{PORT}"
    print("\n" + "=" * 50)
    print(f"  Rose Empire AI Fleet — {url}")
    print(f"  Ollama AI: {'online' if ollama_available() else 'offline (run start_ollama.bat)'}")
    print("  Keep this window open while using the dashboard.")
    print("=" * 50 + "\n")
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False, threaded=True)
