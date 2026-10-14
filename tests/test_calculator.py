"""测计算器工具：只放行纯算式，拦住代码注入。"""
from chatbi.tools.calculator import calc


def test_basic_arithmetic():
    assert calc("1+2*3") == {"ok": True, "result": 7}


def test_parentheses_and_float():
    assert calc("(1+2)*3")["result"] == 9
    assert calc("7/2")["result"] == 3.5


def test_reject_letters():
    assert calc("abc")["ok"] is False


def test_reject_code_injection():
    assert calc("__import__('os').system('dir')")["ok"] is False


def test_syntax_error_is_caught():
    assert calc("1+")["ok"] is False
