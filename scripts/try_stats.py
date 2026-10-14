"""试 GET /stats/warehouses：带 token 拿到各仓库存总量 + 预警数；不带 token 被挡 401。"""
import os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fastapi.testclient import TestClient
from chatbi.api import app

with TestClient(app) as client:
    u = f"stats_{random.randint(1000, 9999)}"
    client.post("/auth/register", json={"username": u, "password": "test123456"})
    token = client.post("/auth/login",
                        json={"username": u, "password": "test123456"}).json()["token"]

    r = client.get("/stats/warehouses", headers={"Authorization": f"Bearer {token}"})
    print("① 带 token -> 状态码", r.status_code)
    rows = r.json()
    print("   返回", len(rows), "条：")
    for x in rows:
        print("     ", x)

    no = client.get("/stats/warehouses")
    print("② 不带 token ->", no.status_code, no.json())

    t = client.get("/stats/trend", headers={"Authorization": f"Bearer {token}"})
    print("③ 趋势接口 -> 状态码", t.status_code, "共", len(t.json()), "个月：")
    for x in t.json():
        print("     ", x)
