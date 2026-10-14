# -*- coding: utf-8 -*-
"""压测：按并发梯度（1/2/4/8）跑同一批业务问题，横向看延迟、吞吐与 token 消耗。

说明：进程内直接调 agent 图（跳过 HTTP / 鉴权 / 限流），
      测的是「模型 + 工具 + 图」这条核心链路的耗时与成本。
"""
import os, sys, time, statistics
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
sys.path.insert(0, os.path.join(HERE, "..", "eval"))

from langgraph.checkpoint.memory import MemorySaver
from chatbi.agent_graph import build_agent_graph
from questions import QUESTIONS

LEVELS = [1, 2, 4, 8]     # 并发梯度
N = 16                    # 每个并发档的请求数

graph = build_agent_graph(MemorySaver())


def one(conc, i):
    q = QUESTIONS[i % len(QUESTIONS)]["q"]
    tid = "bench-%d-%03d" % (conc, i)          # 每档用独立 thread，互不累积上下文
    t0 = time.time()
    try:
        res = graph.invoke({"messages": [("user", q)]},
                           {"configurable": {"thread_id": tid}, "recursion_limit": 50})
        toks = sum((getattr(m, "usage_metadata", None) or {}).get("total_tokens", 0)
                   for m in res["messages"])
        ok = True
    except Exception:
        toks, ok = 0, False
    return time.time() - t0, toks, ok


def pct(sorted_vals, p):
    k = (len(sorted_vals) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - lo)


def main():
    total_tokens = 0
    print("%-6s %-10s %-9s %-9s %-9s %-8s %-9s %s" % (
        "并发", "总耗时", "平均", "P50", "P95", "QPS", "token/次", "失败"))
    for conc in LEVELS:
        t0 = time.time()
        with ThreadPoolExecutor(max_workers=conc) as ex:
            results = list(ex.map(lambda i: one(conc, i), range(N)))
        wall = time.time() - t0

        lats = sorted(d for d, _, ok in results if ok)
        toks = [t for _, t, ok in results if ok]
        fails = sum(1 for _, _, ok in results if not ok)
        total_tokens += sum(toks)

        print("%-6d %-10s %-9.2f %-9.2f %-9.2f %-8.2f %-9.0f %d" % (
            conc, "%.1fs" % wall, statistics.mean(lats) if lats else 0,
            pct(lats, .5) if lats else 0, pct(lats, .95) if lats else 0,
            N / wall, statistics.mean(toks) if toks else 0, fails))

    print("\n累积 token: %d" % total_tokens)


if __name__ == "__main__":
    main()
