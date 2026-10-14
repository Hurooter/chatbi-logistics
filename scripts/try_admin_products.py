"""开发用：验证商品接口的 CRUD + 主键/外键保护。"""
import time

import httpx

BASE = "http://127.0.0.1:8000"
stamp = int(time.time())
username = f"prod_{stamp}"

httpx.post(f"{BASE}/auth/register", json={"username": username, "password": "pw123456"})
token = httpx.post(f"{BASE}/auth/login",
                   json={"username": username, "password": "pw123456"}).json()["token"]
H = {"Authorization": f"Bearer {token}"}

rows = httpx.get(f"{BASE}/admin/products", headers=H).json()
print("① 商品总数:", len(rows))
first_sku = rows[0]["sku"]

sku = f"ZZTEST{stamp % 100000}"
body = {"sku": sku, "product_name": "测试品", "category": "测试",
        "unit_price": 9.9, "volume_l": 1.0, "weight_kg": 0.5}

r = httpx.post(f"{BASE}/admin/products", headers=H, json=body)
print("② 新增:", r.status_code, r.json())

r = httpx.post(f"{BASE}/admin/products", headers=H, json=body)
print("③ 重复 SKU:", r.status_code, r.json())

body2 = dict(body, product_name="测试品改", unit_price=19.9)
r = httpx.put(f"{BASE}/admin/products/{sku}", headers=H, json=body2)
print("④ 修改:", r.status_code, r.json())

r = httpx.delete(f"{BASE}/admin/products/{sku}", headers=H)
print("⑤ 删除:", r.status_code, r.json())

rows = httpx.get(f"{BASE}/admin/products", headers=H).json()
print("⑥ 删完总数:", len(rows))

r = httpx.delete(f"{BASE}/admin/products/{first_sku}", headers=H)
print(f"⑦ 删有库存关联的商品({first_sku}):", r.status_code, r.json())
