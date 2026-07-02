"""Tests for enquiry and charter request endpoints."""
import pytest


@pytest.mark.asyncio
async def test_submit_contact_enquiry(client):
    response = await client.post("/api/enquiries/contact", json={
        "name": "Raj Sharma",
        "phone": "+91 98765 00000",
        "email": "raj@test.com",
        "enquiry_type": "Private charter flight",
        "departure": "Delhi",
        "destination": "Mumbai",
        "travel_date": "2025-03-15",
        "passengers": "4",
        "message": "Need a light jet for a business trip.",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "raj@test.com"
    assert data["status"] == "new"


@pytest.mark.asyncio
async def test_submit_contact_enquiry_missing_required(client):
    response = await client.post("/api/enquiries/contact", json={
        "name": "No Email",
        "phone": "+91 00000 00000",
        # email is missing — required field
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_submit_charter_request(client):
    response = await client.post("/api/enquiries/charter", json={
        "name": "Priya Patel",
        "email": "priya@test.com",
        "phone": "+91 88888 00001",
        "service": "Private charter flight",
        "journey_type": "One Way",
        "from_city": "Mumbai",
        "to_city": "Goa",
        "departure_date": "2025-04-01",
        "passengers": "6",
        "aircraft_preference": "Light Jet",
        "message": "Preferably morning slot.",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["from_city"] == "Mumbai"
    assert data["to_city"] == "Goa"


@pytest.mark.asyncio
async def test_my_enquiries_unauthenticated(client):
    """Guest user should get empty lists, not 401."""
    response = await client.get("/api/enquiries/my")
    assert response.status_code == 200
    data = response.json()
    assert "enquiries" in data
    assert "charter_requests" in data


@pytest.mark.asyncio
async def test_my_enquiries_authenticated(client, auth_headers):
    # Submit an enquiry as logged-in user
    await client.post("/api/enquiries/contact", json={
        "name": "Auth User",
        "phone": "+91 77777 00001",
        "email": "test@example.com",
        "enquiry_type": "Membership enquiry",
    }, headers=auth_headers)

    response = await client.get("/api/enquiries/my", headers=auth_headers)
    assert response.status_code == 200
