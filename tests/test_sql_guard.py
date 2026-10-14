"""测只读 SQL 白名单——这是安全关键点：只放行单条 SELECT，其余全拒。"""
import pytest
from chatbi.tools.sql_runner import _is_readonly


@pytest.mark.parametrize("sql", [
    "SELECT 1",
    "select * from warehouses",
    "SELECT a FROM t WHERE x = 1 ORDER BY a LIMIT 5",
])
def test_select_allowed(sql):
    assert _is_readonly(sql) is True


@pytest.mark.parametrize("sql", [
    "INSERT INTO t VALUES (1)",
    "UPDATE t SET a = 1",
    "DELETE FROM t",
    "DROP TABLE t",
    "ALTER TABLE t ADD c INT",
    "SELECT 1; DROP TABLE t",        # 多语句：夹带写操作
    "not sql at all",               # 解析不了
    "",                             # 空串
])
def test_write_or_bad_rejected(sql):
    assert _is_readonly(sql) is False
