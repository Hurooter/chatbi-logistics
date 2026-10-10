"""开发用：走一遍 注册 → 登录 → 门禁 的完整流程。

先起服务：uv run uvicorn chatbi.api:app --reload
再跑本脚本：uv run python scripts/try_auth_flow.py
"""
import time

import httpx

BASE = "http://127.0.0.1:8000"
username = f"test_{int(time.time())}"
password = "pw123456"

r = httpx.post(f"{BASE}/auth/register", json={"username": username, "password": password})
print("① 注册:", r.status_code, r.json())

r = httpx.post(f"{BASE}/auth/register", json={"username": username, "password": password})
print("② 重复注册:", r.status_code, r.json())

r = httpx.post(f"{BASE}/auth/login", json={"username": username, "password": password})
print("③ 登录:", r.status_code)
token = r.json()["token"]
print("   token:", token[:40], "...")

r = httpx.post(f"{BASE}/auth/login", json={"username": username, "password": "wrong-pw"})
print("④ 密码错登录:", r.status_code, r.json())

r = httpx.post(f"{BASE}/chat", json={"question": "你好"})
print("⑤ 不带 token 调 /chat:", r.status_code, r.json())

r = httpx.post(
    f"{BASE}/chat",
    json={"question": "你好"},
    headers={"Authorization": f"Bearer {token}"},
    timeout=120,
)
print("⑥ 带 token 调 /chat:", r.status_code)
print("   回答:", str(r.json().get("answer"))[:80])
