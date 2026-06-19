"""Rose Empire — local AI Fleet Command dashboard (Flask).

For the website chat widget, run server.py instead (port 5000, Gemini 1.5 Flash).
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify, render_template, request

from fleet_ai import (
    active_model,
    ai_available,
    ai_provider,
    analyze_leads_with_ai,
    clean_leads_with_ai,
    draft_email_pitch_with_ai,
    draft_wholesale_pitch_with_ai,
    ollama_online,
    parse_email_pitch,
)
from fleet_scraper import scrape_fresh_leads
from manchester_sales_pipeline import run_pipeline
from sales_engine import run_sales_cycle
from dashboard_api import (
    BLUEPRINTS,
    dashboard_stats,
    export_leads_csv_text,
    import_leads_csv_text,
    load_pipeline_leads,
    mark_lead_sent,
)
from email_agent import send_email
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATALOG_PDF = ROOT / "assets" / "Rose-Empire-Wholesale-Catalog.pdf"

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False


@app.after_request
def _utf8_headers(response):
    if response.content_type and response.content_type.startswith("text/html"):
        response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response

PORT = int(os.environ.get("FLEET_PORT", "5050"))
HOST = os.environ.get("FLEET_HOST", "127.0.0.1")

INITIAL_AGENTS = [
    {
        "id": "lead_scraper",
        "name": "Sarah (Lead Scraper)",
        "role": "UK Mattress Lead Generation",
        "description": "Scrapes Google Maps, LinkedIn, web search, Reddit, Facebook and Instagram for fresh B2B leads.",
        "status": "Ready",
        "icon": "S",
    },
    {
        "id": "email_writer",
        "name": "James (Copywriter)",
        "role": "B2B Personalization",
        "description": "Drafts custom, high-converting cold pitches for premium waterproof mattress protectors.",
        "status": "Ready",
        "icon": "J",
    },
    {
        "id": "data_cleaner",
        "name": "Adeel (Data Analyst)",
        "role": "Excel Operations",
        "description": "Organizes scraped lead tables, cleans bad records, and compiles down to spreadsheets.",
        "status": "Ready",
        "icon": "A",
    },
]


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "port": PORT,
        "ai": ai_available(),
        "provider": ai_provider(),
        "model": active_model(),
        "ollama": ollama_online(),
        "gemini": bool(os.getenv("GEMINI_API_KEY")),
    })


@app.route("/api/dashboard")
def api_dashboard():
    stats = dashboard_stats()
    return jsonify({
        **stats,
        "ollama_online": ollama_online(),
        "ai_provider": ai_provider(),
        "ai_model": active_model(),
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        "scraping_ready": True,
    })


@app.route("/api/leads")
def api_leads():
    return jsonify({"leads": load_pipeline_leads()})


@app.route("/api/leads/import", methods=["POST"])
def api_leads_import():
    data = request.get_json(silent=True) or {}
    text = (data.get("csv") or "").strip()
    try:
        result = import_leads_csv_text(text)
        return jsonify({"status": "success", **result})
    except ValueError as exc:
        return jsonify({"status": "error", "message": str(exc)}), 400


@app.route("/api/leads/export")
def api_leads_export():
    from flask import Response
    return Response(
        export_leads_csv_text(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=outreach_master.csv"},
    )


@app.route("/api/pitch", methods=["POST"])
def api_pitch():
    data = request.get_json(silent=True) or {}
    company = (data.get("company") or data.get("name") or "").strip()
    if not company:
        return jsonify({"status": "error", "message": "Company name required."}), 400
    sector = (data.get("sector") or data.get("facility_type") or "Commercial Buyer").strip()
    website = (data.get("website") or "").strip()
    products = (data.get("products") or "Protectors, Pillows").strip()
    city = (data.get("city") or "UK").strip()
    prefer = (data.get("provider") or "gemini").strip().lower()
    if prefer == "auto":
        prefer = None
    try:
        raw = draft_wholesale_pitch_with_ai(
            company=company,
            sector=sector,
            website=website,
            products=products,
            city=city,
            prefer=prefer if prefer in ("gemini", "ollama", "openai") else "gemini",
        )
        subject, body = parse_email_pitch(raw)
        why_fit = ""
        value_props = ""
        if "WHY_FIT:" in raw:
            why_fit = raw.split("WHY_FIT:", 1)[-1].split("VALUE_PROPS:", 1)[0].strip()
        if "VALUE_PROPS:" in raw:
            value_props = raw.split("VALUE_PROPS:", 1)[-1].strip()
        return jsonify({
            "status": "success",
            "raw": raw,
            "subject": subject,
            "body": body,
            "why_fit": why_fit,
            "value_props": value_props,
            "provider": ai_provider(prefer),
            "model": active_model(prefer),
        })
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 503


@app.route("/api/pitch/send", methods=["POST"])
def api_pitch_send():
    data = request.get_json(silent=True) or {}
    to_email = (data.get("email") or "").strip()
    subject = (data.get("subject") or "").strip()
    body = (data.get("body") or "").strip()
    lead_key = (data.get("lead_key") or "").strip()
    if not to_email or not subject or not body:
        return jsonify({"status": "error", "message": "email, subject, and body required."}), 400
    try:
        attachments = [CATALOG_PDF] if CATALOG_PDF.is_file() else []
        send_email(to_email, subject, body, attachments=attachments or None)
        if lead_key:
            mark_lead_sent(lead_key)
        return jsonify({"status": "success", "message": f"Sent to {to_email}"})
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/api/scrape", methods=["POST"])
def api_scrape():
    data = request.get_json(silent=True) or {}
    mission = (data.get("mission") or "care homes boutique hotels Manchester UK").strip()
    limit = int(data.get("limit") or 8)
    try:
        leads = scrape_fresh_leads(mission, limit=limit)
        return jsonify({
            "status": "success",
            "message": f"Sarah scraped {len(leads)} lead(s). Run qualify to sync pipeline.",
            "count": len(leads),
        })
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/api/qualify", methods=["POST"])
def api_qualify():
    try:
        from lead_pipeline import merge_and_qualify, save_leads
        from outreach_leads import export_outreach_csv
        leads = merge_and_qualify(manchester_only=True, min_score=35)
        out = ROOT / "linkedin-outreach" / "qualified_manchester_leads.csv"
        save_leads(leads, out)
        stats = export_outreach_csv(out)
        return jsonify({"status": "success", "qualified": len(leads), "stats": stats})
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/api/blueprints")
def api_blueprints():
    return jsonify(BLUEPRINTS)


@app.route("/")
def home():
    return render_template("index.html", agents=INITIAL_AGENTS)


@app.route("/run-pipeline", methods=["POST"])
def run_sales_pipeline():
    data = request.get_json(silent=True) or {}
    limit = int(data.get("limit") or 5)
    send = bool(data.get("send"))
    code = run_pipeline(limit=limit, send=send, enrich=True)
    if code != 0:
        return jsonify({"status": "error", "message": "Pipeline found no leads. Run scrapers first."}), 400
    mode = "sent" if send else "dry-run"
    return jsonify({"status": "success", "message": f"Manchester pipeline complete ({mode}). See linkedin-outreach/qualified_manchester_leads.csv"})


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
            leads = scrape_fresh_leads(user_mission, limit=8)
            if not leads:
                return jsonify(
                    {
                        "status": "success",
                        "message": (
                            "Sarah completed the web search but hit a temporary block. "
                            "Try: 'boutique hotels Manchester UK' or run start_ollama.bat for free AI."
                        ),
                    }
                )

            raw_leads_text = "\n\n".join(leads)

            if ai_available():
                try:
                    analysis = analyze_leads_with_ai(user_mission, raw_leads_text)
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
                        "Sarah scraped live leads (run start_ollama.bat for AI ranking):\n\n" + raw_leads_text
                    ),
                }
            )
        except Exception as err:
            return jsonify(
                {"status": "error", "message": f"Sarah hit an operational error: {err}"}
            ), 500

    elif agent_id == "email_writer":
        try:
            if not ai_available():
                return jsonify(
                    {
                        "status": "error",
                        "message": "James needs AI. Run start_ollama.bat (free) or set OPENAI_API_KEY in .env.",
                    }
                ), 503
            pitch = draft_email_pitch_with_ai(user_mission)
            return jsonify({"status": "success", "message": pitch})
        except Exception as err:
            return jsonify(
                {"status": "error", "message": f"James hit a processing error: {err}"}
            ), 500

    elif agent_id == "data_cleaner":
        try:
            if not ai_available():
                return jsonify(
                    {
                        "status": "error",
                        "message": "Adeel needs AI. Run start_ollama.bat (free) or set OPENAI_API_KEY in .env.",
                    }
                ), 503
            table = clean_leads_with_ai(user_mission)
            return jsonify({"status": "success", "message": table})
        except Exception as err:
            return jsonify(
                {"status": "error", "message": f"Adeel hit an accounting parse error: {err}"}
            ), 500

    return jsonify(
        {
            "status": "success",
            "message": f"Directives routed to [{agent_id}]. Target mission verified: '{user_mission}'",
        }
    )



@app.route("/system-status")
def system_status():
    from pathlib import Path as P
    from email_utils import is_valid_business_email
    from lead_pipeline import merge_and_qualify

    root = P(__file__).resolve().parent
    leads = merge_and_qualify(manchester_only=True, min_score=35)
    with_email = sum(1 for l in leads if l.email and is_valid_business_email(l.email))
    smtp_ok = False
    try:
        import os
        import smtplib
        from dotenv import load_dotenv
        load_dotenv()
        sender = os.getenv("INFO_EMAIL") or os.getenv("EMAIL_ADDRESS")
        pwd = os.getenv("EMAIL_PASSWORD")
        if sender and pwd:
            with smtplib.SMTP("smtp.office365.com", 587, timeout=10) as s:
                s.starttls()
                s.login(sender, pwd)
            smtp_ok = True
    except Exception:
        smtp_ok = False

    return jsonify({
        "openai": ai_available(),
        "ai_provider": ai_provider(),
        "ai_model": active_model(),
        "smtp": smtp_ok,
        "qualified_leads": len(leads),
        "leads_with_valid_email": with_email,
        "csv": str(root / "linkedin-outreach" / "qualified_manchester_leads.csv"),
    })


@app.route("/run-sales-cycle", methods=["POST"])
def run_full_sales_cycle():
    data = request.get_json(silent=True) or {}
    mission = (data.get("mission") or "care homes hotels guest houses Manchester UK").strip()
    limit = int(data.get("limit") or 5)
    send = bool(data.get("send"))
    scrape = bool(data.get("scrape"))
    stats = run_sales_cycle(mission=mission, limit=limit, send=send, scrape_first=scrape)
    if not stats.get("qualified"):
        return jsonify({"status": "error", "message": "No qualified leads. Try scrape=true or run Sarah first.", "stats": stats}), 400
    mode = "sent" if send else "dry-run"
    return jsonify({
        "status": "success",
        "message": f"Sales cycle complete ({mode}). Processed {stats.get('processed', 0)} leads.",
        "stats": stats,
    })

if __name__ == "__main__":
    url = f"http://{HOST}:{PORT}"
    print("\n" + "=" * 50)
    print(f"  Rose Empire AI Fleet — {url}")
    provider = ai_provider()
    print(f"  AI: {provider} ({active_model()})" if ai_available() else "  AI: offline — run start_ollama.bat (free)")
    print("  Keep this window open while using the dashboard.")
    print("=" * 50 + "\n")
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False, threaded=True)

