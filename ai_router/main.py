"""Rose Empire AI Router — OpenAI-compatible gateway with failover routing and no local Ollama fallback."""
from __future__ import annotations

import asyncio
import copy
import json
import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from litellm import Router
import litellm

litellm.drop_params = True

# Load ai_router/.env then repo root .env (fleet keys)
_ROOT = Path(__file__).resolve().parent
load_dotenv(_ROOT / ".env")
load_dotenv(_ROOT.parent / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("AI-Router")

ROUTER_MODEL = os.getenv("AI_ROUTER_MODEL", "boss-model")
MODEL_ALIASES = {
    "gemini-free": ROUTER_MODEL,
    "gemini": ROUTER_MODEL,
    "gpt-3.5-turbo": ROUTER_MODEL,
    "gpt-4": ROUTER_MODEL,
    "gpt-4o": ROUTER_MODEL,
    "gpt-4o-mini": ROUTER_MODEL,
    "gpt-4.1": ROUTER_MODEL,
    "gpt-4.1-mini": ROUTER_MODEL,
    "claude": ROUTER_MODEL,
    "claude-3-haiku": ROUTER_MODEL,
    "deepseek": ROUTER_MODEL,
    "llama": ROUTER_MODEL,
    "mistral": ROUTER_MODEL,
    "qwen": ROUTER_MODEL,
    "ollama": ROUTER_MODEL,
}
PUBLIC_MODEL_IDS = list(dict.fromkeys([*MODEL_ALIASES.keys(), ROUTER_MODEL]))
COOLDOWN_SECONDS = int(os.getenv("AI_ROUTER_COOLDOWN", "30"))
REQUEST_TIMEOUT = int(os.getenv("AI_ROUTER_REQUEST_TIMEOUT", "15"))


def _key(*names: str) -> str:
    for name in names:
        value = (os.getenv(name) or "").strip()
        if value and not value.startswith("your_"):
            return value
    return ""


def _build_model_list() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []

    def add_entry(litellm_model: str, api_key: str | None, entry_id: str, extra_params: dict[str, Any] | None = None) -> None:
        if not api_key:
            return
        params = {"model": litellm_model, "api_key": api_key}
        if extra_params:
            params.update(extra_params)
        entries.append({
            "model_name": ROUTER_MODEL,
            "litellm_params": params,
            "model_info": {"id": entry_id, "tier": "paid", "supports_tools": True},
        })

    add_entry("gemini/gemini-2.5-flash", _key("GEMINI_API_KEY", "GEMINI_API_KEY_1", "GEMINI_API_KEY_2"), "gemini")
    add_entry("openai/gpt-4o", _key("OPENAI_API_KEY"), "openai", extra_params={"api_base": os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")})
    add_entry("deepseek/deepseek-chat", _key("DEEPSEEK_API_KEY"), "deepseek")

    return entries


MODEL_LIST = _build_model_list()
CLOUD_DEPLOYMENTS = len(MODEL_LIST)

_ROUTER_KWARGS = dict(
    routing_strategy=os.getenv("LITELLM_ROUTING_STRATEGY", "simple-shuffle"),
    num_retries=3,
    allowed_fails=2,
    cooldown_time=COOLDOWN_SECONDS,
    set_verbose=False,
)

router = Router(model_list=MODEL_LIST, **_ROUTER_KWARGS)

app = FastAPI(title="Rose Empire Dynamic AI Router", version="1.1.0")


def _response_to_dict(response: Any) -> dict[str, Any]:
    if hasattr(response, "model_dump"):
        return response.model_dump()
    if hasattr(response, "dict"):
        return response.dict()
    if isinstance(response, dict):
        return response
    raise TypeError(f"Unexpected LiteLLM response type: {type(response)}")


@app.on_event("startup")
async def startup_log() -> None:
    logger.info("Rose Empire AI Router starting")
    logger.info("Router model alias: %s", ROUTER_MODEL)
    logger.info("Deployments: %d cloud providers", len(MODEL_LIST))
    logger.info("Cooldown on 429/errors: %ss", COOLDOWN_SECONDS)
    for item in MODEL_LIST:
        info = item.get("model_info", {})
        params = item["litellm_params"]
        logger.info("  - [%s] %s", info.get("id", "?"), params.get("model"))


@app.get("/health")
async def health_check() -> dict[str, Any]:
    return {
        "status": "healthy",
        "router_model": ROUTER_MODEL,
        "model_aliases": PUBLIC_MODEL_IDS,
        "deployments": len(MODEL_LIST),
        "cloud_keys": CLOUD_DEPLOYMENTS,
        "cooldown_seconds": COOLDOWN_SECONDS,
        "request_timeout_seconds": REQUEST_TIMEOUT,
        "tools_passthrough": True,
    }


def _pick_router(body: dict[str, Any]) -> Router:
    return router


def _completion_kwargs(body: dict[str, Any]) -> dict[str, Any]:
    """Forward full OpenAI payload; strip empty tool lists Roo sometimes sends."""
    payload = copy.deepcopy(body)
    payload["model"] = _resolve_model(payload.get("model"))
    if payload.get("tools") == []:
        payload.pop("tools", None)
        payload.pop("tool_choice", None)
        payload.pop("parallel_tool_calls", None)
    return payload


def _resolve_model(requested: str | None) -> str:
    name = (requested or ROUTER_MODEL).strip()
    return MODEL_ALIASES.get(name, name if name in {m["model_name"] for m in MODEL_LIST} else ROUTER_MODEL)


@app.get("/v1/models")
async def list_models() -> dict[str, Any]:
    return {
        "object": "list",
        "data": [
            {"id": mid, "object": "model", "owned_by": "rose-empire"}
            for mid in PUBLIC_MODEL_IDS
        ],
    }


def _chunk_to_sse(chunk: Any) -> str | None:
    if hasattr(chunk, "model_dump"):
        payload = chunk.model_dump()
    elif hasattr(chunk, "dict"):
        payload = chunk.dict()
    elif isinstance(chunk, dict):
        payload = chunk
    else:
        return None
    return f"data: {json.dumps(payload)}\n\n"


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    kwargs = _completion_kwargs(body)
    active_router = _pick_router(body)
    stream = bool(kwargs.get("stream"))
    tool_count = len(body.get("tools") or [])
    msg_count = len(body.get("messages") or [])

    try:
        if stream:
            async def event_stream():
                response = await asyncio.wait_for(
                    active_router.acompletion(**kwargs),
                    timeout=REQUEST_TIMEOUT,
                )
                async for chunk in response:
                    line = _chunk_to_sse(chunk)
                    if line:
                        yield line
                yield "data: [DONE]\n\n"

            logger.info(
                "Stream | pool=%s | tools=%d | messages=%d",
                kwargs["model"],
                tool_count,
                msg_count,
            )
            return StreamingResponse(event_stream(), media_type="text/event-stream")

        response = await asyncio.wait_for(
            active_router.acompletion(**kwargs),
            timeout=REQUEST_TIMEOUT,
        )
        payload = _response_to_dict(response)
        choice = (payload.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        tool_calls = message.get("tool_calls") or []
        logger.info(
            "Routed OK | pool=%s | used=%s | tools=%d | tool_calls=%d",
            kwargs["model"],
            payload.get("model", "unknown"),
            tool_count,
            len(tool_calls),
        )
        return payload
    except Exception as exc:
        logger.error("Router failure (tools=%d): %s", tool_count, exc)
        raise HTTPException(status_code=502, detail=f"AI Router failure: {exc}") from exc


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("AI_ROUTER_HOST", "0.0.0.0")
    port = int(os.getenv("AI_ROUTER_PORT", "8000"))
    uvicorn.run(app, host=host, port=port, reload=False)
