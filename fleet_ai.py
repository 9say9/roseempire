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
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:1.5b")
OLLAMA_FALLBACK_MODELS = [
    m.strip()
    for m in os.getenv("OLLAMA_FALLBACK_MODELS", "qwen2.5-coder:1.5b,qwen2.5-coder:7b").split(",")
    if m.strip()
]

AI_ROUTER_URL = os.getenv("AI_ROUTER_URL", "http://127.0.0.1:8000/v1").rstrip("/")
AI_ROUTER_MODEL = os.getenv("AI_ROUTER_MODEL", "gpt-3.5-turbo")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1").rstrip("/")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)

# router (local gateway) | ollama (free) | gemini (cloud) | openai (paid) | auto
AI_PROVIDER = os.getenv("AI_PROVIDER", "router").lower()

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
    "james": "James — B2B Copywriter. Write short, professional cold emails that feel human, mention the recipient company name by name, reference the buyer's facility type, use one clear CTA to the catalog/quote page, and never leave out the company name or call to action.",
    "adeel": "Adeel — Data Analyst. Clean lead tables, remove junk emails and ads, output valid CSV rows only.",
}


def router_online() -> bool:
    try:
        base = AI_ROUTER_URL.removesuffix("/v1")
        req = urllib.request.Request(f"{base}/health", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


def ollama_online() -> bool:
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def _installed_ollama_models() -> list[str]:
    if not ollama_online():
        return []
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return [m.get("name", "") for m in body.get("models", []) if m.get("name")]
    except Exception:
        return []


def _resolve_ollama_model(name: str, installed: list[str]) -> str | None:
    if name in installed:
        return name
    base = name.split(":")[0]
    for item in installed:
        if item == name or item.startswith(base + ":"):
            return item
    return None


def _ollama_models_to_try() -> list[str]:
    installed = [m for m in _installed_ollama_models() if not m.endswith("-cloud")]
    ordered: list[str] = []
    for candidate in [OLLAMA_MODEL, *OLLAMA_FALLBACK_MODELS]:
        resolved = _resolve_ollama_model(candidate, installed) if installed else candidate
        if resolved and resolved not in ordered:
            ordered.append(resolved)
    if installed:
        for item in installed:
            if item not in ordered:
                ordered.append(item)
    return ordered or [OLLAMA_MODEL, *OLLAMA_FALLBACK_MODELS]


def _primary_ollama_model() -> str:
    models = _ollama_models_to_try()
    return models[0] if models else OLLAMA_MODEL


def ai_provider(prefer: str | None = None) -> str:
    mode = (prefer or AI_PROVIDER).lower()
    if mode == "router":
        return "router" if router_online() else "none"
    if mode == "gemini":
        return "gemini" if GEMINI_API_KEY else "none"
    if mode == "openai":
        return "openai" if OPENAI_API_KEY else "none"
    if mode == "ollama":
        return "ollama" if ollama_online() else "none"
    if router_online():
        return "router"
    if ollama_online():
        return "ollama"
    if GEMINI_API_KEY:
        return "gemini"
    if OPENAI_API_KEY:
        return "openai"
    return "none"


def ai_available(prefer: str | None = None) -> bool:
    return ai_provider(prefer) != "none"


def active_model(prefer: str | None = None) -> str:
    provider = ai_provider(prefer)
    if provider == "router":
        return AI_ROUTER_MODEL
    if provider == "ollama":
        return _primary_ollama_model()
    if provider == "gemini":
        return GEMINI_MODEL
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


def _call_router(system: str, user: str, *, temperature: float = 0.55, max_tokens: int = 1800) -> tuple[str, str]:
    if not router_online():
        raise RuntimeError("AI Router offline. Run start_ai_router.bat first.")
    payload = {
        "model": AI_ROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    headers = {"Authorization": "Bearer local", "Content-Type": "application/json"}
    response = requests.post(
        f"{AI_ROUTER_URL}/chat/completions",
        json=payload,
        headers=headers,
        timeout=(5, 180),
    )
    response.raise_for_status()
    body = response.json()
    text = (body.get("choices") or [{}])[0].get("message", {}).get("content", "").strip()
    if not text:
        raise RuntimeError("Empty response from AI Router.")
    used = body.get("model", AI_ROUTER_MODEL)
    return text, used


def _call_ollama(system: str, user: str, *, temperature: float = 0.55, max_tokens: int = 1800) -> tuple[str, str]:
    if not ollama_online():
        raise RuntimeError(
            "Ollama offline. Run start_ollama.bat or setup_free_bots.bat first."
        )

    models = _ollama_models_to_try()
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
                return text, model
            last_error = f"Empty response from {model}"
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code} from {model}"
        except Exception as exc:
            last_error = str(exc)

    raise RuntimeError(
        f"Ollama failed: {last_error}. Installed: {', '.join(_installed_ollama_models()) or 'none'}. "
        f"Run: ollama pull {OLLAMA_MODEL}"
    )


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


def _call_gemini(system: str, user: str, *, temperature: float = 0.65, max_tokens: int = 1800) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("Gemini not configured. Add GEMINI_API_KEY to .env.")
    payload = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
    }
    response = requests.post(GEMINI_URL, params={"key": GEMINI_API_KEY}, json=payload, timeout=(5, 120))
    response.raise_for_status()
    body = response.json()
    candidates = body.get("candidates") or []
    if not candidates:
        raise RuntimeError("Gemini returned no response.")
    parts = candidates[0].get("content", {}).get("parts") or []
    text = "".join(p.get("text", "") for p in parts).strip()
    if not text:
        raise RuntimeError("Gemini returned an empty response.")
    return text


