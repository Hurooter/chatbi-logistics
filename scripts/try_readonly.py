from chatbi.tools.sql_runner import _is_readonly

CASES = [
    ("SELECT * FROM warehouses", True),
    ("WITH t AS (SELECT warehouse_id FROM warehouses) SELECT * FROM t", True),
    ("SELECT * FROM products WHERE product_name = 'drop table'", True),
    ("SELECT * FROM warehouses; DROP TABLE warehouses", False),
    ("DROP TABLE warehouses", False),
    ("UPDATE inventory SET stock_qty = 0", False),
    ("SELECT * INTO OUTFILE '/tmp/x' FROM warehouses", False),
    ("DELETE FROM inventory", False),
]

for sql, expected in CASES:
    got = _is_readonly(sql)
    mark = "OK" if got == expected else "!!"
    print(f"[{mark}] 期望={expected!s:5} 实际={got!s:5} {sql}")