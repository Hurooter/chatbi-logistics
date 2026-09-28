"""开发用：完整问几个问题，看 ChatBI 端到端表现。

用法：PyCharm 里右键 Run，或 uv run python scripts/try_ask.py
"""
from chatbi.ask import ask

QUESTIONS = [
    "各仓库的库存总量分别是多少",
    "哪个承运商的平均履约时间最长",
    "有多少个仓库的商品库存低于安全库存",
]

for q in QUESTIONS:
    r = ask(q)
    print("=" * 70)
    print("问：", q)
    print("SQL：", r["sql"].replace("\n", " "))
    print("答：", r["answer"])
    print("（SQL 重写次数：%d）" % r["attempts"])
