import hashlib
import hmac
import os
import time
import jwt
from chatbi.config import JWT_EXPIRE_SECONDS, JWT_SECRET

_ITERATIONS = 200_000

def hash_password(password:str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256",password.encode(),salt,_ITERATIONS)
    return f"{salt.hex()}${digest.hex()}"

def verify_password(password:str,stored:str) -> bool:
    salt_hex, digest_hex = stored.split("$")
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), _ITERATIONS)
    return hmac.compare_digest(digest, bytes.fromhex(digest_hex))

def create_token(user_id: int) -> str:
    payload = {"sub": str(user_id), "exp": int(time.time()) + JWT_EXPIRE_SECONDS}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return None
    return int(payload["sub"])
