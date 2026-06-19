"""Dashboard KPIs and lead CRM helpers for the B2B outreach UI."""
from __future__ import annotations

import csv
import io
import re
from datetime import date
from pathlib import Path

from email_utils import is_valid_business_email
from outreach_leads import DEFAULT_OUTREACH, OUTREACH_COLUMNS, export_outreach_csv, update_outreach_row

ROOT = Path(__file__).resolve().parent
OUTREACH_DIR = ROOT / "linkedin-outreach"
QUALIFIED_CSV = OUTREACH_DIR / "qualified_manchester_leads.csv"
SEND_LOG = OUTREACH_DIR / "email_send_log.csv"
AVG_ORDER_VALUE = 1850


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _write_csv(path: Path, rows: list[dict[str, str]], fieldnames: tuple[str, ...] | list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def leads_csv_path() -> Path:
    if DEFAULT_OUTREACH.is_file():
        return DEFAULT_OUTREACH
    return QUALIFIED_CSV


def load_pipeline_leads() -> list[dict[str, str]]:
    path = leads_csv_path()
    rows = _read_csv(path)
    rows.sort(key=lambda r: (-int(r.get("score") or 0), (r.get("name") or "").lower()))
    return rows


def dashboard_stats() -> dict:
    rows = load_pipeline_leads()
    sent = sum(1 for r in rows if (r.get("email_status") or "").strip().lower() == "sent")
    if SEND_LOG.is_file():
        sent = max(sent, len(_read_csv(SEND_LOG)))
    contracts = max(1, sent // 3) if sent else 0
    return {
        "scraped_leads": len(rows),
        "pitches_sent": sent,
        "target_orders_gbp": contracts * AVG_ORDER_VALUE if sent else 0,
        "with_email": sum(1 for r in rows if is_valid_business_email((r.get("email") or "").strip())),
        "email_pending": sum(1 for r in rows if (r.get("email_status") or "pending") == "pending"),
    }


def import_leads_csv_text(text: str) -> dict[str, int]:
    text = text.strip()
    if not text:
        raise ValueError("Paste CSV data first.")

    sample = text.splitlines()[0]
    delimiter = "\t" if sample.count("\t") > sample.count(",") else ","
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    if not reader.fieldnames:
        raise ValueError("Could not parse CSV header.")

    incoming: list[dict[str, str]] = []
    for src in reader:
        name = (src.get("name") or src.get("company") or src.get("business") or "").strip()
        if not name:
            continue
        email = (src.get("email") or "").strip()
        row = {
            "name": name,
            "company": (src.get("company") or name).strip(),
            "email": email,
            "phone": (src.get("phone") or "").strip(),
            "website": (src.get("website") or src.get("url") or "").strip(),
            "linkedin": (src.get("linkedin") or "").strip(),
            "facility_type": (src.get("facility_type") or src.get("sector") or src.get("industry") or "").strip(),
            "city": (src.get("city") or "Manchester").strip(),
            "source": (src.get("source") or "import").strip(),
            "score": str(src.get("score") or "50"),
            "email_status": "pending" if is_valid_business_email(email) else "no_email",
            "call_status": "pending" if (src.get("phone") or "").strip() else "no_phone",
            "last_email_date": "",
            "notes": (src.get("notes") or "").strip(),
        }
        incoming.append(row)

    if not incoming:
        raise ValueError("No valid lead rows found in paste.")

    existing = {re.sub(r"[^a-z0-9]+", "", (r.get("website") or r.get("name") or "").lower()): r for r in load_pipeline_leads()}
    merged = 0
    for row in incoming:
        key = re.sub(r"[^a-z0-9]+", "", (row.get("website") or row.get("name") or "").lower())
        if key in existing:
            existing[key].update({k: v for k, v in row.items() if v})
            merged += 1
        else:
            existing[key] = row

    out_rows = list(existing.values())
    out_rows.sort(key=lambda r: (-int(r.get("score") or 0), (r.get("name") or "").lower()))
    _write_csv(DEFAULT_OUTREACH, out_rows, OUTREACH_COLUMNS)
    return {"imported": len(incoming), "merged": merged, "total": len(out_rows)}


def export_leads_csv_text() -> str:
    rows = load_pipeline_leads()
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=OUTREACH_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def mark_lead_sent(lead_key: str) -> None:
    update_outreach_row(
        DEFAULT_OUTREACH,
        lead_key=lead_key,
        email_status="sent",
        last_email_date=date.today().isoformat(),
    )


BLUEPRINTS = {
    "scraper": '''# Stealth Python Lead Scraper (Sarah) — Rose Empire
py -3 fleet_scraper.py --limit 10 --mission "care homes boutique hotels Manchester UK" --headed
py -3 lead_pipeline.py --qualify --enrich-emails --export-outreach''',
    "ollama_pitch": '''# Local Ollama pitch (free, unlimited) — James
# 1. Run: start_ollama.bat
py -3 fleet_ai.py --agent james "The Savoy Brighton Boutique Hotel"
# Or from dashboard: select lead → Generate Pitch → provider Ollama''',
    "gemini_pitch": '''# Cloud Gemini pitch (dashboard default)
# Requires GEMINI_API_KEY in .env
py -3 -c "from fleet_ai import draft_wholesale_pitch_with_ai; print(draft_wholesale_pitch_with_ai(company='Hotel Name', sector='Boutique Hotel & Resort Spas', prefer='gemini'))"''',
    "smtp_send": '''# Automated SMTP dispatcher — cooldown-safe batches
py -3 send_leads_emails.py --dry-run --limit 5
py -3 send_leads_emails.py --send --limit 5
# Uses INFO_EMAIL + EMAIL_PASSWORD from .env''',
}
