from app.models.post import Post
from app.models.category import Category


def test_list_posts(client):
    resp = client.get("/api/v1/posts")
    assert resp.status_code == 200


def test_create_post(client, admin_headers, db_session):
    db = db_session
    cat = Category(name="TestCat", slug="testcat")
    db.add(cat)
    db.commit()

    resp = client.post("/api/v1/admin/posts", headers=admin_headers, json={
        "title": "Test Post",
        "slug": "test-post",
        "summary": "A test post",
        "content_markdown": "# Hello",
        "is_featured": True,
        "category_id": cat.id,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test Post"
    assert data["slug"] == "test-post"


def test_get_post_increments_view(client, db_session):
    db = db_session
    post = Post(
        title="Existing Post",
        slug="existing-post",
        summary="Summary",
        content_markdown="Content",
        view_count=0,
    )
    db.add(post)
    db.commit()

    resp = client.get("/api/v1/posts/existing-post")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Existing Post"
    assert resp.json()["view_count"] == 1


def test_delete_post(client, admin_headers, db_session):
    db = db_session
    post = Post(
        title="To Delete",
        slug="to-delete",
        summary="Summary",
        content_markdown="Content",
    )
    db.add(post)
    db.commit()
    post_id = post.id

    resp = client.delete(f"/api/v1/admin/posts/{post_id}", headers=admin_headers)
    assert resp.status_code == 204


def test_create_post_unauthorized(client):
    resp = client.post("/api/v1/admin/posts", json={
        "title": "No auth",
        "slug": "no-auth",
        "summary": "test",
        "content_markdown": "test",
    })
    assert resp.status_code in (401, 403)
