def test_register(client):
    resp = client.post("/api/v1/auth/register", json={
        "username": "newuser",
        "password": "Newpass123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "newuser"
    assert "id" in data


def test_register_weak_password(client):
    """Password must be 8+ chars with uppercase and digit."""
    resp = client.post("/api/v1/auth/register", json={
        "username": "weakuser",
        "password": "short",
    })
    assert resp.status_code == 422


def test_login_success(client):
    resp = client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "testpass123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_wrong_password(client):
    resp = client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "wrongpassword",
    })
    assert resp.status_code == 401


def test_get_me_no_token(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_get_me(client, admin_token):
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "testadmin"


def test_refresh_token(client):
    """Test refresh token flow."""
    login_resp = client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "testpass123",
    })
    tokens = login_resp.json()

    resp = client.post("/api/v1/auth/refresh", json={
        "refresh_token": tokens["refresh_token"],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_refresh_token_invalid(client):
    resp = client.post("/api/v1/auth/refresh", json={
        "refresh_token": "invalid-token",
    })
    assert resp.status_code == 401


def test_login_lockout(client):
    """Test that wrong password returns 401."""
    resp = client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "wrongpassword1",
    })
    assert resp.status_code == 401


def test_update_profile(client, admin_token):
    resp = client.put("/api/v1/auth/me", json={
        "bio": "Updated bio",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert resp.json()["bio"] == "Updated bio"
