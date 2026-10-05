"""开发用：试 Agent 版图。

用法：PyCharm 里右键 Run，或 uv run python scripts/try_agent.py
"""
from langchain_core.messages import HumanMessage

from chatbi.agent_graph import graph

config = {"configurable": {"thread_id": "agent-1"}}

QUESTIONS = [
    "库里都有哪些表？",
    "你好啊",
    "各仓库的库存总量分别是多少",
]

for q in QUESTIONS:
    r = graph.invoke({"messages": [HumanMessage(content=q)]}, config)
    print("=" * 70)
    print("问：", q)
    print("答：", r["messages"][-1].content)
