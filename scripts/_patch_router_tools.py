from pathlib import Path

p = Path(r"D:\roseempire\ai_router\main.py")
text = p.read_text(encoding="utf-8")

# Add OLLAMA_TOOLS_MODEL after OLLAMA_MODEL line
if "OLLAMA_TOOLS_MODEL" not in text:
    text = text.replace(
        'OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:1.5b")\n',
        'OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:1.5b")\n'
        'OLLAMA_TOOLS_MODEL = os.getenv("OLLAMA_TOOLS_MODEL", "gemma4:31b-cloud")\n',
        1,
    )

# Add tool-capable Ollama deployment before local ollama entry
needle = '''    # Always include local Ollama as final deployment in the pool
    entries.append(
        {
            "model_name": ROUTER_MODEL,
            "litellm_params": {
                "model": f"ollama/{OLLAMA_MODEL}",
                "api_base": OLLAMA_BASE,
            },
            "model_info": {"id": "ollama-local", "tier": "free"},
        }
    )'''

replacement = '''    if OLLAMA_TOOLS_MODEL:
        entries.append(
            {
                "model_name": ROUTER_MODEL,
                "litellm_params": {
                    "model": f"ollama/{OLLAMA_TOOLS_MODEL}",
                    "api_base": OLLAMA_BASE,
                },
                "model_info": {"id": "ollama-tools", "tier": "tools"},
            }
        )

    # Always include local Ollama as final deployment in the pool
    entries.append(
        {
            "model_name": ROUTER_MODEL,
            "litellm_params": {
                "model": f"ollama/{OLLAMA_MODEL}",
                "api_base": OLLAMA_BASE,
            },
            "model_info": {"id": "ollama-local", "tier": "free"},
        }
    )'''

if "ollama-tools" not in text:
    text = text.replace(needle, replacement, 1)

# Build TOOLS_MODEL_LIST and router_tools
if "TOOLS_MODEL_LIST" not in text:
    text = text.replace(
        "CLOUD_MODEL_LIST = [m for m in MODEL_LIST if m.get(\"model_info\", {}).get(\"tier\") == \"paid\"]\n"
        "CLOUD_DEPLOYMENTS = len(CLOUD_MODEL_LIST)\n",
        "CLOUD_MODEL_LIST = [m for m in MODEL_LIST if m.get(\"model_info\", {}).get(\"tier\") == \"paid\"]\n"
        "TOOLS_MODEL_LIST = CLOUD_MODEL_LIST + [m for m in MODEL_LIST if m.get(\"model_info\", {}).get(\"tier\") == \"tools\"]\n"
        "CLOUD_DEPLOYMENTS = len(CLOUD_MODEL_LIST)\n",
        1,
    )

if "router_tools" not in text:
    text = text.replace(
        "router_cloud = (\n"
        "    Router(\n"
        "        model_list=CLOUD_MODEL_LIST,\n"
        "        **{**_ROUTER_KWARGS, \"num_retries\": max(2, len(CLOUD_MODEL_LIST))},\n"
        "    )\n"
        "    if CLOUD_MODEL_LIST\n"
        "    else router\n"
        ")\n",
        "router_cloud = (\n"
        "    Router(\n"
        "        model_list=CLOUD_MODEL_LIST,\n"
        "        **{**_ROUTER_KWARGS, \"num_retries\": max(2, len(CLOUD_MODEL_LIST))},\n"
        "    )\n"
        "    if CLOUD_MODEL_LIST\n"
        "    else router\n"
        ")\n"
        "router_tools = (\n"
        "    Router(\n"
        "        model_list=TOOLS_MODEL_LIST,\n"
        "        **{**_ROUTER_KWARGS, \"num_retries\": max(2, len(TOOLS_MODEL_LIST))},\n"
        "    )\n"
        "    if TOOLS_MODEL_LIST\n"
        "    else router\n"
        ")\n",
        1,
    )

# Update _pick_router
old_pick = '''def _pick_router(body: dict[str, Any]) -> Router:
    """Roo Code requires native tool_calls — route tool requests to cloud only."""
    if body.get("tools") and SKIP_OLLAMA_FOR_TOOLS and CLOUD_MODEL_LIST:
        return router_cloud
    return router'''

new_pick = '''def _pick_router(body: dict[str, Any]) -> Router:
    """Roo Code requires native tool_calls — prefer cloud, then Ollama tools model."""
    if body.get("tools") and SKIP_OLLAMA_FOR_TOOLS:
        if TOOLS_MODEL_LIST:
            return router_tools
        if CLOUD_MODEL_LIST:
            return router_cloud
    return router'''

if "router_tools" in text and old_pick in text:
    text = text.replace(old_pick, new_pick, 1)

# Health + startup metadata
if "ollama_tools_fallback" not in text:
    text = text.replace(
        '"ollama_fallback": f"ollama/{OLLAMA_MODEL}",\n',
        '"ollama_fallback": f"ollama/{OLLAMA_MODEL}",\n'
        '        "ollama_tools_fallback": f"ollama/{OLLAMA_TOOLS_MODEL}",\n',
        1,
    )

if "Ollama tools fallback" not in text:
    text = text.replace(
        'logger.info("Ollama fallback: %s @ %s", OLLAMA_MODEL, OLLAMA_BASE)\n',
        'logger.info("Ollama fallback: %s @ %s", OLLAMA_MODEL, OLLAMA_BASE)\n'
        '    logger.info("Ollama tools fallback: %s @ %s", OLLAMA_TOOLS_MODEL, OLLAMA_BASE)\n',
        1,
    )

# Fix logging cloud_only to tools_pool
text = text.replace("active_router is router_cloud", "active_router is router_tools")

p.write_text(text, encoding="utf-8")
print("patched tools fallback")
