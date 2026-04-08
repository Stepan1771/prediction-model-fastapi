import pytest

from unittest.mock import (
    AsyncMock,
    MagicMock,
)

from services.auth import AuthService

from exceptions.auth import UsernameAlreadyExistsError

from schemas import RegisterRequest


def make_service(existing_user=None):
    repo = MagicMock()
    repo.get_by_username = AsyncMock(return_value=existing_user)
    repo.create = AsyncMock(return_value=MagicMock(username="testuser"))
    return AuthService(user_repository=repo), repo


class TestAuthServiceRegister:
    async def test_register_new_user(self):
        service, repo = make_service(existing_user=None)
        schema = RegisterRequest(username="testuser", password="Pass123!")
        user = await service.register(schema=schema)
        repo.create.assert_awaited_once()
        assert user.username == "testuser"

    async def test_register_duplicate_raises(self):
        fake_user = MagicMock(username="testuser")
        service, _ = make_service(existing_user=fake_user)
        schema = RegisterRequest(username="testuser", password="Pass123!")
        with pytest.raises(UsernameAlreadyExistsError):
            await service.register(schema=schema)

    async def test_password_is_hashed(self):
        service, repo = make_service(existing_user=None)
        schema = RegisterRequest(username="u", password="MyPlainPass1!")
        await service.register(schema=schema)

        call_kwargs = repo.create.call_args
        created_schema = call_kwargs.kwargs.get("schema") or call_kwargs.args[0]
        assert created_schema.password_hash != "MyPlainPass1!"
        assert len(created_schema.password_hash) > 20

