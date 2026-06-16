"""Sarah / James / Adeel — Rose Empire sales fleet (Ollama free, OpenAI optional)."""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
OLLAMA_FALLBACK_MODELS = [
    m.strip()
    for m in os.getenv("OLLAMA_FALLBACK_MODELS", "qwen2.5-coder:1.5b,llama3.1:8b").split(",")
    if m.strip()
]

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1").rstrip("/")

# ollama (free) | openai (paid) | auto (ollama first)
AI_PROVIDER = os.getenv("AI_PROVIDER", "auto").lower()

ROSE_EMPIRE_FACTS = """
Rose Empire — Manchester wholesale B2B supplier.
Products: WQMP waterproof quilted protectors, QMP quilted protectors, Terry waterproof protectors, goose/duck down pillows (standard 50x75cm, 2-pillow sets).
MOQ: 20 pieces per size (one trade box). Discounts: 10% at 50+, 20% at 200+.
Trade pricing from ~GBP 2.40/piece protectors, ~GBP 8.50/piece pillows.
UK-wide delivery. Quote: roseempire.co.uk catalog -> RFQ -> PDF quote.
Contact: info@roseempire.co.uk, +44 7999 988450.
Landing for outreach: https://www.roseempire.co.uk/?utm_source=outreach&utm_medium=email&utm_campaign=manchester_b2b#catalog-section
Ideal buyers: care homes, hotels, guest houses, student accommodation, procurement managers in Greater Manchester.
"""

AGENTS = {
    "sarah": "Sarah — Lead Scraper & Qualifier. Find high-intent UK B2B buyers. Rank by facility type fit, Manchester proximity, website quality, and likelihood to order bulk bedding.",
    "james": "James — B2B Copywriter. Write short, professional cold emails that feel human, mention the buyer's facility type, one clear CTA to the catalog/quote page, no hype or spam triggers.",
    "adeel": "Adeel — Data Analyst. Clean lead tables, remove junk emails and ads, output valid CSV rows only.",
}


def ollama_online() -> bool:
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def ai_provider() -> str:
    if AI_PROVIDER == "openai":
        return "openai" if OPENAI_API_KEY else "none"
    if AI_PROVIDER == "ollama":
        return "ollama" if ollama_online() else "none"
    if ollama_online():
        return "ollama"
    if OPENAI_API_KEY:
        return "openai"
    return "none"


def ai_available() -> bool:
    return ai_provider() != "none"


def active_model() -> str:
    provider = ai_provider()
    if provider == "ollama":
        return OLLAMA_MODEL
    if provider == "openai":
        return OPENAI_MODEL
    return "none"


def _post_json(url: str, payload: dict, *, timeout: int = 180) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _call_ollama(system: str, user: str, *, temperature: float = 0.55, max_tokens: int = 1800) -> str:
    if not ollama_online():
        raise RuntimeError(
            "Ollama offline. Run start_ollama.bat or setup_free_bots.bat first."
        )

    models = [OLLAMA_MODEL, *OLLAMA_FALLBACK_MODELS]
    last_error = ""
    for model in models:
        try:
            data = _post_json(
                f"{OLLAMA_URL}/api/chat",
                {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "stream": False,
                    "keep_alive": "1h",
                    "options": {"temperature": temperature, "num_predict": max_tokens},
                },
            )
            text = (data.get("message") or {}).get("content", "").strip()
            if text:
                return text
            last_error = f"Empty response from {model}"
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code} from {model}"
        except Exception as exc:
            last_error = str(exc)

    raise RuntimeError(f"Ollama failed: {last_error}. Run: ollama pull {OLLAMA_MODEL}")


def _call_openai(system: str, user: str, *, temperature: float = 0.55, max_tokens: int = 1800) -> str:
    if not OPENAI_API_KEY:
        raise RuntimeError("OpenAI not configured. Add OPENAI_API_KEY to .env or use Ollama.")
    url = f"{OPENAI_API_BASE}/chat/completions"
    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers, timeout=(5, 120))
    response.raise_for_status()
    text = (response.json().get("choices") or [{}])[0].get("message", {}).get("content", "").strip()
    if not text:
        raise RuntimeError("Empty response from OpenAI.")
    return text


def _call_ai(system: str, user: str, *, temperature: float = 0.55, max_tokens: int = 1800) -> tuple[str, str]:
    provider = ai_provider()
    if provider == "ollama":
        return _call_ollama(system, user, temperature=temperature, max_tokens=max_tokens), OLLAMA_MODEL
    if provider == "openai":
        return _call_openai(system, user, temperature=temperature, max_tokens=max_tokens), OPENAI_MODEL
    raise RuntimeError(
        "No AI provider available. Run start_ollama.bat (free) or set OPENAI_API_KEY in .env."
    )


