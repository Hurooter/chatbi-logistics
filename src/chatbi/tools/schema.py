"""工具一：查表结构。把库里每张表的字段说明读出来，供模型理解数据库。"""
from chatbi.config import DB_NAME
from chatbi.db import query


def get_schema() -> str:
    """返回全部表的字段说明，格式化成一整段文本。"""
    sql = """
        SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, COLUMN_COMMENT
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s
        ORDER BY TABLE_NAME, ORDINAL_POSITION
    """
    _, rows = query(sql, (DB_NAME,))

    # 把扁平的结果按表名归拢：{表名: [(字段, 类型, 注释), ...]}
    tables = {}
    for table, column, col_type, comment in rows:
        if table not in tables:
            tables[table] = []
        tables[table].append((column, col_type, comment))

    lines = []
    for table, columns in tables.items():
        lines.append(f"【{table}】")
        for column, col_type, comment in columns:
            lines.append(f"  {column:<16}{col_type:<16}{comment}")
        lines.append("")
    return "\n".join(lines)
