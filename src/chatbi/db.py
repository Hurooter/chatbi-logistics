from typing import Any
import pymysql
from chatbi.config import db_config

def query(sql:str,params: tuple | None = None) -> tuple[list[str], list[tuple]]:
    conn = pymysql.connect(**db_config())
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            columns=[d[0] for d in cursor.description]
            rows=list(cursor.fetchall())
        return columns, rows
    finally:
        conn.close()

