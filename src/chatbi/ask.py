from chatbi.nodes.explainer import explain
from chatbi.nodes.sql_fixer import fix_sql
from chatbi.nodes.sql_generator import generate_sql
from chatbi.tools.sql_runner import run_sql

MAX_RETRY = 2   # 最多重写几次

def ask(question:str) -> dict:
    sql = generate_sql(question)
    result = run_sql(sql)
    attempts=0
    while not result["ok"] and attempts<MAX_RETRY:
        attempts += 1
        sql = fix_sql(question,sql,result["error"])
        result = run_sql(sql)
    if result["ok"]:
        answer = explain(question,sql,result)
    else:
        answer = "抱歉，这个问题我试了几次都没查出来，可能库里没有相关数据。"
    return{
        "question":question,
        "sql":sql,
        "result":result,
        "answer":answer,
        "attempts":attempts
    }


