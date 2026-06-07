"""Authentication unit tests."""

import pytest


@pytest.mark.asyncio
async def test_register(client):
    """Test user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    """Test registration with duplicate email."""
    # First registration
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "securepassword123",
        },
    )
    # Duplicate
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "securepassword123",
        },
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login(client):
    """Test user login."""
    # Register first
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "securepassword123",
        },
    )
    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "securepassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    """Test login with wrong password."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client):
    """Test getting current user profile."""
    # Register and get token
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "me@example.com",
            "password": "securepassword123",
        },
    )
    token = reg.json()["access_token"]

    # Get profile
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


@pytest.mark.asyncio
async def test_refresh_token(client):
    """Test token refresh."""
    # Register
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "refresh@example.com",
            "password": "securepassword123",
        },
    )
    refresh_token = reg.json()["refresh_token"]

    # Refresh
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
