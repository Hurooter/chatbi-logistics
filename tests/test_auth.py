"""测密码哈希与 JWT：哈希要带随机盐、验证要对；token 能解出、被篡改要失效。"""
from chatbi.auth import create_token, decode_token, hash_password, verify_password


def test_hash_has_salt_and_is_random():
    h1 = hash_password("pw123456")
    h2 = hash_password("pw123456")
    assert "$" in h1          # 格式是「盐$指纹」
    assert h1 != h2           # 随机盐 → 同一密码两次哈希不同


def test_verify_password():
    stored = hash_password("secret")
    assert verify_password("secret", stored) is True
    assert verify_password("wrong", stored) is False


def test_token_roundtrip():
    assert decode_token(create_token(42)) == 42


def test_token_invalid_returns_none():
    assert decode_token("garbage") is None
    assert decode_token("a.b.c") is None


def test_token_tampered_returns_none():
    token = create_token(1)
    tampered = token[:-1] + ("a" if token[-1] != "a" else "b")   # 改掉签名最后一个字符
    assert decode_token(tampered) is None
