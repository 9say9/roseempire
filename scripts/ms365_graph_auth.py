"""One-time Microsoft 365 login for sending mail via Graph API (no SMTP required)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from email_agent import TOKEN_CACHE, get_graph_access_token


def main() -> int:
    print("\n=== Rose Empire — Microsoft 365 Graph login ===\n")
    print("A browser window will open. Sign in as info@roseempire.co.uk if asked.")
    print("If you are already signed in, just pick that account and click Accept.")
    print("This bypasses SMTP (which is disabled on your tenant).\n")

    token = get_graph_access_token(interactive=True)
    if not token:
        print("\nLogin failed. Try again or register your own Azure app (see .env.example).")
        return 1

    print(f"\nSuccess. Token cache saved: {TOKEN_CACHE}")
    print("You can now run: py -3 manchester_sales_pipeline.py --limit 5 --send\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
