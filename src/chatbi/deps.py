"""公共依赖：多个模块都要用的东西放这，避免互相 import 成环。"""
import time
from fastapi import Depends, Header, HTTPException

from chatbi.auth import decode_token


def get_current_user(authorization: str | None = Header(None)) -> int:
    token = (authorization or "").removeprefix("Bearer ").strip()
    user_id = decode_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="未登录或登录已过期")
    return user_id


# 限流：按 user_id 做滑动窗口，内存版（重启清零、仅单进程有效）
_WINDOWS: dict[int, list[float]] = {}
RATE_LIMIT = 10        # 窗口内允许的次数
RATE_WINDOW = 60       # 窗口长度（秒）


def rate_limit(user_id: int = Depends(get_current_user)) -> int:
    """先鉴权（拿 user_id），再数它这一窗口内已经请求了几次，超了就 429。"""
    now = time.time()
    stamps = [t for t in _WINDOWS.get(user_id, []) if now - t < RATE_WINDOW]
    if len(stamps) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="请求过于频繁，请稍后再试")
    stamps.append(now)
    _WINDOWS[user_id] = stamps
    return user_id

