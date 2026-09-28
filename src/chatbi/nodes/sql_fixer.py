from chatbi.llm import chat
from chatbi.tools.schema import get_schema

SYSTEM_PROMPT = """你之前写的 SQL 执行失败了。请根据报错信息修正它。
规则：
1. 只输出修正后的 SQL，不要任何解释
2. 只能写 SELECT 查询
3. 报错信息里通常会指出出错的位置，重点看那里
只能使用下面列出的表和字段，不要臆造字段名
数据库表结构如下：
{schema}
"""

def fix_sql(question:str,sql:str,error:str) -> str:
    prompt=f"""用户的问题：{question}
    你之前写的 SQL：
    {sql}
    执行报错：
    {error}
    请修正。
    """
    system=SYSTEM_PROMPT.format(schema=get_schema())
    return chat(prompt,system).strip()


