"""开发用：打印当前数据库的全部表结构。

用法：PyCharm 里右键 Run，或命令行 uv run python scripts/show_schema.py
"""
from chatbi.tools.schema import get_schema

print(get_schema())
