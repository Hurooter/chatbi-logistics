"""开发用：验证改密码接口。

先起服务：uv run uvicorn chatbi.api:app --reload
再跑本脚本：uv run python scripts/try_change_pw.py
"""
import time

import httpx

BASE = "http://127.0.0.1:8000"
username = f"pwtest_{int(time.time())}"

httpx.post(f"{BASE}/auth/register", json={"username": username, "password": "old123456"})
token = httpx.post(
    f"{BASE}/auth/login", json={"username": username, "password": "old123456"}
).json()["token"]
headers = {"Authorization": f"Bearer {token}"}

r = httpx.post(
    f"{BASE}/auth/password",
    json={"old_password": "wrong", "new_password": "new123456"},
    headers=headers,
)
print("① 原密码错:", r.status_code, r.json())

r = httpx.post(
    f"{BASE}/auth/password",
    json={"old_password": "old123456", "new_password": "new123456"},
    headers=headers,
)
print("② 改密码:", r.status_code, r.json())

r = httpx.post(f"{BASE}/auth/login", json={"username": username, "password": "old123456"})
print("③ 用旧密码登录:", r.status_code)

r = httpx.post(f"{BASE}/auth/login", json={"username": username, "password": "new123456"})
print("④ 用新密码登录:", r.status_code)

r = httpx.post(
    f"{BASE}/auth/password",
    json={"old_password": "new123456", "new_password": "x"},
)
print("⑤ 不带 token 改密码:", r.status_code)
