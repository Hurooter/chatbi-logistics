"""开发用：验证 auth.py 的密码哈希与 JWT。"""
from chatbi.auth import create_token, decode_token, hash_password, verify_password

stored = hash_password("mysecret123")
print("存进库的样子:", stored[:44], "...")
print("正确密码:", verify_password("mysecret123", stored))
print("错误密码:", verify_password("wrong-password", stored))

print()
token = create_token(42)
print("签出的 token:", token[:44], "...")
print("解回来 user_id:", decode_token(token))
print("乱码 token:", decode_token("garbage"))