def analyze_leads_with_ai(mission: str, raw_leads_text: str) -> str:
    system = f"{ROSE_EMPIRE_FACTS}\n\n{AGENTS['sarah']}"
    user = (
        f"Mission: {mission}\n\nRaw leads:\n{raw_leads_text}\n\n"
        "Return:\n1) Top 5 ranked leads with score 1-10 and why\n"
        "2) Recommended next scrape query\n"
        "3) Which leads to email first vs LinkedIn only"
    )
    text, model = _call_ai(system, user)
    return f"[Sarah via {model}]\n\n{text}"


def draft_email_pitch_with_ai(customer_data: str) -> str:
    system = f"{ROSE_EMPIRE_FACTS}\n\n{AGENTS['james']}"
    user = (
        f"Lead data: {customer_data}\n\n"
        "Write a cold email. Format exactly:\n"
        "SUBJECT: <one line>\n"
        "BODY:\n<plain text, 120-180 words, sign off as Rose Empire Wholesale>"
    )
    text, model = _call_ai(system, user, temperature=0.65)
    return f"[James via {model}]\n\n{text}"


def parse_email_pitch(pitch_text: str) -> tuple[str, str]:
    text = pitch_text
    if "[James via" in text:
        text = text.split("\n\n", 1)[-1]
    subject_match = re.search(r"^SUBJECT:\s*(.+)$", text, re.I | re.M)
    body_match = re.search(r"^BODY:\s*\n([\s\S]+)$", text, re.I)
    subject = subject_match.group(1).strip() if subject_match else "Wholesale mattress protectors for your facility"
    body = body_match.group(1).strip() if body_match else text.strip()
    return subject, body


def clean_leads_with_ai(raw_data: str) -> str:
    system = f"{ROSE_EMPIRE_FACTS}\n\n{AGENTS['adeel']}"
    user = (
        f"Clean this lead data:\n{raw_data}\n\n"
        "Return CSV with header: name,email,phone,website,facility_type,score,notes\n"
        "Drop junk emails (bootstrap@, image filenames, placeholders). Keep only real UK businesses."
    )
    text, model = _call_ai(system, user, temperature=0.2)
    return f"[Adeel via {model}]\n\n{text}"


def rank_leads_json(mission: str, leads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not leads or not ai_available():
        return leads
    system = f"{ROSE_EMPIRE_FACTS}\n\n{AGENTS['sarah']}"
    user = (
        f"Mission: {mission}\n\nLeads JSON:\n{json.dumps(leads[:25], ensure_ascii=False)}\n\n"
        "Return ONLY a JSON array of objects with keys: name, priority_score (1-100), reason, recommended_action (email|linkedin|skip)."
    )
    try:
        raw, _model = _call_ai(system, user, temperature=0.3, max_tokens=2000)
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start >= 0 and end > start:
            ranked = json.loads(raw[start:end])
            return ranked if isinstance(ranked, list) else leads
    except Exception:
        pass
    return leads


# Backward-compatible aliases
ollama_available = ollama_online
analyze_leads_with_ollama = analyze_leads_with_ai
draft_email_pitch_with_ollama = draft_email_pitch_with_ai
clean_leads_with_ollama = clean_leads_with_ai


def _cli() -> int:
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Rose Empire fleet AI (James / Sarah / Adeel)")
    parser.add_argument(
        "email",
        nargs="?",
        help="Test target for James pitch (email or company name)",
    )
    parser.add_argument("--agent", choices=("james", "sarah", "adeel"), default="james")
    args = parser.parse_args()

    if not ai_available():
        print("ERROR: No AI provider. Run start_ollama.bat (free) or set OPENAI_API_KEY.", file=sys.stderr)
        return 1

    print(f"AI provider: {ai_provider()} ({active_model()})")

    try:
        if args.agent == "james":
            lead = args.email or "Test Hotel Manchester"
            if "@" in lead:
                lead = f"Facility contact: {lead}, boutique hotel Manchester UK"
            print(draft_email_pitch_with_ai(lead))
        elif args.agent == "sarah":
            print(analyze_leads_with_ai("care homes Manchester UK", "Sample Lead: Oak Care Home — Manchester"))
        else:
            print(clean_leads_with_ai("Oak Care Home, info@oakcare.co.uk, 0161 123 4567"))
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
