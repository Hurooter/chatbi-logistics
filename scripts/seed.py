"""容器首次启动时的灌数入口：库里已有数据就跳过，空库才造。

用法（容器内）：python scripts/seed.py
"""
import os
import runpy

import pymysql


def warehouse_count() -> int:
    conn = pymysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "chatbi_logistics"),
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM warehouses")
            return cur.fetchone()[0]
    finally:
        conn.close()


if __name__ == "__main__":
    n = warehouse_count()
    if n:
        print(f"库里已有 {n} 个仓库，跳过造数")
    else:
        print("空库，开始造数…")
        runpy.run_path("scripts/gen_data.py", run_name="__main__")
