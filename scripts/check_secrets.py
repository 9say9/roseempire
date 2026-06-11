"""Scan tracked files for accidental secrets before deploy."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "github_browser_profile", "gsc_browser_profile"}
SKIP_FILES = {".env.example"}

PATTERNS = [
    (re.compile(r"GEMINI_API_KEY\s*=\s*['\"]?[A-Za-z0-9._\-]{20,}"), "GEMINI_API_KEY assignment"),
    (re.compile(r"EMAIL_PASSWORD\s*=\s*['\"]?[^\s'\"#]{8,}"), "EMAIL_PASSWORD assignment"),
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), "OpenAI-style API key"),
    (re.compile(r"\bAIza[A-Za-z0-9\-_]{30,}\b"), "Google API key"),
    (re.compile(r"\brnd_[A-Za-z0-9]{20,}\b"), "Render API key"),
    (re.compile(r"AQ\.[A-Za-z0-9\-_]{20,}"), "Google OAuth/API token"),
]

ALLOW_PLACEHOLDER = re.compile(r"your_.*_here|placeholder|example|xxx|<", re.I)


def scan_file(path: Path) -> list[str]:
    issues = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return issues
    for pattern, label in PATTERNS:
        for match in pattern.finditer(text):
            snippet = match.group(0)
            if ALLOW_PLACEHOLDER.search(snippet):
                continue
            issues.append(f"{path.relative_to(ROOT)}: possible {label}")
    if path.name == ".env":
        issues.append(f"{path.relative_to(ROOT)}: .env file must not be committed")
    return issues


def main() -> int:
    issues: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name in SKIP_FILES:
            continue
        if path.suffix in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".zip", ".pdf"}:
            continue
        issues.extend(scan_file(path))

    if issues:
        print("SECRET SCAN FAILED — possible credentials in repo:\n")
        for item in sorted(set(issues)):
            print(" ", item)
        return 1

    print("Secret scan passed — no obvious API keys or passwords in repo files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
