"""数据管理接口：仓库 / 商品的增删改查。

这条是"管理通道"——用户填表单、后端拼**参数化 SQL**，完全不经过模型。
跟助手的只读通道（run_sql 白名单）物理分开。
"""
import pymysql
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from chatbi.db import execute, query
from chatbi.deps import get_current_user

router = APIRouter(prefix="/admin", tags=["数据管理"])


# ---------------- 仓库 ----------------

class WarehouseIn(BaseModel):
    warehouse_name: str
    city: str
    area_sqm: int
    manager: str


@router.get("/warehouses")
def list_warehouses(user_id: int = Depends(get_current_user)):
    cols, rows = query(
        "SELECT warehouse_id, warehouse_name, city, area_sqm, manager "
        "FROM warehouses ORDER BY warehouse_id"
    )
    return [dict(zip(cols, r)) for r in rows]


@router.post("/warehouses")
def create_warehouse(req: WarehouseIn, user_id: int = Depends(get_current_user)):
    execute(
        "INSERT INTO warehouses (warehouse_name, city, area_sqm, manager) VALUES (%s, %s, %s, %s)",
        (req.warehouse_name, req.city, req.area_sqm, req.manager),
    )
    return {"message": "已新增"}


@router.put("/warehouses/{warehouse_id}")
def update_warehouse(warehouse_id: int, req: WarehouseIn,
                     user_id: int = Depends(get_current_user)):
    _, rows = query("SELECT 1 FROM warehouses WHERE warehouse_id = %s", (warehouse_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="仓库不存在")
    execute(
        "UPDATE warehouses SET warehouse_name=%s, city=%s, area_sqm=%s, manager=%s "
        "WHERE warehouse_id=%s",
        (req.warehouse_name, req.city, req.area_sqm, req.manager, warehouse_id),
    )
    return {"message": "已更新"}


@router.delete("/warehouses/{warehouse_id}")
def delete_warehouse(warehouse_id: int, user_id: int = Depends(get_current_user)):
    try:
        n = execute("DELETE FROM warehouses WHERE warehouse_id = %s", (warehouse_id,))
    except pymysql.err.IntegrityError:
        raise HTTPException(status_code=409, detail="该仓库还有库存或单据关联，不能删除")
    if n == 0:
        raise HTTPException(status_code=404, detail="仓库不存在")
    return {"message": "已删除"}


# ---------------- 商品 ----------------

class ProductIn(BaseModel):
    sku: str
    product_name: str
    category: str
    unit_price: float
    volume_l: float
    weight_kg: float


@router.get("/products")
def list_products(user_id: int = Depends(get_current_user)):
    cols, rows = query(
        "SELECT sku, product_name, category, unit_price, volume_l, weight_kg "
        "FROM products ORDER BY sku"
    )
    return [dict(zip(cols, r)) for r in rows]


@router.post("/products")
def create_product(req: ProductIn, user_id: int = Depends(get_current_user)):
    try:
        execute(
            "INSERT INTO products (sku, product_name, category, unit_price, volume_l, weight_kg) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (req.sku, req.product_name, req.category, req.unit_price, req.volume_l, req.weight_kg),
        )
    except pymysql.err.IntegrityError:
        raise HTTPException(status_code=409, detail="该 SKU 已存在")
    return {"message": "已新增"}


@router.put("/products/{sku}")
def update_product(sku: str, req: ProductIn, user_id: int = Depends(get_current_user)):
    _, rows = query("SELECT 1 FROM products WHERE sku = %s", (sku,))
    if not rows:
        raise HTTPException(status_code=404, detail="商品不存在")
    execute(
        "UPDATE products SET product_name=%s, category=%s, unit_price=%s, volume_l=%s, weight_kg=%s "
        "WHERE sku=%s",
        (req.product_name, req.category, req.unit_price, req.volume_l, req.weight_kg, sku),
    )
    return {"message": "已更新"}


@router.delete("/products/{sku}")
def delete_product(sku: str, user_id: int = Depends(get_current_user)):
    try:
        n = execute("DELETE FROM products WHERE sku = %s", (sku,))
    except pymysql.err.IntegrityError:
        raise HTTPException(status_code=409, detail="该商品还有库存或单据关联，不能删除")
    if n == 0:
        raise HTTPException(status_code=404, detail="商品不存在")
    return {"message": "已删除"}
