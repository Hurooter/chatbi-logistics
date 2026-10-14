"""开发用：验证会话跨重启持久化。

第一步（服务运行时）：  uv run python scripts/try_persist.py setup
    —— 开会话、告诉助手"我叫张三，今年30岁"

然后重启服务（Ctrl+C 后重新 uvicorn）

第二步（重启后）：      uv run python scripts/try_persist.py check
    —— 用同一个会话问"我叫什么"，答对就说明历史没丢
"""
import json
import pathlib
import sys

import httpx

BASE = "http://127.0.0.1:8000"
STATE = pathlib.Path(__file__).with_name("_persist_state.json")
USERNAME = "persist_user"
PASSWORD = "pw123456"


def login() -> dict:
    r = httpx.post(f"{BASE}/auth/login", json={"username": USERNAME, "password": PASSWORD})
    return {"Authorization": f"Bearer {r.json()['token']}"}


if len(sys.argv) < 2 or sys.argv[1] == "setup":
    httpx.post(f"{BASE}/auth/register", json={"username": USERNAME, "password": PASSWORD})
    headers = login()
    thread_id = httpx.post(f"{BASE}/conversations", headers=headers).json()["thread_id"]
    r = httpx.post(
        f"{BASE}/chat",
        json={"question": "请记住：我叫张三，今年30岁。", "thread_id": thread_id},
        headers=headers,
        timeout=180,
    )
    print("setup 回答:", str(r.json().get("answer"))[:70])
    STATE.write_text(json.dumps({"thread_id": thread_id}), encoding="utf-8")
    print("会话号已存下。现在去重启服务，再跑 check。")
else:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    headers = login()
    r = httpx.post(
        f"{BASE}/chat",
        json={"question": "我叫什么？今年多大？", "thread_id": state["thread_id"]},
        headers=headers,
        timeout=180,
    )
    print("重启后回答:", r.json().get("answer"))
