"""One-off patch: add request timeouts to ai_router/main.py."""
from pathlib import Path

p = Path(r"D:\roseempire\ai_router\main.py")
text = p.read_text(encoding="utf-8")

if "import asyncio" not in text:
    text = text.replace("import copy", "import asyncio\nimport copy", 1)

if "REQUEST_TIMEOUT" not in text:
    text = text.replace(
        'COOLDOWN_SECONDS = int(os.getenv("AI_ROUTER_COOLDOWN", "60"))',
        'COOLDOWN_SECONDS = int(os.getenv("AI_ROUTER_COOLDOWN", "60"))\nREQUEST_TIMEOUT = int(os.getenv("AI_ROUTER_REQUEST_TIMEOUT", "90"))',
        1,
    )

if "request_timeout_seconds" not in text:
    text = text.replace(
        '"cooldown_seconds": COOLDOWN_SECONDS,',
        '"cooldown_seconds": COOLDOWN_SECONDS,\n        "request_timeout_seconds": REQUEST_TIMEOUT,',
        1,
    )

stream_old = "                response = await active_router.acompletion(**kwargs)"
stream_new = """                response = await asyncio.wait_for(
                    active_router.acompletion(**kwargs),
                    timeout=REQUEST_TIMEOUT,
                )"""
if stream_old in text and "asyncio.wait_for" not in text:
    text = text.replace(stream_old, stream_new, 1)

sync_old = "        response = await active_router.acompletion(**kwargs)"
sync_new = """        response = await asyncio.wait_for(
            active_router.acompletion(**kwargs),
            timeout=REQUEST_TIMEOUT,
        )"""
if sync_old in text:
    text = text.replace(sync_old, sync_new, 1)

p.write_text(text, encoding="utf-8")
print("patched", p)
