import pytest

from core.security import (
    hash_password,
    verify_password,
)


class TestHashPassword:
    def test_returns_string(self):
        result = hash_password("mypassword")
        assert isinstance(result, str)

    def test_not_plain_text(self):
        password = "mypassword"
        assert hash_password(password) != password

    def test_different_hashes_for_same_password(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2


class TestVerifyPassword:
    def test_correct_password(self):
        hashed = hash_password("correct")
        assert verify_password("correct", hashed) is True

    def test_wrong_password(self):
        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False

    def test_empty_password_fails(self):
        hashed = hash_password("secret")
        assert verify_password("", hashed) is False

    def test_invalid_hash_returns_false(self):
        assert verify_password("any", "not-a-valid-hash") is False
