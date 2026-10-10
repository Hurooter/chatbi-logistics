"""开发用：测流式接口，看它一个个吐字。

先起服务：uv run uvicorn chatbi.api:app --reload
再跑本脚本：uv run python scripts/try_stream.py
"""
import json

import httpx

URL = "http://127.0.0.1:8000/chat/stream"

with httpx.stream("POST", URL, json={"question": "你好"}, timeout=60) as r:
    for line in r.iter_lines():
        if line.startswith("data: "):
            token = json.loads(line[6:])["token"]
            print(token, end="", flush=True)
print()
