"""Tests for authentication endpoints."""
import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    response = await client.post("/api/auth/register", json={
        "name": "Tushar Samaniya",
        "email": "tushar@test.com",
        "phone": "+91 99999 00001",
        "password": "SecurePass@123",
    })
    assert response.status_code == 201
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    payload = {"name": "A", "email": "dup@test.com", "phone": "+91 11111 11111", "password": "Pass@1234"}
    await client.post("/api/auth/register", json=payload)
    response = await client.post("/api/auth/register", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/api/auth/register", json={
        "name": "Login Test",
        "email": "login@test.com",
        "phone": "+91 99999 00002",
        "password": "LoginPass@1",
    })
    response = await client.post("/api/auth/login", json={
        "email": "login@test.com",
        "password": "LoginPass@1",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["email"] == "login@test.com"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/api/auth/register", json={
        "name": "Wrong Pass",
        "email": "wrong@test.com",
        "phone": "+91 99999 00003",
        "password": "CorrectPass@1",
    })
    response = await client.post("/api/auth/login", json={
        "email": "wrong@test.com",
        "password": "WrongPassword",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_profile_authenticated(client, auth_headers):
    response = await client.get("/api/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_get_profile_unauthenticated(client):
    response = await client.get("/api/users/me")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_forgot_password_always_200(client):
    """Should return 200 even for non-existent email (security: don't reveal emails)."""
    response = await client.post("/api/auth/forgot-password", json={"email": "nonexistent@test.com"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_token_refresh(client):
    await client.post("/api/auth/register", json={
        "name": "Refresh User",
        "email": "refresh@test.com",
        "phone": "+91 99999 00004",
        "password": "RefreshPass@1",
    })
    login_resp = await client.post("/api/auth/login", json={
        "email": "refresh@test.com",
        "password": "RefreshPass@1",
    })
    refresh_token = login_resp.json()["refresh_token"]
    response = await client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()
