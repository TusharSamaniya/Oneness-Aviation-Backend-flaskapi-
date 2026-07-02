"""Tests for fleet endpoints."""
import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_list_fleet_empty(client):
    """Should return empty list when no aircraft in DB."""
    response = await client.get("/api/fleet")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_list_fleet_categories(client):
    response = await client.get("/api/fleet/categories")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_nonexistent_aircraft(client):
    response = await client.get("/api/fleet/does-not-exist")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_fleet_filter_by_category(client):
    response = await client.get("/api/fleet?category=light-jet")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_fleet_filter_by_passengers(client):
    response = await client.get("/api/fleet?passengers_min=8")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
