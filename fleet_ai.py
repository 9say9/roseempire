"""Sarah — local Ollama analysis for scraped leads."""
from __future__ import annotations

import os

import requests

OLLAMA_URL = os.getenv("OLLAMA_API_URL", "http://127.0.0.1:11434/api/generate")
OLLAMA_MODELS = [
    os.getenv("OLLAMA_MODEL", ""),
    "qwen2.5-coder:1.5b",
    "gemma3:4b",
    "qwen2.5-coder:7b",
]
OLLAMA_MODELS = [m for m in OLLAMA_MODELS if m]


def ollama_available() -> bool:
    try:
        r = requests.get("http://127.0.0.1:11434/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def analyze_leads_with_ollama(mission: str, raw_leads_text: str) -> str:
    prompt = (
        "You are Sarah, the Lead Generation Specialist for Rose Empire wholesale mattress protectors.\n"
        f"Analyze these raw search results for the query: '{mission}'\n\n"
        f"RAW DATA EXTRACTED:\n{raw_leads_text}\n\n"
        "YOUR TASK:\n"
        "Filter through these results. Identify which look like genuine UK businesses "
        "(hotels, B&Bs, care homes, student housing, guest houses).\n"
        "Briefly explain WHY each might need waterproof mattress protectors for commercial use.\n"
        "Rank them from best to worst lead. Keep the response structured and business-focused."
    )

    return _call_ollama(prompt, "Sarah AI analysis")


def _call_ollama(prompt: str, agent_label: str) -> str:
    last_error = "Ollama not reachable."
    for model in OLLAMA_MODELS:
        try:
            response = requests.post(
                OLLAMA_URL,
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=60,
            )
            response.raise_for_status()
            text = response.json().get("response", "").strip()
            if text:
                return f"[{agent_label} via {model}]\n\n{text}"
            last_error = f"Empty response from {model}."
        except Exception as err:
            last_error = str(err)
            continue
    raise RuntimeError(last_error)


def draft_email_pitch_with_ollama(customer_data: str) -> str:
    prompt = (
        "You are James, the expert B2B Copywriter for Rose Empire.\n"
        "Your company sells commercial-grade, 100% waterproof, breathable, anti-allergy, "
        "and noiseless mattress protectors to UK businesses.\n\n"
        f"CUSTOMER DATA provided by user:\n{customer_data}\n\n"
        "YOUR TASK:\n"
        "Write a highly professional, short, and punchy B2B cold outreach email template "
        "that can be sent to these targets.\n"
        "Include a compelling Subject Line emphasizing asset protection and hygiene for their mattresses.\n"
        "Keep the email tone polite, professional, and explicitly focused on how Rose Empire "
        "saves them money on mattress replacements.\n"
        "Add clear [Bracket Placeholders] for names and details where necessary."
    )
    return _call_ollama(prompt, "James B2B pitch")


def clean_leads_with_ollama(raw_data: str) -> str:
    prompt = (
        "You are Alex, the Data Analyst for Rose Empire.\n"
        "You excel at data cleaning and structuring messy text entries into clean table formats.\n\n"
        f"RAW DATA TO CLEAN:\n{raw_data}\n\n"
        "YOUR TASK:\n"
        "Extract any business names, website links, locations, or descriptions from the text provided.\n"
        "Remove junk characters and fix formatting mistakes.\n"
        "Organize them into a clean markdown table with headers: "
        "| Business Name | Estimated Industry | Key Focus Area |.\n"
        "Directly beneath the table, provide comma-separated CSV rows for those same items "
        "so the user can copy and paste into Microsoft Excel. Keep everything neat."
    )
    return _call_ollama(prompt, "Alex CSV export")
