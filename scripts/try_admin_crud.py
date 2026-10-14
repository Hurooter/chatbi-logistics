"""开发用：验证数据管理接口（CRUD + 外键保护）。

只操作本次新建的数据，不改动既有业务数据。
"""
import time

import httpx

BASE = "http://127.0.0.1:8000"
stamp = int(time.time())
username = f"admin_{stamp}"

httpx.post(f"{BASE}/auth/register", json={"username": username, "password": "pw123456"})
token = httpx.post(f"{BASE}/auth/login",
                   json={"username": username, "password": "pw123456"}).json()["token"]
H = {"Authorization": f"Bearer {token}"}

rows = httpx.get(f"{BASE}/admin/warehouses", headers=H).json()
print("① 仓库总数:", len(rows))

r = httpx.post(f"{BASE}/admin/warehouses", headers=H, json={
    "warehouse_name": "测试仓", "city": "测试市", "area_sqm": 1000, "manager": "测试员"})
print("② 新增仓库:", r.status_code, r.json())

rows = httpx.get(f"{BASE}/admin/warehouses", headers=H).json()
print("③ 新增后总数:", len(rows))
new_id = [w for w in rows if w["warehouse_name"] == "测试仓"][0]["warehouse_id"]
print("   新仓库 id:", new_id)

r = httpx.put(f"{BASE}/admin/warehouses/{new_id}", headers=H, json={
    "warehouse_name": "测试仓改", "city": "测试市", "area_sqm": 2000, "manager": "测试员2"})
print("④ 修改:", r.status_code, r.json())

r = httpx.delete(f"{BASE}/admin/warehouses/{new_id}", headers=H)
print("⑤ 删除:", r.status_code, r.json())

rows = httpx.get(f"{BASE}/admin/warehouses", headers=H).json()
print("⑥ 删除后总数:", len(rows))

r = httpx.delete(f"{BASE}/admin/warehouses/1", headers=H)
print("⑦ 删有库存关联的仓库:", r.status_code, r.json())

r = httpx.delete(f"{BASE}/admin/warehouses/99999", headers=H)
print("⑧ 删不存在的仓库:", r.status_code, r.json())

r = httpx.get(f"{BASE}/admin/warehouses")
print("⑨ 不带 token 访问:", r.status_code)
