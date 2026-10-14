from fastapi import APIRouter, Depends
from chatbi.db import query
from chatbi.deps import get_current_user

router = APIRouter(prefix="/stats",tags=["统计"])

@router.get("/warehouses")
def warehouse_stats(user_id:int = Depends(get_current_user)):
    sql = """
        SELECT w.warehouse_name,
               SUM(i.stock_qty) AS stock_qty,
               SUM(CASE WHEN i.stock_qty < i.safety_stock THEN 1 ELSE 0 END) AS low_cnt
        FROM warehouses w
        JOIN inventory i ON i.warehouse_id = w.warehouse_id
        GROUP BY w.warehouse_id, w.warehouse_name
        ORDER BY stock_qty DESC
    """
    _,rows = query(sql)
    return [
        {"name":r[0],"stock_qty":int(r[1]),"low_cnt":int(r[2])}
        for r in rows
    ]

@router.get("/trend")
def monthly_trend(user_id: int = Depends(get_current_user)):
    sql_in = """
        SELECT DATE_FORMAT(inbound_time, '%Y-%m') AS ym, SUM(quantity) AS qty
        FROM inbound_orders GROUP BY ym
    """
    sql_out = """
        SELECT DATE_FORMAT(outbound_time, '%Y-%m') AS ym, SUM(quantity) AS qty
        FROM outbound_orders GROUP BY ym
    """
    months = {}
    for ym, qty in query(sql_in)[1]:
        months.setdefault(ym, {})["inbound"] = int(qty)
    for ym, qty in query(sql_out)[1]:
        months.setdefault(ym, {})["outbound"] = int(qty)

    rows = [
        {"month": ym,
         "inbound": months[ym].get("inbound", 0),
         "outbound": months[ym].get("outbound", 0)}
        for ym in sorted(months)
    ]
    return rows[-6:]