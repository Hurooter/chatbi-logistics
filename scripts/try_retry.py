"""开发用：验证「SQL 出错 -> 自动重写」这条链路。

用法：PyCharm 里右键 Run，或 uv run python scripts/try_retry.py
"""
from chatbi.nodes.sql_fixer import fix_sql
from chatbi.tools.sql_runner import run_sql

QUESTION = "各仓库的库存总量分别是多少"

print("=== 1. 先造一个必然报错的 SQL ===")
print("inventory 表里没有 warehouse_name 字段，所以它一定失败")
bad_sql = "SELECT warehouse_name, SUM(stock_qty) FROM inventory GROUP BY warehouse_name"
first = run_sql(bad_sql)
print(first)

print("\n=== 2. 把报错交给模型，让它重写 ===")
fixed_sql = fix_sql(QUESTION, bad_sql, first["error"])
print(fixed_sql)

print("\n=== 3. 重写后的 SQL 能跑通吗 ===")
print(run_sql(fixed_sql))
