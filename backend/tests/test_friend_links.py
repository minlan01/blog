def test_list_friend_links_empty(client):
    resp = client.get("/api/v1/friend-links")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_friend_link(client, admin_headers):
    resp = client.post("/api/v1/admin/friend-links", headers=admin_headers, json={
        "name": "Test Link",
        "url": "https://example.com",
        "description": "A test link",
        "category": "test",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Test Link"
    assert data["url"] == "https://example.com"


def test_list_friend_links_after_create(client, admin_headers):
    client.post("/api/v1/admin/friend-links", headers=admin_headers, json={
        "name": "Visible Link",
        "url": "https://example.com",
        "category": "test",
        "is_active": True,
    })
    resp = client.get("/api/v1/friend-links")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["name"] == "Visible Link"


def test_update_friend_link(client, admin_headers):
    create_resp = client.post("/api/v1/admin/friend-links", headers=admin_headers, json={
        "name": "Original",
        "url": "https://example.com",
        "category": "test",
    })
    link_id = create_resp.json()["id"]

    resp = client.put(f"/api/v1/admin/friend-links/{link_id}", headers=admin_headers, json={
        "name": "Updated",
    })
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated"


def test_delete_friend_link(client, admin_headers):
    create_resp = client.post("/api/v1/admin/friend-links", headers=admin_headers, json={
        "name": "To Delete",
        "url": "https://example.com",
        "category": "test",
    })
    link_id = create_resp.json()["id"]

    resp = client.delete(f"/api/v1/admin/friend-links/{link_id}", headers=admin_headers)
    assert resp.status_code == 200

    # Verify deleted
    list_resp = client.get("/api/v1/friend-links")
    assert len(list_resp.json()) == 0


def test_inactive_friend_link_hidden(client, admin_headers):
    client.post("/api/v1/admin/friend-links", headers=admin_headers, json={
        "name": "Inactive Link",
        "url": "https://example.com",
        "category": "test",
        "is_active": False,
    })
    resp = client.get("/api/v1/friend-links")
    assert resp.status_code == 200
    assert len(resp.json()) == 0


def test_create_friend_link_unauthorized(client):
    resp = client.post("/api/v1/admin/friend-links", json={
        "name": "No auth",
        "url": "https://example.com",
    })
    assert resp.status_code == 401


def test_stats_includes_counts(client):
    resp = client.get("/api/v1/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "posts" in data
    assert "total_views" in data
    assert "total_words" in data
    assert "friend_links" in data
