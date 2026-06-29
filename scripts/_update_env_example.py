from pathlib import Path
p = Path(r"D:\roseempire\.env.example")
text = p.read_text(encoding="utf-8")
if "OLLAMA_TOOLS_MODEL" not in text:
    text = text.replace(
        "OLLAMA_MODEL=qwen2.5-coder:1.5b\n",
        "OLLAMA_MODEL=qwen2.5-coder:1.5b\nOLLAMA_TOOLS_MODEL=gemma4:31b-cloud\n",
        1,
    )
    p.write_text(text, encoding="utf-8")
    print("updated .env.example")
else:
    print("already set")
