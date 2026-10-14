"""开发用：验证删除会话 + 越权拦截。"""
import time

import httpx

BASE = "http://127.0.0.1:8000"


def register_and_login(name: str) -> dict:
    httpx.post(f"{BASE}/auth/register", json={"username": name, "password": "pw123456"})
    r = httpx.post(f"{BASE}/auth/login", json={"username": name, "password": "pw123456"})
    return {"Authorization": f"Bearer {r.json()['token']}"}


stamp = int(time.time())
alice = register_and_login(f"del_a_{stamp}")
bob = register_and_login(f"del_b_{stamp}")

a_thread = httpx.post(f"{BASE}/conversations", headers=alice).json()["thread_id"]
print("alice 的会话号:", a_thread)

httpx.post(f"{BASE}/chat", json={"question": "你好", "thread_id": a_thread},
           headers=alice, timeout=180)
print("（alice 先聊了一句，制造 checkpoint 数据）")

r = httpx.delete(f"{BASE}/conversations/{a_thread}", headers=bob)
print("① bob 删 alice 的会话:", r.status_code, r.json())

r = httpx.delete(f"{BASE}/conversations/{a_thread}", headers=alice)
print("② alice 删自己的会话:", r.status_code, r.json())

r = httpx.get(f"{BASE}/conversations", headers=alice)
print("③ alice 列表剩余:", len(r.json()))

r = httpx.post(f"{BASE}/chat", json={"question": "你好", "thread_id": a_thread},
               headers=alice, timeout=180)
print("④ 删完再聊:", r.status_code, r.json())
