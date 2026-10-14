"""测评估集的判分逻辑：结果集比对与「结论正确」判定。"""
from decimal import Decimal

from run_eval import answer_numbers, canon, close, conclusion_ok, project_match


def test_norm_decimal():
    assert canon([(Decimal("3.10"),)]) == canon([(3.1,)])


def test_canon_ignores_row_order():
    assert canon([(2,), (1,)]) == canon([(1,), (2,)])


def test_project_match_allows_extra_columns():
    model = [(1, "华东仓", 100), (2, "华北仓", 200)]
    gold = [("华东仓", 100), ("华北仓", 200)]
    assert project_match(model, gold) is True


def test_project_match_rejects_wrong_value():
    assert project_match([(1, "华东仓", 999)], [("华东仓", 100)]) is False


def test_answer_numbers_understands_units():
    nums = answer_numbers("约 1.113 亿元，另有 9.6 万件")
    assert any(close(n, 111332526) for n in nums)     # 亿 → ×1e8
    assert any(close(n, 96167) for n in nums)         # 万 → ×1e4


def test_conclusion_ok():
    gold = [("华东仓", Decimal("109620"))]
    assert conclusion_ok(gold, "华东仓库存 109,620 件") is True
    assert conclusion_ok(gold, "华北仓库存 100 件") is False
