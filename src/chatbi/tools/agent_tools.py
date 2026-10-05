from langchain_core.tools import tool
from chatbi.tools.schema import get_schema
from chatbi.tools.sql_runner import run_sql
from chatbi.tools.calculator import calc


@tool
def schema_tool():
    """查看数据库里所有表的结构：表名、字段名、字段类型、中文含义。

    在写 SQL 之前必须先调用它，确认表名和字段名的准确写法。"""
    return get_schema()

@tool
def sql_tool(sql:str) -> str:
    """执行一条只读SQL(只能是SELECT)，返回查询结果
    Args：
        sql:要执行的SQL语句"""
    result = run_sql(sql)
    if not result["ok"]:
        return f"error:{result['error']}"
    head = f"共{result['rowcount']}行"
    if result["truncated"]:
        head += f"（太多，只显示前 {len(result['rows'])} 行）"
    lines = [head,"|".join(result["columns"])]
    for row in result["rows"]:
        lines.append("|".join(str(value) for value in row))
    return "\n".join(lines)

@tool
def calc_tool(expression:str) -> str:
    """计算一个纯数字算式，比如 (2450-1800)/1800*100。

    需要做算术时用它，不要自己心算，心算容易出错。

    Args:
        expression: 只含数字和 + - * / ( ) 的算式"""
    result = calc(expression)
    if not result["ok"]:
        return f"error:{result['error']}"
    return str(result["result"])
