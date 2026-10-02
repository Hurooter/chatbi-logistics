"""开发用：验证图里的自纠环——故意让第一次生成的 SQL 就是错的。

用法：PyCharm 里右键 Run，或 uv run python scripts/try_graph_loop.py
"""
import chatbi.graph as g

# 临时把"生成 SQL"这个函数换掉，让它一律返回一条必然报错的 SQL
# （inventory 表里没有 warehouse_name 字段）
g.generate_sql = lambda question: (
    "SELECT warehouse_name, SUM(stock_qty) FROM inventory GROUP BY warehouse_name"
)

state = g.graph.invoke({"question": "各仓库的库存总量分别是多少"})

print("最终 SQL：")
print(state["sql"])
print()
print("重写次数：", state["attempts"])
print("答：", state["answer"])
