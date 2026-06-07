"""Billing and subscription unit tests."""

import pytest


async def _create_user_with_tenant(client, email: str):
    """Helper: register user + create tenant, return (token, tenant_id)."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "securepassword123"},
    )
    token = reg.json()["access_token"]

    tenant_resp = await client.post(
        "/api/v1/tenants",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": f"Tenant {email}", "slug": email.replace("@", "-").replace(".", "-")},
    )
    tenant_id = tenant_resp.json()["id"]
    return token, tenant_id


@pytest.mark.asyncio
async def test_get_subscription(client):
    """Test getting current subscription."""
    token, tenant_id = await _create_user_with_tenant(client, "sub@example.com")

    response = await client.get(
        "/api/v1/billing/subscription",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["plan"] == "free"
    assert data["status"] == "trialing"


@pytest.mark.asyncio
async def test_upgrade_subscription(client):
    """Test upgrading subscription plan."""
    token, tenant_id = await _create_user_with_tenant(client, "upgrade@example.com")

    response = await client.post(
        "/api/v1/billing/subscription/upgrade",
        headers={"Authorization": f"Bearer {token}"},
        json={"plan": "pro"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["plan"] == "pro"

    # Verify it persisted
    sub_resp = await client.get(
        "/api/v1/billing/subscription",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert sub_resp.json()["plan"] == "pro"


@pytest.mark.asyncio
async def test_upgrade_invalid_plan(client):
    """Test upgrading to an invalid plan."""
    token, tenant_id = await _create_user_with_tenant(client, "invalidplan@example.com")

    response = await client.post(
        "/api/v1/billing/subscription/upgrade",
        headers={"Authorization": f"Bearer {token}"},
        json={"plan": "nonexistent"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_list_invoices(client):
    """Test listing invoices/transactions."""
    token, tenant_id = await _create_user_with_tenant(client, "invoices@example.com")

    response = await client.get(
        "/api/v1/billing/invoices",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_usage(client):
    """Test getting usage breakdown."""
    token, tenant_id = await _create_user_with_tenant(client, "usage@example.com")

    response = await client.get(
        "/api/v1/billing/usage",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "tenant_id" in data
    assert "daily_usage" in data
