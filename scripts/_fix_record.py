from pathlib import Path
p = Path(r"D:\roseempire\scripts\record_demo_video.py")
t = p.read_text(encoding="utf-8")
t = t.replace(
    """        else:
            browser = await p.chromium.launch(headless=False, args=launch_kwargs.pop("args"))
            context = await browser.new_context(**launch_kwargs)""",
    """        else:
            browser_args = launch_kwargs.pop("args")
            context_kwargs = {k: v for k, v in launch_kwargs.items() if k != "headless"}
            browser = await p.chromium.launch(headless=False, args=browser_args)
            context = await browser.new_context(**context_kwargs)""",
)
p.write_text(t, encoding="utf-8")
print("fixed")
