# -*- coding: utf-8 -*-
"""20 题评估集：让 Agent 逐题作答，用三个口径判分。

口径①「严格」：Agent 跑过的任意一条 SQL 的结果集，与标准 SQL 结果集完全一致
             （忽略行序）。
口径②「宽松」：在①基础上，允许 Agent 多带列（对模型结果做列投影再比）。
口径③「结论正确」：标准答案里的关键值是否出现在 Agent 的最终回答里
             （数字带容差并解析「万 / 亿」，文本做包含判断）。

为什么要三档：这是个多轮 Agent，它常先探量再查询、还常多返回几列/几行。
只看①会严重低估；③才最贴近「用户有没有拿到对的结论」。
"""
import os, sys, itertools, re
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
sys.path.insert(0, HERE)

from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage
from chatbi.db import query
from chatbi.agent_graph import build_agent_graph
from questions import QUESTIONS


def norm(v):
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, Decimal):
        return round(float(v), 4)
    if isinstance(v, (int, float)):
        return round(float(v), 4)
    return str(v)


def canon(rows):
    return sorted((tuple(norm(v) for v in r) for r in rows), key=repr)


def project_match(model_rows, gold_rows):
    """gold 的行能否由 model 的某几列投影出来（允许 model 多带列）。"""
    if not gold_rows:
        return not model_rows
    if not model_rows:
        return False
    k, m = len(model_rows[0]), len(gold_rows[0])
    if m > k:
        return False
    gold = canon(gold_rows)
    for cols in itertools.combinations(range(k), m):
        proj = [tuple(r[c] for c in cols) for r in model_rows]
        if canon(proj) == gold:
            return True
    return False


def model_sqls(state):
    out = []
    for msg in state.values.get("messages", []):
        if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
            for tc in msg.tool_calls:
                if tc.get("name") == "sql_tool":
                    out.append((tc.get("args") or {}).get("sql"))
    return out


def answer_numbers(text):
    """从回答里抽出所有数字，并解析「万 / 亿」单位。"""
    out = []
    for m in re.finditer(r"(\d[\d,]*(?:\.\d+)?)\s*(亿|万)?", text):
        try:
            v = float(m.group(1).replace(",", ""))
        except ValueError:
            continue
        if m.group(2) == "亿":
            v *= 1e8
        elif m.group(2) == "万":
            v *= 1e4
        out.append(v)
    return out


def close(a, b):
    return abs(a - b) <= max(0.02, 0.005 * abs(b))   # 相对容差 0.5%


def conclusion_ok(gold_rows, ans):
    """标准答案里的每个值都要在最终回答里找到（数字带容差）。"""
    nums = answer_numbers(ans)
    for row in gold_rows:
        for v in row:
            if isinstance(v, bool):
                v = int(v)
            if isinstance(v, (Decimal, int, float)):
                gv = float(v)
                if not any(close(n, gv) for n in nums):
                    return False
            else:
                if str(v) not in ans:
                    return False
    return True


def main():
    graph = build_agent_graph(MemorySaver())
    n = len(QUESTIONS)
    strict = tolerant = concl = 0
    bad = []

    for i, item in enumerate(QUESTIONS, 1):
        tid = "eval-%02d" % i
        res = graph.invoke({"messages": [("user", item["q"])]},
                           {"configurable": {"thread_id": tid}, "recursion_limit": 50})
        state = graph.get_state({"configurable": {"thread_id": tid}})
        gold_rows = query(item["gold"])[1]
        gold = canon(gold_rows)

        results = []
        for s in model_sqls(state):
            try:
                results.append(query(s)[1])
            except Exception:
                results.append(None)

        st_ok = any(r is not None and canon(r) == gold for r in results)
        tol_ok = any(r is not None and project_match(r, gold_rows) for r in results)

        ans = res["messages"][-1].content or ""
        c_ok = conclusion_ok(gold_rows, ans)

        strict += st_ok
        tolerant += tol_ok
        concl += c_ok
        print("%2d  严格%s  宽松%s  结论%s   %s" % (
            i, "OK" if st_ok else "--", "OK" if tol_ok else "--", "OK" if c_ok else "--", item["q"]))
        if not c_ok:
            bad.append((i, item["q"], item["gold"], model_sqls(state), ans))

    print("\n===== 严格 %d/%d ｜ 宽松 %d/%d ｜ 结论正确 %d/%d ======" % (
        strict, n, tolerant, n, concl, n))

    for i, q, g, sqls, ans in bad:
        print("\n--- 第 %d 题结论未过: %s" % (i, q))
        print("  标准 SQL:", g)
        for j, s in enumerate(sqls, 1):
            print("  模型SQL%d:" % j, (s or "").replace("\n", " "))
        print("  最终答案:", ans[:300].replace("\n", " "))


if __name__ == "__main__":
    main()
