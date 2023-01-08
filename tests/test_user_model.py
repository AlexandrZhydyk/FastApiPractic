import pytest
from starlette import status


@pytest.mark.asyncio
async def test_create_user(client):

    user = {"email": "test@test.com",
            "name": "Test",
            "password": "testpass",
            "confirmed_password": "testpass",
            "is_company": True,
            "is_active": True
            }
    resp = await client.post('users/', json=user)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["email"] == "test@test.com"
    assert resp.json()["name"] == "Test"
    assert resp.json()["is_company"] == True
    assert resp.json()["is_active"] == True


@pytest.mark.asyncio
async def test_get_me(authorized_client):
    resp = await authorized_client.get('/users/me', )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["email"] == "test@test.com"
    assert resp.json()["name"] == "Test"
    assert resp.json()["is_company"] == True
    assert resp.json()["is_active"] == True


@pytest.mark.parametrize(
    "update_field, update_value",
    (
        ("email", "updated_test@test.com"),
        ("name", "Updated"),
    ),
)
async def test_update_me(authorized_client, update_field, update_value):
    resp = await authorized_client.put('/users/me', json={update_field: update_value})
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()[update_field] == update_value
