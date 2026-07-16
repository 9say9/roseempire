"""Scan tracked files for accidental secrets before deploy."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SKIP_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "github_browser_profile",
    "gsc_browser_profile",
    "m365_browser_profile",
}
SKIP_FILES = {".env.example"}
SKIP_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".zip", ".pdf",
    ".pma", ".db", ".wal", ".pb", ".dat", ".bin", ".tmp",
}

PATTERNS = [
    (re.compile(r"GEMINI_API_KEY\s*=\s*['\"]?[A-Za-z0-9._\-]{20,}"), "GEMINI_API_KEY assignment"),
    (re.compile(r"EMAIL_PASSWORD\s*=\s*['\"]?[^\s'\"#]{8,}"), "EMAIL_PASSWORD assignment"),
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), "OpenAI-style API key"),
    (re.compile(r"\bsk_(live|test)_[A-Za-z0-9]{20,}\b"), "Stripe secret key"),
    (re.compile(r"\bpk_(live|test)_[A-Za-z0-9]{20,}\b"), "Stripe publishable key"),
    (re.compile(r"\bAIza[A-Za-z0-9\-_]{30,}\b"), "Google API key"),
    (re.compile(r"\brnd_[A-Za-z0-9]{20,}\b"), "Render API key"),
    (re.compile(r"AQ\.[A-Za-z0-9\-_]{20,}"), "Google OAuth/API token"),
    (re.compile(r"sarah_admin=[A-Za-z0-9_\-]{12,}"), "Sarah admin token in URL"),
    (re.compile(r"rose-empire-owner-\d{4}"), "Hardcoded Sarah owner token"),
]

ALLOW_PLACEHOLDER = re.compile(r"your_.*_here|placeholder|example|xxx|<|sk_test_your_|pk_test_your_", re.I)


def _tracked_files() -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=ROOT,
            capture_output=True,
            check=True,
        )
        return [
            ROOT / rel
            for rel in result.stdout.decode("utf-8", errors="replace").split("\0")
            if rel
        ]
    except Exception:
        return [p for p in ROOT.rglob("*") if p.is_file()]


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
    for path in _tracked_files():
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name in SKIP_FILES:
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
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
