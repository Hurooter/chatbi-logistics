"""生成 ChatBI 物流仓储业务的模拟数据，灌入 MySQL。

用法：uv run python scripts/gen_data.py
"""
import os
import random
from datetime import datetime, timedelta

import pymysql
from dotenv import load_dotenv

load_dotenv()

# ---------- 造数规模（想改数据量就改这里）----------
N_SKUS = 200
N_INBOUND = 6000
N_OUTBOUND = 30000
DAYS_BACK = 180

random.seed(42)   # 固定随机种子：每次跑出来的数据完全一样，方便复现问题

NOW = datetime.now()

# ---------- 业务素材 ----------
CITIES = ["上海", "北京", "广州", "成都", "武汉", "沈阳", "西安", "杭州"]
WAREHOUSE_NAMES = ["华东仓", "华北仓", "华南仓", "西南仓", "华中仓", "东北仓", "西北仓", "华东二仓"]
MANAGERS = ["张伟", "李娜", "王强", "刘洋", "陈静", "赵磊", "孙丽", "周涛"]

CATEGORIES = ["家用电器", "数码配件", "服饰鞋包", "食品饮料", "家居家装", "母婴用品", "运动户外", "美妆个护"]
ADJ = ["轻便", "智能", "经典", "旗舰", "便携", "加厚", "儿童", "专业"]
NOUN = ["保温杯", "蓝牙耳机", "双肩包", "运动鞋", "折叠椅", "电饭煲", "洗发水", "充电宝", "台灯", "瑜伽垫"]

SUPPLIERS = ["南方供应链有限公司", "通达贸易有限公司", "恒信实业有限公司",
             "广源物资有限公司", "中兴供应链有限公司"]
CUSTOMERS = ["京东自营", "天猫超市", "拼多多优选", "永辉超市",
             "大润发", "苏宁易购", "盒马鲜生", "物美集团"]

# 承运商 -> 运输时长 (下限, 上限) 天。故意拉开差距，好让"哪家最慢"有明确答案
CARRIERS = {
    "顺丰速运": (1, 2),
    "京东物流": (1, 2),
    "中通快递": (2, 4),
    "圆通速递": (2, 5),
    "韵达快递": (2, 5),
    "德邦物流": (3, 6),
}


def random_time():
    """随机一个过去 2~DAYS_BACK 天内的业务时间；工作日出现概率高于周末。"""
    while True:
        day = NOW - timedelta(days=random.randint(2, DAYS_BACK))
        if day.weekday() < 5 or random.random() < 0.3:
            break
    return day.replace(hour=random.randint(8, 20), minute=random.randint(0, 59),
                       second=random.randint(0, 59), microsecond=0)


def build_warehouses():
    return [
        (i + 1, WAREHOUSE_NAMES[i], CITIES[i], random.randint(8000, 30000), MANAGERS[i])
        for i in range(len(WAREHOUSE_NAMES))
    ]


def build_products():
    rows = []
    for i in range(1, N_SKUS + 1):
        rows.append((
            f"SKU{i:04d}",
            random.choice(ADJ) + random.choice(NOUN),
            random.choice(CATEGORIES),
            round(random.uniform(9, 2000), 2),
            round(random.uniform(0.1, 60), 2),
            round(random.uniform(0.05, 30), 2),
        ))
    return rows


def build_inventory(warehouses, products):
    rows = []
    for wh in warehouses:
        for p in products:
            safety = random.randint(50, 400)
            # 约 15% 的"仓 x SKU"组合库存压到安全线以下，制造缺货问题
            if random.random() < 0.15:
                stock = random.randint(0, safety)
            else:
                stock = random.randint(safety + 1, safety * 4)
            rows.append((wh[0], p[0], stock, safety, random_time()))
    return rows


