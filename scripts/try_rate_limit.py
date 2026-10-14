"""试限流：连发 /chat，超过上限后应返回 429。

为避免真调大模型（太慢），这里给 agent 打个桩，让它秒回。
"""
import os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from langchain_core.messages import AIMessage
import chatbi.agent_graph as ag


class FakeModel:
    def invoke(self, messages):
        return AIMessage(content="（打桩回复）")


ag._agent_with_tools = FakeModel()      # 让 agent 节点秒回，不真调 API

from fastapi.testclient import TestClient
from chatbi.api import app

with TestClient(app) as client:
    u = f"rl_{random.randint(1000, 9999)}"
    client.post("/auth/register", json={"username": u, "password": "test123456"})
    token = client.post("/auth/login",
                        json={"username": u, "password": "test123456"}).json()["token"]
    h = {"Authorization": f"Bearer {token}"}
    tid = client.post("/conversations", headers=h).json()["thread_id"]

    for i in range(1, 13):
        r = client.post("/chat", headers=h, json={"question": "你好", "thread_id": tid})
        detail = r.json().get("detail", "")
        print("第 %2d 次 -> %s  %s" % (i, r.status_code, detail))
