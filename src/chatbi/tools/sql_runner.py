from chatbi.db import query
import sqlglot
MAX_ROWS = 200
SENSITIVE_COLUMNS = {"manager", "customer"}

def _is_readonly(sql:str) -> bool:
    try:
        statements = [s for s in sqlglot.parse(sql,read="mysql") if s is not None]
    except sqlglot.errors.ParseError:
        return False
    if len(statements) != 1:
        return False
    return isinstance(statements[0],sqlglot.exp.Select)

def _mask_rows(columns:list[str],rows:list[tuple]) -> list[tuple]:
    hit = { i for i,c in enumerate(columns) if c.lower() in SENSITIVE_COLUMNS}
    if not hit:
        return rows
    return [tuple("***" if i in hit else v for i,v in enumerate(row)) for row in rows]

def run_sql(sql:str) -> dict:
    if  not _is_readonly(sql):
        return {"ok":False,"error":"只允许执行查询操作，这条被拒绝了。"}
    try:
        columns,rows = query(sql)
        rows = _mask_rows(columns,rows)
    except Exception as e:
        return {"ok":False,"error":f"SQL执行出错，{e}"}
    return {"ok":True,"columns":columns,"rows":rows[:MAX_ROWS],"rowcount":len(rows),"truncated":len(rows)>MAX_ROWS}
