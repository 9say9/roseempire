from pathlib import Path
p = Path("d:/roseempire/email_agent.py")
text = p.read_text(encoding="utf-8")
start = text.find("    if not result and interactive:")
end = text.find("    _save_msal_cache(cache)", start)
new_block = """    if not result and interactive:
        print("Microsoft 365 device login — open the URL below in your browser.")
        print("Sign in as info@roseempire.co.uk if asked, then click Accept.\n")
        flow = app.initiate_device_flow(scopes=GRAPH_SCOPES)
        if "message" not in flow:
            raise RuntimeError(f"Device flow failed: {flow}")
        print(flow["message"])
        print("\nWaiting for approval in browser...\n")
        result = app.acquire_token_by_device_flow(flow)

"""
text = text[:start] + new_block + text[end:]
p.write_text(text, encoding="utf-8")
import py_compile
py_compile.compile(str(p))
print("ok")
