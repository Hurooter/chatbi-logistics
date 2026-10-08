import time

from chatbi.tools.sql_runner import run_sql

t = time.time()
slow = run_sql("SELECT SLEEP(30)")
print(f"[慢查询] 耗时 {time.time() - t:.1f} 秒 | ok = {slow['ok']}")
print("         error =", slow.get("error"))

fast = run_sql("SELECT COUNT(*) FROM warehouses")
print("[正常查询] ok =", fast["ok"], "| rows =", fast["rows"])