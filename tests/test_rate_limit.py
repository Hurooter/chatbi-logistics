"""测限流：窗口内超次数返回 429，且不同用户互不影响。"""
import pytest
from fastapi import HTTPException

import chatbi.deps as deps


def setup_function():
    deps._WINDOWS.clear()          # 每个用例前清空计数，互不干扰


def test_under_limit_passes():
    for _ in range(deps.RATE_LIMIT):
        assert deps.rate_limit(user_id=1) == 1


def test_over_limit_raises_429():
    for _ in range(deps.RATE_LIMIT):
        deps.rate_limit(user_id=2)
    with pytest.raises(HTTPException) as err:
        deps.rate_limit(user_id=2)
    assert err.value.status_code == 429


def test_users_are_isolated():
    for _ in range(deps.RATE_LIMIT):
        deps.rate_limit(user_id=3)
    assert deps.rate_limit(user_id=4) == 4      # 换个用户不受影响
