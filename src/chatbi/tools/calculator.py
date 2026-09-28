import re
_ALLOWED = re.compile(r"^[0-9+\-*/(). ]+$")

def calc(expression: str) -> dict:
    e=expression.strip()
    if not _ALLOWED.match(e):
        return {"ok":False,"error":"只支持数字和 + - * / ( ) 组成的算式"}
    try:
        result=eval(e,{"__builtins__":{}})
    except Exception as e:
        return {"ok":False,"error":f"计算出错：{e}"}
    return {"ok":True,"result":result}
