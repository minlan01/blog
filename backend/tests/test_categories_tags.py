def test_list_categories_empty(client):
    resp = client.get("/api/v1/categories")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_category(client, admin_headers):
    resp = client.post("/api/v1/admin/categories", headers=admin_headers, json={
        "name": "Technology",
        "slug": "technology",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Technology"
    assert data["slug"] == "technology"


def test_create_category_invalid_slug(client, admin_headers):
    resp = client.post("/api/v1/admin/categories", headers=admin_headers, json={
        "name": "Bad Category",
        "slug": "bad slug!",
    })
    assert resp.status_code == 422


def test_list_categories_after_create(client, admin_headers):
    client.post("/api/v1/admin/categories", headers=admin_headers, json={
        "name": "Tech",
        "slug": "tech",
    })
    resp = client.get("/api/v1/categories")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["name"] == "Tech"


def test_update_category(client, admin_headers):
    create_resp = client.post("/api/v1/admin/categories", headers=admin_headers, json={
        "name": "Original",
        "slug": "original",
    })
    cat_id = create_resp.json()["id"]

    resp = client.put(f"/api/v1/admin/categories/{cat_id}", headers=admin_headers, json={
        "name": "Updated",
    })
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated"


def test_delete_category(client, admin_headers):
    create_resp = client.post("/api/v1/admin/categories", headers=admin_headers, json={
        "name": "ToDelete",
        "slug": "to-delete",
    })
    cat_id = create_resp.json()["id"]

    resp = client.delete(f"/api/v1/admin/categories/{cat_id}", headers=admin_headers)
    assert resp.status_code == 204

    list_resp = client.get("/api/v1/categories")
    assert len(list_resp.json()) == 0


def test_delete_category_nullifies_posts(client, admin_headers, db_session):
    db = db_session
    from app.models.category import Category
    from app.models.post import Post

    cat = Category(name="TempCat", slug="tempcat")
    db.add(cat)
    db.commit()

    post = Post(title="WithCat", slug="with-cat", summary="s", content_markdown="c", category_id=cat.id)
    db.add(post)
    db.commit()
    post_id = post.id

    resp = client.delete(f"/api/v1/admin/categories/{cat.id}", headers=admin_headers)
    assert resp.status_code == 204

    db.expire_all()
    updated_post = db.get(Post, post_id)
    assert updated_post.category_id is None


def test_list_tags_empty(client):
    resp = client.get("/api/v1/tags")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_tag(client, admin_headers):
    resp = client.post("/api/v1/admin/tags", headers=admin_headers, json={
        "name": "Python",
        "slug": "python",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Python"
    assert data["slug"] == "python"


def test_create_tag_invalid_slug(client, admin_headers):
    resp = client.post("/api/v1/admin/tags", headers=admin_headers, json={
        "name": "Bad Tag",
        "slug": "bad tag!",
    })
    assert resp.status_code == 422


def test_update_tag(client, admin_headers):
    create_resp = client.post("/api/v1/admin/tags", headers=admin_headers, json={
        "name": "Original",
        "slug": "original",
    })
    tag_id = create_resp.json()["id"]

    resp = client.put(f"/api/v1/admin/tags/{tag_id}", headers=admin_headers, json={
        "name": "Updated",
    })
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated"


def test_delete_tag(client, admin_headers):
    create_resp = client.post("/api/v1/admin/tags", headers=admin_headers, json={
        "name": "ToDelete",
        "slug": "to-delete",
    })
    tag_id = create_resp.json()["id"]

    resp = client.delete(f"/api/v1/admin/tags/{tag_id}", headers=admin_headers)
    assert resp.status_code == 204

    list_resp = client.get("/api/v1/tags")
    assert len(list_resp.json()) == 0
