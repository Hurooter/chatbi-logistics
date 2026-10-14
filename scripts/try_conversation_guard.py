"""开发用：验证会话归属校验（越权拦截）。"""
import time

import httpx

BASE = "http://127.0.0.1:8000"


def register_and_login(name: str) -> dict:
    httpx.post(f"{BASE}/auth/register", json={"username": name, "password": "pw123456"})
    r = httpx.post(f"{BASE}/auth/login", json={"username": name, "password": "pw123456"})
    return {"Authorization": f"Bearer {r.json()['token']}"}


stamp = int(time.time())
alice = register_and_login(f"a_{stamp}")
bob = register_and_login(f"b_{stamp}")

a_thread = httpx.post(f"{BASE}/conversations", headers=alice).json()["thread_id"]
b_thread = httpx.post(f"{BASE}/conversations", headers=bob).json()["thread_id"]
print("alice 的会话:", a_thread)
print("bob 的会话:  ", b_thread)

r = httpx.post(f"{BASE}/chat", json={"question": "你好", "thread_id": a_thread},
               headers=alice, timeout=180)
print("① alice 用自己会话:", r.status_code)

r = httpx.post(f"{BASE}/chat", json={"question": "你好", "thread_id": a_thread},
               headers=bob, timeout=180)
print("② bob 盗用 alice 会话:", r.status_code, r.json())

r = httpx.post(f"{BASE}/chat", json={"question": "你好", "thread_id": b_thread},
               headers=bob, timeout=180)
print("③ bob 用自己会话:", r.status_code)

r = httpx.post(f"{BASE}/chat", json={"question": "你好", "thread_id": "编造的号"},
               headers=bob, timeout=180)
print("④ 编造的会话号:", r.status_code, r.json())
