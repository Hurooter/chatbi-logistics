# -*- coding: utf-8 -*-
"""20 题评估集：每题的「问题」+「标准 SQL」。

标准 SQL 只用来跑出「期望结果集」，不是拿来和模型的 SQL 比文本。
覆盖：单表条件 / JOIN / GROUP BY / 聚合 / 比率 / 时间过滤 / 排序取前 N / 多表连接。
"""

QUESTIONS = [
    {"q": "有哪些仓库，分别在哪个城市？",
     "gold": "SELECT warehouse_name, city FROM warehouses ORDER BY warehouse_id"},

    {"q": "各仓库的库存总量分别是多少？",
     "gold": "SELECT w.warehouse_name, SUM(i.stock_qty) AS total FROM warehouses w JOIN inventory i ON i.warehouse_id=w.warehouse_id GROUP BY w.warehouse_id, w.warehouse_name ORDER BY total DESC"},

    {"q": "有多少条库存记录低于安全库存？",
     "gold": "SELECT COUNT(*) FROM inventory WHERE stock_qty < safety_stock"},

    {"q": "库存低于安全库存的记录数最多的仓库是哪个？",
     "gold": "SELECT w.warehouse_name, COUNT(*) AS c FROM warehouses w JOIN inventory i ON i.warehouse_id=w.warehouse_id WHERE i.stock_qty < i.safety_stock GROUP BY w.warehouse_id, w.warehouse_name ORDER BY c DESC LIMIT 1"},

    {"q": "每个商品类目有多少个 SKU？",
     "gold": "SELECT category, COUNT(*) AS sku_count FROM products GROUP BY category ORDER BY sku_count DESC"},

    {"q": "单价最贵的 5 个商品是哪几个（名称和单价）？",
     "gold": "SELECT product_name, unit_price FROM products ORDER BY unit_price DESC LIMIT 5"},

    {"q": "华东仓的库存总量是多少件？",
     "gold": "SELECT SUM(i.stock_qty) FROM warehouses w JOIN inventory i ON i.warehouse_id=w.warehouse_id WHERE w.warehouse_name='华东仓'"},

    {"q": "各承运商的运单总数分别是多少？",
     "gold": "SELECT carrier, COUNT(*) AS cnt FROM shipments GROUP BY carrier ORDER BY cnt DESC"},

    {"q": "各状态的运单数分别是多少？",
     "gold": "SELECT status, COUNT(*) AS cnt FROM shipments GROUP BY status ORDER BY cnt DESC"},

    {"q": "有多少条运单还没签收（状态不是已签收）？",
     "gold": "SELECT COUNT(*) FROM shipments WHERE status <> '已签收'"},

    {"q": "2026 年 8 月的入库总量是多少？",
     "gold": "SELECT SUM(quantity) FROM inbound_orders WHERE inbound_time >= '2026-08-01' AND inbound_time < '2026-09-01'"},

    {"q": "各供应商的入库总量分别是多少？",
     "gold": "SELECT supplier, SUM(quantity) AS qty FROM inbound_orders GROUP BY supplier ORDER BY qty DESC"},

    {"q": "出库量最多的前 5 个 SKU 是哪些？",
     "gold": "SELECT sku, SUM(quantity) AS qty FROM outbound_orders GROUP BY sku ORDER BY qty DESC LIMIT 5"},

    {"q": "各仓库的存货总金额是多少（库存件数 × 单价）？",
     "gold": "SELECT w.warehouse_name, ROUND(SUM(i.stock_qty * p.unit_price), 2) AS amount FROM inventory i JOIN warehouses w ON w.warehouse_id=i.warehouse_id JOIN products p ON p.sku=i.sku GROUP BY w.warehouse_id, w.warehouse_name ORDER BY amount DESC"},

    {"q": "每个仓库有多少种 SKU？",
     "gold": "SELECT w.warehouse_name, COUNT(DISTINCT i.sku) AS sku_kinds FROM warehouses w JOIN inventory i ON i.warehouse_id=w.warehouse_id GROUP BY w.warehouse_id, w.warehouse_name"},

    {"q": "有多少个仓库位于上海？",
     "gold": "SELECT COUNT(*) FROM warehouses WHERE city='上海'"},

    {"q": "运单中「异常」状态的占比是多少（百分比，保留两位小数）？",
     "gold": "SELECT ROUND(SUM(status='异常')/COUNT(*)*100, 2) FROM shipments"},

    {"q": "签收超过 5 天的已签收运单有多少条？",
     "gold": "SELECT COUNT(*) FROM shipments WHERE status='已签收' AND DATEDIFF(deliver_time, ship_time) > 5"},

    {"q": "各仓库的入库单数量分别是多少？",
     "gold": "SELECT w.warehouse_name, COUNT(*) AS cnt FROM warehouses w JOIN inbound_orders o ON o.warehouse_id=w.warehouse_id GROUP BY w.warehouse_id, w.warehouse_name ORDER BY cnt DESC"},

    {"q": "库存总量最低的仓库是哪个？",
     "gold": "SELECT w.warehouse_name FROM warehouses w JOIN inventory i ON i.warehouse_id=w.warehouse_id GROUP BY w.warehouse_id, w.warehouse_name ORDER BY SUM(i.stock_qty) ASC LIMIT 1"},
]
