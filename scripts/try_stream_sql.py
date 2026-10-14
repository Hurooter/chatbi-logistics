"""试 /chat/stream：回答流完后应多出一个 sqls 事件（本轮实际执行的 SQL）。"""
import os, sys, json, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fastapi.testclient import TestClient
from chatbi.api import app

with TestClient(app) as client:
    u = f"sql_{random.randint(1000, 9999)}"
    client.post("/auth/register", json={"username": u, "password": "test123456"})
    token = client.post("/auth/login",
                        json={"username": u, "password": "test123456"}).json()["token"]
    h = {"Authorization": f"Bearer {token}"}
    tid = client.post("/conversations", headers=h).json()["thread_id"]

    tokens, statuses, sqls = 0, [], None
    with client.stream("POST", "/chat/stream", headers=h,
                       json={"question": "各仓库的库存总量分别是多少？", "thread_id": tid}) as r:
        for line in r.iter_lines():
            if not line.startswith("data: "):
                continue
            d = json.loads(line[6:])
            if "token" in d:
                tokens += 1
            elif "status" in d:
                statuses.append(d["status"])
            elif "sqls" in d:
                sqls = d["sqls"]

    print("token 事件数:", tokens)
    print("status 事件:", statuses)
    print("sqls 事件:")
    for s in (sqls or []):
        print("   ", s.replace("\n", " "))
    print("判定:", "通过" if sqls else "没收到 sqls，失败")
