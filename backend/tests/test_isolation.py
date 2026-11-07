import pytest

@pytest.mark.asyncio
async def test_active_environment_default(client):
    res = await client.get("/api/v1/environment/active")
    assert res.status_code == 200
    assert res.json()["environment"] == "DEMO"
    assert res.json()["is_demo"] is True

@pytest.mark.asyncio
async def test_menu_environment_isolation_demo(client):
    res = await client.get("/api/v1/menus?outlet_id=1&environment=DEMO")
    assert res.status_code == 200
    items = res.json()
    assert len(items) >= 1
    assert any("Demo" in item["name"] for item in items)
    assert not any("Real Verified" in item["name"] for item in items)

@pytest.mark.asyncio
async def test_environment_switch_rbac(client, staff_token, admin_token):
    # Staff cannot switch mode
    res = await client.post(
        "/api/v1/environment/switch",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={
            "target_environment": "REAL",
            "reason": "Unauthorized staff attempt",
            "confirm_acknowledgment": True,
        },
    )
    assert res.status_code == 403

    # Super Admin can switch mode
    admin_res = await client.post(
        "/api/v1/environment/switch",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "target_environment": "REAL",
            "reason": "Transitioning to verified corporate records",
            "confirm_acknowledgment": True,
        },
    )
    assert admin_res.status_code == 200
    assert admin_res.json()["active_environment"] == "REAL"

    # Verify active environment is REAL
    check_res = await client.get("/api/v1/environment/active")
    assert check_res.json()["environment"] == "REAL"
    assert check_res.json()["is_demo"] is False

    # Verify menu queries in REAL mode only return REAL items
    real_menus = await client.get("/api/v1/menus?outlet_id=1&environment=REAL")
    assert real_menus.status_code == 200
    real_items = real_menus.json()
    assert any("Real Verified" in item["name"] for item in real_items)
    assert not any("Demo" in item["name"] for item in real_items)

    # Revert back to DEMO for other tests
    await client.post(
        "/api/v1/environment/switch",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "target_environment": "DEMO",
            "reason": "Reverting back to DEMO mode",
            "confirm_acknowledgment": True,
        },
    )
