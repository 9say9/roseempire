from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parent
ENV_PATH = ROOT / ".env"
ENV_EXAMPLE_PATH = ROOT / ".env.example"


def _run(cmd: Sequence[str], *, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    print(f"\n>> {' '.join(cmd)}")
    completed = subprocess.run(list(cmd), cwd=str(cwd or ROOT), text=True)
    if check and completed.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {completed.returncode}: {' '.join(cmd)}")
    return completed


def ensure_env() -> None:
    if ENV_PATH.exists():
        return
    if ENV_EXAMPLE_PATH.exists():
        shutil.copy2(ENV_EXAMPLE_PATH, ENV_PATH)
        print(f"Created {ENV_PATH.name} from {ENV_EXAMPLE_PATH.name}.")
    else:
        print("No .env or .env.example found; continuing with existing environment if present.")


def start_ollama() -> None:
    if os.name != "nt":
        print("Ollama startup is currently intended for Windows; skipping.")
        return
    ollama_exe = Path(os.getenv("LOCALAPPDATA", "")) / "Programs" / "Ollama" / "ollama.exe"
    if not ollama_exe.exists():
        print("Ollama executable not found; skipping startup.")
        return
    try:
        _run(["cmd", "/c", "start_ollama.bat", "silent"], check=False)
    except Exception as exc:
        print(f"Ollama startup warning: {exc}")


def run_pipeline(args: argparse.Namespace) -> int:
    ensure_env()
    start_ollama()

    if args.check_only:
        print("Configuration check complete. Local launcher is ready.")
        return 0

    if not args.skip_scrape:
        _run([sys.executable, "fleet_scraper.py", "--limit", str(args.limit), "--mission", args.mission])

    _run([sys.executable, "lead_pipeline.py", "--qualify", "--export-outreach"])

    if args.draft_sample:
        _run([sys.executable, "fleet_ai.py", "--agent", "james", args.mission])

    if args.email_mode == "dry-run":
        _run([sys.executable, "send_leads_emails.py", "--dry-run", "--limit", str(args.email_limit)])
    elif args.email_mode == "send":
        _run([sys.executable, "send_leads_emails.py", "--send", "--limit", str(args.email_limit)])

    if args.dashboard:
        print("Starting dashboard in a separate window...")
        if os.name == "nt":
            subprocess.Popen(["cmd", "/c", "run_ai_fleet.bat"], cwd=str(ROOT), creationflags=subprocess.CREATE_NEW_CONSOLE if hasattr(subprocess, "CREATE_NEW_CONSOLE") else 0)
        else:
            subprocess.Popen(["bash", "-lc", "./run_ai_fleet.bat"], cwd=str(ROOT))

    print("\nRose Empire local launcher completed.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="One-click local Rose Empire launcher")
    parser.add_argument("--limit", type=int, default=10, help="Number of leads to scrape")
    parser.add_argument("--mission", default="care homes Manchester UK", help="Sarah search mission")
    parser.add_argument("--skip-scrape", action="store_true", help="Skip Sarah scrape step")
    parser.add_argument("--draft-sample", action="store_true", help="Run a sample James draft")
    parser.add_argument("--email-mode", choices=["none", "dry-run", "send"], default="dry-run", help="Email step mode")
    parser.add_argument("--email-limit", type=int, default=5, help="Email batch size")
    parser.add_argument("--dashboard", action="store_true", help="Open the local AI fleet dashboard")
    parser.add_argument("--check-only", action="store_true", help="Only verify the local launcher setup")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return run_pipeline(args)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        return 130
    except Exception as exc:
        print(f"\nLauncher error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
