"""认证模块单元测试: password hashing, JWT"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


class TestPasswordHashing:
    """密码哈希与验证"""

    def test_hash_returns_string(self):
        """哈希后应返回字符串"""
        result = hash_password("mypassword")
        assert isinstance(result, str)
        assert len(result) > 20  # bcrypt hash 至少 60 字符

    def test_hash_same_password_different_result(self):
        """同一密码两次哈希结果不同（盐值不同）"""
        h1 = hash_password("same_password")
        h2 = hash_password("same_password")
        assert h1 != h2  # bcrypt 每次生成不同盐值

    def test_verify_correct_password(self):
        """正确密码验证通过"""
        hashed = hash_password("hello_world")
        assert verify_password("hello_world", hashed) is True

    def test_verify_wrong_password(self):
        """错误密码验证失败"""
        hashed = hash_password("correct_password")
        assert verify_password("wrong_password", hashed) is False

    def test_verify_empty_password(self):
        """空密码也能正常哈希和验证"""
        hashed = hash_password("")
        assert verify_password("", hashed) is True

    def test_verify_unicode_password(self):
        """中文密码正常处理"""
        hashed = hash_password("中文密码测试123")
        assert verify_password("中文密码测试123", hashed) is True

    def test_hash_long_password(self):
        """长密码正常处理（不超过72字节的bcrypt限制）"""
        long_pw = "a" * 50
        hashed = hash_password(long_pw)
        assert verify_password(long_pw, hashed) is True


class TestJWTToken:
    """JWT Token 生成与验证"""

    def test_create_and_decode_token(self):
        """生成的 Token 能正确解码"""
        token = create_access_token({"sub": "user_001", "role": "user"})
        assert isinstance(token, str)
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "user_001"
        assert payload["role"] == "user"

    def test_decode_invalid_token(self):
        """无效 Token 返回 None"""
        assert decode_access_token("not_a_valid_token") is None
        assert decode_access_token("") is None

    def test_decode_tampered_token(self):
        """篡改过的 Token 返回 None"""
        token = create_access_token({"sub": "user_001"})
        tampered = token[:-5] + "XXXXX"  # 修改最后几位
        assert decode_access_token(tampered) is None

    def test_token_contains_expiry(self):
        """Token 包含过期时间"""
        token = create_access_token({"sub": "test_user"})
        payload = decode_access_token(token)
        assert "exp" in payload

    def test_token_with_custom_data(self):
        """Token 支持自定义 payload 字段"""
        token = create_access_token({
            "sub": "user_002",
            "role": "admin",
            "custom_field": "custom_value",
        })
        payload = decode_access_token(token)
        assert payload["sub"] == "user_002"
        assert payload["role"] == "admin"
        assert payload["custom_field"] == "custom_value"