def build_inbound(warehouses, products):
    rows = []
    for i in range(1, N_INBOUND + 1):
        wh = random.choice(warehouses)
        p = random.choice(products)
        t = random_time()
        rows.append((
            f"IN{t:%Y%m%d}{i:05d}",
            wh[0], p[0],
            random.randint(10, 500),
            t,
            random.choice(SUPPLIERS),
        ))
    return rows


def build_outbound(warehouses, products):
    hot, rest = products[:20], products[20:]   # 前 20 个 SKU 当爆款，被抽中概率更高
    rows = []
    for i in range(1, N_OUTBOUND + 1):
        p = random.choice(hot) if random.random() < 0.4 else random.choice(rest)
        wh = random.choice(warehouses)
        t = random_time()
        rows.append((
            f"OUT{t:%Y%m%d}{i:05d}",
            wh[0], p[0],
            random.randint(1, 50),
            t,
            random.choice(CUSTOMERS),
            random.choice(list(CARRIERS)),
        ))
    return rows


def build_shipments(outbound_rows):
    rows = []
    for i, ob in enumerate(outbound_rows, start=1):
        outbound_id, _wh, _sku, _qty, outbound_time, _cus, carrier = ob
        ship_time = outbound_time + timedelta(hours=random.randint(1, 36))
        lo, hi = CARRIERS[carrier]
        deliver_time = ship_time + timedelta(days=random.randint(lo, hi),
                                             hours=random.randint(0, 23))
        if deliver_time > NOW:
            status, deliver_time = "运输中", None
        elif random.random() < 0.03:
            status, deliver_time = "异常", None
        else:
            status = "已签收"

        rows.append((
            f"SO{ship_time:%Y%m%d}{i:05d}",
            outbound_id, carrier, ship_time, deliver_time, status,
        ))
    return rows


def main():
    conn = pymysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "chatbi_logistics"),
        charset="utf8mb4",
    )

    warehouses = build_warehouses()
    products = build_products()
    inventory = build_inventory(warehouses, products)
    inbound = build_inbound(warehouses, products)
    outbound = build_outbound(warehouses, products)
    shipments = build_shipments(outbound)

    with conn.cursor() as cur:
        cur.execute("SET FOREIGN_KEY_CHECKS = 0")   # 先关外键检查，否则 TRUNCATE 父表会被拦
        for t in ("shipments", "outbound_orders", "inbound_orders",
                  "inventory", "products", "warehouses"):
            cur.execute(f"TRUNCATE TABLE {t}")
        cur.execute("SET FOREIGN_KEY_CHECKS = 1")

        cur.executemany(
            "INSERT INTO warehouses (warehouse_id, warehouse_name, city, area_sqm, manager)"
            " VALUES (%s, %s, %s, %s, %s)", warehouses)
        cur.executemany(
            "INSERT INTO products (sku, product_name, category, unit_price, volume_l, weight_kg)"
            " VALUES (%s, %s, %s, %s, %s, %s)", products)
        cur.executemany(
            "INSERT INTO inventory (warehouse_id, sku, stock_qty, safety_stock, updated_at)"
            " VALUES (%s, %s, %s, %s, %s)", inventory)
        cur.executemany(
            "INSERT INTO inbound_orders (inbound_id, warehouse_id, sku, quantity, inbound_time, supplier)"
            " VALUES (%s, %s, %s, %s, %s, %s)", inbound)
        cur.executemany(
            "INSERT INTO outbound_orders (outbound_id, warehouse_id, sku, quantity, outbound_time, customer, carrier)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s)", outbound)
        cur.executemany(
            "INSERT INTO shipments (shipment_id, outbound_id, carrier, ship_time, deliver_time, status)"
            " VALUES (%s, %s, %s, %s, %s, %s)", shipments)
        conn.commit()

        print("\n=== 灌数结果 ===")
        for t in ("warehouses", "products", "inventory",
                  "inbound_orders", "outbound_orders", "shipments"):
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            print(f"{t:18s} {cur.fetchone()[0]:>8d} 行")

    conn.close()
    print("\n完成。")


if __name__ == "__main__":
    main()
