from mcp.server.mcpserver import MCPServer
from chatbi.tools.schema import get_schema
from chatbi.tools.sql_runner import run_sql
from chatbi.tools.calculator import calc

srv = MCPServer("chatbi-db")

@srv.tool()
def schema_tool() -> str:
    """查看数据库里所有表的结构：表名、字段名、字段类型、中文含义。"""
    return get_schema()

@srv.tool()
def sql_tool(sql:str) -> str:
    """执行一条只读 SQL（只能是 SELECT），返回查询结果。参数 sql 就是 SQL 语句本身。"""
    r = run_sql(sql)
    if not r['ok']:
        return f"error:{r['error']}"
    head = f"共{r['rowcount']}行"
    if r["truncated"]:
        head += f"（太多，只显示前 {len(r['rows'])} 行）"
    lines = [head, "|".join(r["columns"])]
    for row in r["rows"]:
        lines.append("|".join(str(v) for v in row))
    return "\n".join(lines)

@srv.tool()
def calc_tool(expression:str) -> str:
    """计算一个纯数字算式，比如 (2450-1800)/1800*100。只支持数字和 + - * / ( )。"""
    r = calc(expression)
    if not r['ok']:
        return f"error:{r['error']}"
    return str(r["result"])













if __name__ == "__main__":
    srv.run()
