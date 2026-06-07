"""Marketplace publish and my-listings unit tests."""

import pytest


async def _create_user_with_workspace_and_workflow(client, email: str):
    """Helper: register user + create workspace + create workflow, return (token, workspace_id, workflow_id)."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "securepassword123"},
    )
    token = reg.json()["access_token"]

    ws_resp = await client.post(
        "/api/v1/workspaces",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": f"WS for {email}"},
    )
    workspace_id = ws_resp.json()["id"]

    wf_resp = await client.post(
        "/api/v1/workflows",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "workspace_id": workspace_id,
            "name": f"Workflow for {email}",
            "config": {"prompt": "Hello {name}", "model": "openai/gpt-4o-mini"},
        },
    )
    workflow_id = wf_resp.json()["id"]
    return token, workspace_id, workflow_id


@pytest.mark.asyncio
async def test_publish_workflow(client):
    """Test publishing a workflow."""
    token, workspace_id, workflow_id = await _create_user_with_workspace_and_workflow(
        client, "wfpublish@example.com"
    )

    response = await client.post(
        f"/api/v1/workflows/{workflow_id}/publish",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_published"] is True
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_publish_workflow_not_found(client):
    """Test publishing a nonexistent workflow."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "wfpublish404@example.com", "password": "securepassword123"},
    )
    token = reg.json()["access_token"]

    response = await client.post(
        "/api/v1/workflows/00000000-0000-0000-0000-000000000000/publish",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_marketplace_listing(client):
    """Test creating a marketplace listing from a workflow."""
    token, workspace_id, workflow_id = await _create_user_with_workspace_and_workflow(
        client, "mplisting@example.com"
    )

    # Publish the workflow first
    await client.post(
        f"/api/v1/workflows/{workflow_id}/publish",
        headers={"Authorization": f"Bearer {token}"},
    )

    response = await client.post(
        "/api/v1/marketplace/listings",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "workflow_id": workflow_id,
            "title": "My AI Email Assistant",
            "description": "Automatically responds to emails using AI",
            "price_type": "one_time",
            "price": 29.99,
            "category": "Productivity",
            "tags": ["email", "ai", "automation"],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My AI Email Assistant"
    assert data["price_type"] == "one_time"
    assert data["price"] == 29.99
    assert data["status"] == "pending_review"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_listing_workflow_not_found(client):
    """Test creating a listing for a nonexistent workflow."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "mplisting404@example.com", "password": "securepassword123"},
    )
    token = reg.json()["access_token"]

    response = await client.post(
        "/api/v1/marketplace/listings",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "workflow_id": "00000000-0000-0000-0000-000000000000",
            "title": "Ghost Workflow",
            "price_type": "free",
            "price": 0,
        },
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_my_listings(client):
    """Test listing the current user's marketplace listings."""
    token, workspace_id, workflow_id = await _create_user_with_workspace_and_workflow(
        client, "mpmylist@example.com"
    )

    # Publish and create listing
    await client.post(
        f"/api/v1/workflows/{workflow_id}/publish",
        headers={"Authorization": f"Bearer {token}"},
    )
    await client.post(
        "/api/v1/marketplace/listings",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "workflow_id": workflow_id,
            "title": "My Listed Workflow",
            "price_type": "free",
            "price": 0,
        },
    )

    response = await client.get(
        "/api/v1/marketplace/my-listings",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["title"] == "My Listed Workflow"


@pytest.mark.asyncio
async def test_my_listings_empty(client):
    """Test listing marketplace listings when user has none."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "mpmylistempty@example.com", "password": "securepassword123"},
    )
    token = reg.json()["access_token"]

    response = await client.get(
        "/api/v1/marketplace/my-listings",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == []
