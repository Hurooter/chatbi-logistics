"""试 GET /auth/me：带 token 能查到自己是谁；不带 / 带坏 token 被挡成 401。"""
import os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fastapi.testclient import TestClient
from chatbi.api import app

with TestClient(app) as client:
    u = f"me_{random.randint(1000, 9999)}"
    client.post("/auth/register", json={"username": u, "password": "test123456"})
    token = client.post("/auth/login",
                        json={"username": u, "password": "test123456"}).json()["token"]
    print("注册并登录的用户名:", u)

    ok = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    print("① 带 token   ->", ok.status_code, ok.json())

    no = client.get("/auth/me")
    print("② 不带 token ->", no.status_code, no.json())

    bad = client.get("/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    print("③ 坏 token   ->", bad.status_code, bad.json())