def _provider_chain(prefer: str | None = None) -> list[str]:
    if prefer and prefer != "auto":
        return [prefer.lower()]
    chain: list[str] = []
    if AI_PROVIDER not in ("auto", ""):
        chain.append(AI_PROVIDER)
    for candidate in ("openai", "ollama", "router", "gemini"):
        if candidate not in chain:
            chain.append(candidate)
    return chain


def _invoke_provider(
    provider: str,
    system: str,
    user: str,
    *,
    temperature: float,
    max_tokens: int,
) -> tuple[str, str]:
    if provider == "router":
        return _call_router(system, user, temperature=temperature, max_tokens=max_tokens)
    if provider == "ollama":
        return _call_ollama(system, user, temperature=temperature, max_tokens=max_tokens)
    if provider == "gemini":
        return _call_gemini(system, user, temperature=temperature, max_tokens=max_tokens), GEMINI_MODEL
    if provider == "openai":
        return _call_openai(system, user, temperature=temperature, max_tokens=max_tokens), OPENAI_MODEL
    raise RuntimeError(f"Unknown AI provider: {provider}")


def _call_ai(
    system: str,
    user: str,
    *,
    temperature: float = 0.55,
    max_tokens: int = 1800,
    prefer: str | None = None,
) -> tuple[str, str]:
    errors: list[str] = []
    for provider in _provider_chain(prefer):
        if provider == "router" and not router_online():
            continue
        if provider == "ollama" and not ollama_online():
            continue
        if provider == "gemini" and not GEMINI_API_KEY:
            continue
        if provider == "openai" and not OPENAI_API_KEY:
            continue
        try:
            return _invoke_provider(
                provider,
                system,
                user,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as exc:
            errors.append(f"{provider}: {exc}")
            continue
    detail = "; ".join(errors[-4:]) if errors else "no providers configured"
    raise RuntimeError(
        "All AI providers failed. " + detail + ". Run start_ollama.bat or check API keys/rate limits."
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


SECTOR_PAIN_POINTS = {
    "Boutique Hotel & Resort Spas": "guest comfort, premium linen standards, fast room turnaround",
    "Care Home & Nursing": "heavy sanitizing, waterproof durability, infection control compliance",
    "Student Accommodation": "high turnover, budget durability, bulk replacement cycles",
    "Guest House & B&B": "cost-effective quality, easy laundering, low MOQ flexibility",
    "Procurement / Facilities": "supplier consolidation, trade pricing, reliable UK delivery",
}


def draft_wholesale_pitch_with_ai(
    *,
    company: str,
    sector: str = "Commercial Buyer",
    website: str = "",
    products: str = "Protectors, Pillows",
    city: str = "UK",
    prefer: str | None = None,
) -> str:
    pains = SECTOR_PAIN_POINTS.get(sector, "operational efficiency, guest comfort, and supplier reliability")
    system = f"""{ROSE_EMPIRE_FACTS}

{AGENTS['james']}

You write B2B wholesale cold emails for Rose Empire mattress protectors and pillows.
Emphasize sector pain points: {pains}.
Products in scope: {products}."""
    user = f"""Target: {company}
Sector: {sector}
Website: {website or 'unknown'}
City/region: {city}

Return exactly this structure:

SUBJECT: <one compelling line>

BODY:
<120-180 words, plain text, human tone, explicitly mention the company name in the greeting and first paragraph, one clear CTA to catalog quote page>

WHY_FIT:
<2-3 sentences on why this prospect is a strong wholesale buyer>

VALUE_PROPS:
1. <retail/operational value prop>
2. <product quality value prop>
3. <commercial/trade value prop>"""
    text, model = _call_ai(system, user, temperature=0.65, prefer=prefer or "auto")
    return f"[James via {model}]\n\n{text}"


def draft_email_pitch_with_ai(customer_data: str, prefer: str | None = None) -> str:
    system = f"{ROSE_EMPIRE_FACTS}\n\n{AGENTS['james']}"
    user = (
        f"Lead data: {customer_data}\n\n"
        "Write a cold email for the specific company in the lead data. Mention the company name in the greeting and first paragraph. Never leave out the company name. Format exactly:\n"
        "SUBJECT: <one line>\n"
        "BODY:\n<plain text, 120-180 words, sign off as Rose Empire Wholesale, include one clear CTA to the catalog or quote page>"
    )
    text, model = _call_ai(system, user, temperature=0.65, prefer=prefer or "auto")
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
        print("ERROR: No AI provider. Run start_ai_router.bat or start_ollama.bat.", file=sys.stderr)
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
