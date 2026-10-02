from chatbi.llm import chat
from chatbi.tools.schema import get_schema

SYSTEM_PROMPT = """你是一个 MySQL 数据分析助手。根据用户的问题，写出一条能回答问题的 SQL 查询。
规则：
1. 只输出 SQL 本身，不要任何解释
2. 只能写 SELECT 查询，禁止增删改
3. 只能使用下面列出的表和字段，绝对不要臆造表名或字段名
4. 需要时间条件时用 MySQL 的语法
5. 涉及仓库、商品这类有名称的实体时，要查出并返回名称，不要只返回 ID

数据库表结构如下：
{schema}
"""

def generate_sql(question:str,history:str="") -> str:
    system=SYSTEM_PROMPT.format(schema=get_schema())
    if history:
        prompt=f"之前的对话: {history}\n现在用户提问: {question}"
    else:
        prompt = question
    return chat(prompt, system).strip()

