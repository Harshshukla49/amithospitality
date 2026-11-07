import pytest

@pytest.mark.asyncio
async def test_login_success(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@amithospitality.com", "password": "AmitConcierge2026!Secure"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "SUPER_ADMIN"
    assert data["email"] == "admin@amithospitality.com"

@pytest.mark.asyncio
async def test_login_invalid_password(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@amithospitality.com", "password": "WrongPassword!"},
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_current_user_me(client, admin_token):
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@amithospitality.com"
    assert data["role"] == "SUPER_ADMIN"

@pytest.mark.asyncio
async def test_rbac_user_management(client, admin_token, staff_token):
    # Staff cannot list users (Forbidden)
    staff_res = await client.get(
        "/api/v1/auth/users",
        headers={"Authorization": f"Bearer {staff_token}"},
    )
    assert staff_res.status_code == 403

    # Super Admin can list users
    admin_res = await client.get(
        "/api/v1/auth/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_res.status_code == 200
    assert len(admin_res.json()) >= 2
