import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY","")
DB_USER = os.getenv("DB_USER","root")
DB_PASSWORD = os.getenv("DB_PASSWORD","")
DB_HOST = os.getenv("DB_HOST","127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT","3306"))
DB_NAME = os.getenv("DB_NAME","chatbi_logistics")
DB_CONNECT_TIMEOUT = 5
DB_READ_TIMEOUT = 10

def db_config() -> dict:
    return{
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "database": DB_NAME,
        "charset": "utf8mb4",
        "connect_timeout": DB_CONNECT_TIMEOUT,
        "read_timeout": DB_READ_TIMEOUT
    }

