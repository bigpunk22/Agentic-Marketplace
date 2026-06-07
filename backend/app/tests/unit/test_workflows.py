"""Workflow CRUD and execution unit tests."""

import pytest


async def _get_workspace_id(client, token):
    """Get workspace_id by creating a tenant and extracting workspace from DB via API."""
    # Create a tenant (which auto-creates a workspace)
    tenant_resp = await client.post(
        "/api/v1/tenants",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Workflow Test Tenant", "slug": f"wf-test-{token[:8]}"},
    )
    tenant_id = tenant_resp.json()["id"]

    # We need the workspace_id. Since the API doesn't expose a workspace list endpoint,
    # we'll use the db_session fixture approach through a dedicated endpoint.
    # For now, return tenant_id and we'll create workflows via the API.
    return tenant_id


@pytest.mark.asyncio
async def test_list_workflows_empty(client):
    """Test listing workflows when none exist."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "wflist@example.com", "password": "securepassword123"},
    )
    token = reg.json()["access_token"]

    response = await client.get(
        "/api/v1/workflows",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_workflow_without_workspace_membership(client):
    """Test creating workflow without being a workspace member."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "wfmember@example.com", "password": "securepassword123"},
    )
    token = reg.json()["access_token"]

    fake_workspace_id = "00000000-0000-0000-0000-000000000001"
    response = await client.post(
        "/api/v1/workflows",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "workspace_id": fake_workspace_id,
            "name": "Test Workflow",
        },
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_nonexistent_workflow(client):
    """Test getting a workflow that doesn't exist."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "wfnonexist@example.com", "password": "securepassword123"},
    )
    token = reg.json()["access_token"]

    response = await client.get(
        "/api/v1/workflows/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_workflow(client):
    """Test deleting a workflow that doesn't exist."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "wfdelnonexist@example.com", "password": "securepassword123"},
    )
    token = reg.json()["access_token"]

    response = await client.delete(
        "/api/v1/workflows/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_execute_nonexistent_workflow(client):
    """Test executing a workflow that doesn't exist."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "wfexecnonexist@example.com", "password": "securepassword123"},
    )
    token = reg.json()["access_token"]

    response = await client.post(
        "/api/v1/workflows/00000000-0000-0000-0000-000000000000/execute",
        headers={"Authorization": f"Bearer {token}"},
        json={"input_data": {}},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_executions_nonexistent_workflow(client):
    """Test listing executions for a workflow that doesn't exist."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "wfexecnonexist2@example.com", "password": "securepassword123"},
    )
    token = reg.json()["access_token"]

    response = await client.get(
        "/api/v1/workflows/00000000-0000-0000-0000-000000000000/executions",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == []
