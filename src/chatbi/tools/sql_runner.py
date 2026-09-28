from chatbi.db import query
MAX_ROWS = 200
FORBIDDEN = ("insert", "update", "delete", "drop", "alter", "truncate",
             "create", "replace", "grant", "revoke", "rename")

def _is_readonly(sql:str) -> bool:
    s=sql.strip().lower()
    if not (s.startswith("select") or s.startswith("with")):
        return False
    return not any(word in s for word in FORBIDDEN)

def run_sql(sql:str) -> dict:
    if  not _is_readonly(sql):
        return {"ok":False,"error":"只允许执行查询操作，这条被拒绝了。"}
    try:
        columns,rows = query(sql)
    except Exception as e:
        return {"ok":False,"error":f"SQL执行出错，{e}"}
    return {"ok":True,"columns":columns,"rows":rows[:MAX_ROWS],"rowcount":len(rows),"truncated":len(rows)>MAX_ROWS}
