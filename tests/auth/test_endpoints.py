import pytest

from fastapi import status
from async_asgi_testclient import TestClient # type: ignore

from src.database import get_redis_connection

pytestmark = pytest.mark.asyncio


async def test_register(client: TestClient):
    payload = {
        "email": "test@example.com",
        "password": "mM@#12345678n",
        "confirmPassword": "mM@#12345678n"
    }
    response = await client.post("/auth/register/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {'email': 'test@example.com'}


@pytest.mark.parametrize(
        "entered_data, expected_status",
        [
            (
                {
                    "email": "test1@example.com",
                    "password": "mM@12",
                    "confirmPassword": "mM@12"
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            (
                {
                    "email": "test1@example.com",
                    "password": "123456789",
                    "confirmPassword": "123456789"
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            (
                {
                    "email": "test1@example.com",
                    "password": "test@example.com",
                    "confirmPassword": "test@example.com"
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            (
                {
                    "email": "test1@example.com",
                    "password": "@m12345&test12",
                    "confirmPassword": "@m12345&test12"
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            
        ]
)
async def test_register_with_invalid_data(client: TestClient, entered_data, expected_status):
    response = await client.post("/auth/register/", json=entered_data)
    assert response.status_code == expected_status


async def test_register_with_duplicate_email(client: TestClient):
    payload = {
        "email": "test@example.com",
        "password": "mM@#12345678n",
        "confirmPassword": "mM@#12345678n"
    }
    response = await client.post("/auth/register/", json=payload)

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


async def test_verify_account_with_invalid_verification_code(client: TestClient):
    payload = {
        "verificationCode": "12345678"
    }
    response = await client.post("/auth/verify-account/", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Verification code is invalid, get a new one"}


async def test_verify_account_with_valid_verification_code(client: TestClient):
    r = get_redis_connection()
    result_list: list[str] = r.keys(pattern="verification_code*") # type: ignore
    payload = {
        "verificationCode": result_list[0].split(":")[1]
    }
    response = await client.post("/auth/verify-account/", json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Account verified successfully"}


async def test_login_with_not_existing_account(client: TestClient):
    payload = {
        "username": "invalid@email.com",
        "password": "invalid12345"
    }
    response = await client.post(
        "/auth/login/", headers={"Content-Type": "application/x-www-form-urlencoded"}, data=payload
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "There is no active account with the provided info"}