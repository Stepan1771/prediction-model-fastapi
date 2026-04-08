import pytest

from tests.conftest import basic_auth


REGISTER_URL = "/api/v1/auth/register"
ME_URL = "/api/v1/auth/me"


class TestRegister:
    async def test_register_success(self, client):
        resp = await client.post(REGISTER_URL, json={
            "username": "newuser",
            "password": "StrongPass1!",
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["user"] == "newuser"
        assert "message" in body

    async def test_register_duplicate_username(self, client):
        payload = {"username": "dupuser", "password": "StrongPass1!"}
        await client.post(REGISTER_URL, json=payload)
        resp = await client.post(REGISTER_URL, json=payload)
        assert resp.status_code == 409
        assert resp.json()["code"] == "USERNAME_ALREADY_EXISTS"

    async def test_register_missing_fields(self, client):
        resp = await client.post(REGISTER_URL, json={"username": "onlyname"})
        assert resp.status_code == 422

    async def test_register_empty_body(self, client):
        resp = await client.post(REGISTER_URL, json={})
        assert resp.status_code == 422


class TestMe:
    async def test_me_authenticated(self, client, registered_user):
        resp = await client.get(
            ME_URL,
            headers=basic_auth(registered_user["username"], registered_user["password"]),
        )
        assert resp.status_code == 200
        assert resp.json()["username"] == registered_user["username"]

    async def test_me_no_credentials(self, client):
        resp = await client.get(ME_URL)
        assert resp.status_code == 401
        assert resp.json()["code"] == "AUTH_REQUIRED"

    async def test_me_wrong_password(self, client, registered_user):
        resp = await client.get(
            ME_URL,
            headers=basic_auth(registered_user["username"], "WrongPass999!"),
        )
        assert resp.status_code == 403
        assert resp.json()["code"] == "INVALID_CREDENTIALS"

    async def test_me_unknown_user(self, client):
        resp = await client.get(
            ME_URL,
            headers=basic_auth("ghost_user", "AnyPass1!"),
        )
        assert resp.status_code == 403
