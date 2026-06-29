import asyncio
import litellm
litellm.drop_params = True

async def main():
    try:
        r = await litellm.acompletion(
            model="ollama/gemma4:31b-cloud",
            api_base="http://127.0.0.1:11434",
            messages=[{"role": "user", "content": "Use update_todo_list to add todo Test"}],
            tools=[{"type": "function", "function": {"name": "update_todo_list", "description": "Update todos", "parameters": {"type": "object", "properties": {"todos": {"type": "string"}}, "required": ["todos"]}}}],
            tool_choice="required",
        )
        msg = r.choices[0].message
        print("tool_calls", getattr(msg, "tool_calls", None))
        print("content", (msg.content or "")[:200])
    except Exception as e:
        print("FAIL", e)

asyncio.run(main())
