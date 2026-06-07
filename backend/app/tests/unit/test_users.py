"""User management unit tests."""

import pytest


@pytest.mark.asyncio
async def test_get_current_user_profile(client):
    """Test getting current user profile."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "profile@example.com",
            "password": "securepassword123",
            "full_name": "Profile User",
        },
    )
    token = reg.json()["access_token"]

    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "profile@example.com"
    assert data["full_name"] == "Profile User"


@pytest.mark.asyncio
async def test_update_profile(client):
    """Test updating user profile."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "update@example.com",
            "password": "securepassword123",
            "full_name": "Original Name",
        },
    )
    token = reg.json()["access_token"]

    response = await client.patch(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Updated Name"},
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"


@pytest.mark.asyncio
async def test_get_user_by_id(client):
    """Test getting a user by ID."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "getuser@example.com",
            "password": "securepassword123",
        },
    )
    user_id = reg.json()["user"]["id"]
    token = reg.json()["access_token"]

    response = await client.get(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == user_id


@pytest.mark.asyncio
async def test_get_nonexistent_user(client):
    """Test getting a user that doesn't exist."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "nonexist@example.com",
            "password": "securepassword123",
        },
    )
    token = reg.json()["access_token"]

    response = await client.get(
        "/api/v1/users/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
