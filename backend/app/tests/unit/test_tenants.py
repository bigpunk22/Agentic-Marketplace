"""Tenant management unit tests."""

import pytest


@pytest.mark.asyncio
async def test_create_tenant(client):
    """Test creating a new tenant."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "tenant@example.com", "password": "securepassword123"},
    )
    token = reg.json()["access_token"]

    response = await client.post(
        "/api/v1/tenants",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "My Company", "slug": "my-company"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Company"
    assert data["slug"] == "my-company"
    assert data["plan"] == "free"
    assert data["status"] == "trialing"


@pytest.mark.asyncio
async def test_create_tenant_duplicate_slug(client):
    """Test creating tenant with duplicate slug."""
    reg1 = await client.post(
        "/api/v1/auth/register",
        json={"email": "dupslug1@example.com", "password": "securepassword123"},
    )
    token1 = reg1.json()["access_token"]

    await client.post(
        "/api/v1/tenants",
        headers={"Authorization": f"Bearer {token1}"},
        json={"name": "First", "slug": "duplicate-slug"},
    )

    reg2 = await client.post(
        "/api/v1/auth/register",
        json={"email": "dupslug2@example.com", "password": "securepassword123"},
    )
    token2 = reg2.json()["access_token"]

    response = await client.post(
        "/api/v1/tenants",
        headers={"Authorization": f"Bearer {token2}"},
        json={"name": "Second", "slug": "duplicate-slug"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_get_current_tenant(client):
    """Test getting current user's tenant."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "currenttenant@example.com", "password": "securepassword123"},
    )
    token = reg.json()["access_token"]

    tenant_resp = await client.post(
        "/api/v1/tenants",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Current Tenant Co", "slug": "current-tenant-co"},
    )
    tenant_id = tenant_resp.json()["id"]

    response = await client.get(
        "/api/v1/tenants/current",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == tenant_id


@pytest.mark.asyncio
async def test_tenant_usage(client):
    """Test getting tenant usage stats."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "usage@example.com", "password": "securepassword123"},
    )
    token = reg.json()["access_token"]

    tenant_resp = await client.post(
        "/api/v1/tenants",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Usage Tenant", "slug": "usage-tenant"},
    )
    tenant_id = tenant_resp.json()["id"]

    response = await client.get(
        f"/api/v1/tenants/{tenant_id}/usage",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tenant_id"] == tenant_id
    assert "executions_this_month" in data
