import pytest

from fastapi import Response


@pytest.mark.parametrize(
    "data, expected_status, expected_response",
    [
        (
            {"username": "defaultuser",     "email": "defaultuser@example.com",     "password": "SecurePassword1!"},
            201,
            {"username": "defaultuser",     "email": "defaultuser@example.com",     "role": "user"},
        ),
        (
            {"username": "a",               "email": "defaultuser@example.com",     "password": "SecurePassword1!"},
            422,
            {"detail": "Username must be at least 3 characters long"},
        ),
        (
            {"username": "defaultuser",     "email": "invalidemail",                "password": "SecurePassword1!"},
            422,
            {"detail": "An email address must have an @-sign"},
        ),
        (
            {"username": "defaultuser",     "email": "defaultuser@example.com",     "password": "123"},
            422,
            {"detail": "Password must be at least 8 characters long"},
        ),
    ],
)
@pytest.mark.asyncio
async def test_create_user(client_async, data, expected_status, expected_response):

    response: Response = await client_async.post("/api/v1/auth/register", json=data)

    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
    json_data = response.json()

    if expected_status == 201:
        assert json_data["username"] == expected_response["username"]
        assert json_data["email"] == expected_response["email"]
        assert json_data["role"] == expected_response["role"]
    else:
        assert expected_response["detail"] in str(json_data)
