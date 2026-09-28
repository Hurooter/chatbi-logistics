from chatbi.llm import chat

SYSTEM_PROMPT = """你是数据分析助手。用户问了一个问题，数据库给出了查询结果，请用自然语言回答用户。
规则：
1. 直接给结论，不要复述 SQL，也不要说"根据查询结果"
2. 数字要带上含义（多少件、多少元），别只丢一个裸数字
3. 结果有多行时，点出最值得注意的（最大的、最小的、异常的那个）
4. 简明扼要，两三句话说完，不要啰嗦
"""

def _format_rows(result:dict) -> str:
    lines = ["|".join(result["columns"])]
    for row in result["rows"]:
        lines.append("|".join(str(value) for value in row))
    return "\n".join(lines)

def explain(question:str,sql:str,result:dict) -> str:
    prompt = f"""用户的问题：{question}
    执行的 SQL：
    {sql}
    查询结果（共 {result["rowcount"]} 行）：
    {_format_rows(result)}
    """
    return chat(prompt,SYSTEM_PROMPT).strip()

