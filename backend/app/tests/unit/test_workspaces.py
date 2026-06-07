"""Workspace unit tests."""

import pytest


async def _create_user_with_workspace(client, email: str):
    """Helper: register user + create tenant + create workspace, return (token, workspace_id)."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "securepassword123"},
    )
    token = reg.json()["access_token"]

    ws_resp = await client.post(
        "/api/v1/workspaces",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": f"Workspace for {email}", "description": "Test workspace"},
    )
    workspace_id = ws_resp.json()["id"]
    return token, workspace_id


@pytest.mark.asyncio
async def test_create_workspace(client):
    """Test creating a new workspace."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "wscreate@example.com", "password": "securepassword123"},
    )
    token = reg.json()["access_token"]

    response = await client.post(
        "/api/v1/workspaces",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "My Workspace", "description": "A test workspace"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Workspace"
    assert data["description"] == "A test workspace"
    assert "id" in data
    assert "tenant_id" in data


@pytest.mark.asyncio
async def test_list_workspaces(client):
    """Test listing workspaces for the current user."""
    token, workspace_id = await _create_user_with_workspace(client, "wslist@example.com")

    response = await client.get(
        "/api/v1/workspaces",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["id"] == workspace_id


@pytest.mark.asyncio
async def test_list_workspaces_empty(client):
    """Test listing workspaces when user has none."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "wsempty@example.com", "password": "securepassword123"},
    )
    token = reg.json()["access_token"]

    response = await client.get(
        "/api/v1/workspaces",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_workspace(client):
    """Test getting workspace details."""
    token, workspace_id = await _create_user_with_workspace(client, "wsget@example.com")

    response = await client.get(
        f"/api/v1/workspaces/{workspace_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == workspace_id
    assert data["name"] == "Workspace for wsget@example.com"


@pytest.mark.asyncio
async def test_get_workspace_not_member(client):
    """Test getting workspace details when not a member."""
    # Create user 1 with workspace
    token1, workspace_id = await _create_user_with_workspace(client, "wsnotmem1@example.com")

    # Create user 2
    reg2 = await client.post(
        "/api/v1/auth/register",
        json={"email": "wsnotmem2@example.com", "password": "securepassword123"},
    )
    token2 = reg2.json()["access_token"]

    # User 2 tries to access user 1's workspace
    response = await client.get(
        f"/api/v1/workspaces/{workspace_id}",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_invite_member(client):
    """Test inviting a user to a workspace."""
    token1, workspace_id = await _create_user_with_workspace(client, "wsinvite1@example.com")

    # Create user 2 to invite
    await client.post(
        "/api/v1/auth/register",
        json={"email": "wsinvite2@example.com", "password": "securepassword123"},
    )

    response = await client.post(
        f"/api/v1/workspaces/{workspace_id}/invite",
        headers={"Authorization": f"Bearer {token1}"},
        json={"email": "wsinvite2@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "invitation sent" in data["message"].lower()


@pytest.mark.asyncio
async def test_invite_member_not_found(client):
    """Test inviting a user that doesn't exist."""
    token, workspace_id = await _create_user_with_workspace(client, "wsnotfound1@example.com")

    response = await client.post(
        f"/api/v1/workspaces/{workspace_id}/invite",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "nonexistent@example.com"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_invite_duplicate_member(client):
    """Test inviting a user who is already a member."""
    token, workspace_id = await _create_user_with_workspace(client, "wsdup1@example.com")

    # Create and invite user 2
    await client.post(
        "/api/v1/auth/register",
        json={"email": "wsdup2@example.com", "password": "securepassword123"},
    )
    await client.post(
        f"/api/v1/workspaces/{workspace_id}/invite",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "wsdup2@example.com"},
    )

    # Try to invite again
    response = await client.post(
        f"/api/v1/workspaces/{workspace_id}/invite",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "wsdup2@example.com"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_remove_member(client):
    """Test removing a member from a workspace."""
    token1, workspace_id = await _create_user_with_workspace(client, "wsremove1@example.com")

    # Create and invite user 2
    reg2 = await client.post(
        "/api/v1/auth/register",
        json={"email": "wsremove2@example.com", "password": "securepassword123"},
    )
    user2_id = reg2.json()["user"]["id"]

    await client.post(
        f"/api/v1/workspaces/{workspace_id}/invite",
        headers={"Authorization": f"Bearer {token1}"},
        json={"email": "wsremove2@example.com"},
    )

    # Remove user 2
    response = await client.delete(
        f"/api/v1/workspaces/{workspace_id}/members/{user2_id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert response.status_code == 200
    assert "removed" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_remove_last_admin_fails(client):
    """Test that removing the last admin fails."""
    token, workspace_id = await _create_user_with_workspace(client, "wsadmin@example.com")

    # Get user ID
    me = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    user_id = me.json()["id"]

    # Try to remove yourself (the only admin)
    response = await client.delete(
        f"/api/v1/workspaces/{workspace_id}/members/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
