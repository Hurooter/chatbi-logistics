"""开发用：跑一遍 LangGraph 版 ChatBI。

用法：PyCharm 里右键 Run，或 uv run python scripts/try_graph.py
"""
from chatbi.graph import graph

QUESTION = "各仓库的库存总量分别是多少"

state = graph.invoke({"question": QUESTION})

print("问：", QUESTION)
print("SQL：", state["sql"].replace("\n", " "))
print("答：", state["answer"])
print()
print("state 里最终的格子：", list(state.keys()))
