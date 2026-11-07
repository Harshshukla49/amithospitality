import pytest

@pytest.mark.asyncio
async def test_create_reservation_request(client):
    res = await client.post(
        "/api/v1/reservations",
        json={
            "outlet_id": 1,
            "guest_name": "Rohan Mehra",
            "guest_phone": "+91 98200 11223",
            "guest_email": "rohan@example.com",
            "guest_count": 4,
            "reservation_date": "2026-11-12",
            "reservation_time": "20:00",
            "seating_preference": "ROOFTOP",
            "special_requests": "Birthday dinner",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["guest_name"] == "Rohan Mehra"
    assert data["status"] == "NEW"
    assert data["environment"] == "DEMO"
    assert data["guest_count"] == 4

@pytest.mark.asyncio
async def test_staff_update_reservation_status(client, staff_token):
    create_res = await client.post(
        "/api/v1/reservations",
        json={
            "outlet_id": 1,
            "guest_name": "Meera Kapoor",
            "guest_phone": "+91 98111 22334",
            "guest_count": 2,
            "reservation_date": "2026-11-15",
            "reservation_time": "19:30",
            "seating_preference": "INDOOR",
        },
    )
    res_id = create_res.json()["id"]

    update_res = await client.patch(
        f"/api/v1/reservations/{res_id}/status",
        headers={"Authorization": f"Bearer {staff_token}"},
        json={
            "status": "ACCEPTED",
            "internal_notes": "Table 14 allocated by Hostess Priya",
        },
    )
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["status"] == "ACCEPTED"
    assert "Table 14" in data["internal_notes"]

@pytest.mark.asyncio
async def test_export_reservations_csv(client, admin_token):
    res = await client.get(
        "/api/v1/reservations/export",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "Guest Name" in res.text
