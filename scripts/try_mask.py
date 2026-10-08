from chatbi.tools.sql_runner import run_sql

print("=== 含敏感列 manager ===")
r = run_sql("SELECT warehouse_name, city, manager FROM warehouses LIMIT 5")
print("列：", r["columns"])
for row in r["rows"]:
    print("   ", row)

print("=== 不含敏感列 ===")
r2 = run_sql("SELECT warehouse_name, area_sqm FROM warehouses LIMIT 3")
for row in r2["rows"]:
    print("   ", row)
