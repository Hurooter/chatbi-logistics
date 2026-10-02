"""开发用：验证多轮对话——追问里的"那它"能不能被理解。

用法：PyCharm 里右键 Run，或 uv run python scripts/try_multi_turn.py
"""
from langchain_core.messages import HumanMessage

from chatbi.graph import graph

config = {"configurable": {"thread_id": "test-1"}}

r1 = graph.invoke({"messages": [HumanMessage(content="各仓库的库存总量分别是多少")]}, config)
print("第一轮问：各仓库的库存总量分别是多少")
print("第一轮答：", r1["answer"])
print()

r2 = graph.invoke({"messages": [HumanMessage(content="那华东仓的库存占八仓总量的百分之多少？")]}, config)
print("第二轮问：那华东仓的库存占八仓总量的百分之多少？")
print("第二轮 SQL：", r2["sql"].replace("\n", " "))
print("第二轮答：", r2["answer"])
