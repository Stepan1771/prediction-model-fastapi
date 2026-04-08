import pytest

from tests.conftest import basic_auth


PREDICT_URL = "/api/v1/predict/"

VALID_PAYLOAD = {
    "Pregnancies": 6,
    "Glucose": 148,
    "BMI": 33.6,
    "Age": 50,
}


class TestPredict:
    async def test_predict_success(self, client, registered_user):
        resp = await client.post(
            PREDICT_URL,
            json=VALID_PAYLOAD,
            headers=basic_auth(registered_user["username"], registered_user["password"]),
        )
        assert resp.status_code == 201
        body = resp.json()
        assert "prediction" in body
        assert body["prediction"] in (0, 1)

    async def test_predict_unauthenticated(self, client):
        resp = await client.post(PREDICT_URL, json=VALID_PAYLOAD)
        assert resp.status_code == 401
        assert resp.json()["code"] == "AUTH_REQUIRED"

    async def test_predict_wrong_credentials(self, client, registered_user):
        resp = await client.post(
            PREDICT_URL,
            json=VALID_PAYLOAD,
            headers=basic_auth(registered_user["username"], "BadPass000!"),
        )
        assert resp.status_code == 403

    async def test_predict_missing_fields(self, client, registered_user):
        resp = await client.post(
            PREDICT_URL,
            json={"Pregnancies": 2},
            headers=basic_auth(registered_user["username"], registered_user["password"]),
        )
        assert resp.status_code == 422

    async def test_predict_empty_body(self, client, registered_user):
        resp = await client.post(
            PREDICT_URL,
            json={},
            headers=basic_auth(registered_user["username"], registered_user["password"]),
        )
        assert resp.status_code == 422

    async def test_predict_invalid_types(self, client, registered_user):
        resp = await client.post(
            PREDICT_URL,
            json={**VALID_PAYLOAD, "Age": "not-a-number"},
            headers=basic_auth(registered_user["username"], registered_user["password"]),
        )
        assert resp.status_code == 422
