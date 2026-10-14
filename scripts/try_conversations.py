"""开发用：验证会话新建 / 列表 / 跨用户隔离。

先起服务：uv run uvicorn chatbi.api:app --reload
再跑本脚本：uv run python scripts/try_conversations.py
"""
import time

import httpx

BASE = "http://127.0.0.1:8000"


def register_and_login(name: str) -> dict:
    httpx.post(f"{BASE}/auth/register", json={"username": name, "password": "pw123456"})
    r = httpx.post(f"{BASE}/auth/login", json={"username": name, "password": "pw123456"})
    return {"Authorization": f"Bearer {r.json()['token']}"}


stamp = int(time.time())
alice = register_and_login(f"alice_{stamp}")
bob = register_and_login(f"bob_{stamp}")

for i in range(2):
    r = httpx.post(f"{BASE}/conversations", headers=alice)
    print(f"alice 新建会话 {i + 1}:", r.status_code, r.json())

r = httpx.post(f"{BASE}/conversations", headers=bob)
print("bob 新建会话:", r.status_code, r.json())

ra = httpx.get(f"{BASE}/conversations", headers=alice).json()
rb = httpx.get(f"{BASE}/conversations", headers=bob).json()
print("alice 看到的会话数:", len(ra))
print("bob 看到的会话数:", len(rb))

a_ids = {c["thread_id"] for c in ra}
b_ids = {c["thread_id"] for c in rb}
print("两边交集（应为空）:", a_ids & b_ids)
