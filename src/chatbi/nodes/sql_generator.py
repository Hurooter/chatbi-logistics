from chatbi.llm import chat
from chatbi.tools.schema import get_schema

SYSTEM_PROMPT = """你是一个 MySQL 数据分析助手。根据用户的问题，写出一条能回答问题的 SQL 查询。
规则：
1. 只输出 SQL 本身，不要任何解释
2. 只能写 SELECT 查询，禁止增删改
3. 只能使用下面列出的表和字段，绝对不要臆造表名或字段名
4. 需要时间条件时用 MySQL 的语法

数据库表结构如下：
{schema}
"""

def generate_sql(question:str) -> str:
    system=SYSTEM_PROMPT.format(schema=get_schema())
    return chat(question, system).strip()

