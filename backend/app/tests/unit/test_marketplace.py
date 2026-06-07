"""Marketplace unit tests."""

import pytest


async def _setup_user_with_workspace(client, email: str):
    """Helper: register user + create tenant, return (token, tenant_id, workspace_id)."""
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

    # Get workspace_id via the db_session fixture through a test helper
    # For now, we skip workspace-dependent tests since the API doesn't expose workspace listing
    workspace_id = None

    return token, tenant_id, workspace_id


@pytest.mark.asyncio
async def test_browse_listings_empty(client):
    """Test browsing marketplace with no listings."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "browse@example.com", "password": "securepassword123"},
    )
    token = reg.json()["access_token"]

    response = await client.get(
        "/api/v1/marketplace/listings",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_browse_listings_with_sort(client):
    """Test browsing listings with different sort options."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "browsesort@example.com", "password": "securepassword123"},
    )
    token = reg.json()["access_token"]

    for sort in ["popular", "newest", "top_rated", "price_asc", "price_desc"]:
        response = await client.get(
            f"/api/v1/marketplace/listings?sort={sort}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_nonexistent_listing(client):
    """Test getting a listing that doesn't exist."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "nolisting@example.com", "password": "securepassword123"},
    )
    token = reg.json()["access_token"]

    response = await client.get(
        "/api/v1/marketplace/listings/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_categories_empty(client):
    """Test getting categories when none exist."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "cats@example.com", "password": "securepassword123"},
    )
    token = reg.json()["access_token"]

    response = await client.get(
        "/api/v1/marketplace/categories",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_featured_empty(client):
    """Test getting featured listings when none exist."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "featured@example.com", "password": "securepassword123"},
    )
    token = reg.json()["access_token"]

    response = await client.get(
        "/api/v1/marketplace/featured",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == []
