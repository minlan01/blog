from app.models.post import Post
from app.models.comment import Comment


def test_list_comments_empty(client, db_session):
    db = db_session
    post = Post(title="Test", slug="test", summary="s", content_markdown="c")
    db.add(post)
    db.commit()

    resp = client.get(f"/api/v1/comments?post_id={post.id}")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_comment(client, admin_token, db_session):
    db = db_session
    post = Post(title="Test", slug="test", summary="s", content_markdown="c")
    db.add(post)
    db.commit()

    resp = client.post("/api/v1/comments", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "content": "Nice post!",
        "post_id": post.id,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["content"] == "Nice post!"
    assert data["post_id"] == post.id
    assert data["is_approved"] is True


def test_create_comment_unauthenticated(client, db_session):
    db = db_session
    post = Post(title="Test", slug="test", summary="s", content_markdown="c")
    db.add(post)
    db.commit()

    resp = client.post("/api/v1/comments", json={
        "content": "No auth",
        "post_id": post.id,
    })
    assert resp.status_code == 401


def test_create_comment_nonexistent_post(client, admin_token):
    resp = client.post("/api/v1/comments", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "content": "Orphan comment",
        "post_id": 99999,
    })
    assert resp.status_code == 404


def test_create_nested_comment(client, admin_token, db_session):
    db = db_session
    post = Post(title="Test", slug="test", summary="s", content_markdown="c")
    db.add(post)
    db.commit()

    parent_resp = client.post("/api/v1/comments", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "content": "Parent comment",
        "post_id": post.id,
    })
    parent_id = parent_resp.json()["id"]

    child_resp = client.post("/api/v1/comments", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "content": "Child comment",
        "post_id": post.id,
        "parent_id": parent_id,
    })
    assert child_resp.status_code == 201
    assert child_resp.json()["parent_id"] == parent_id


def test_delete_own_comment(client, admin_token, db_session):
    db = db_session
    post = Post(title="Test", slug="test", summary="s", content_markdown="c")
    db.add(post)
    db.commit()

    create_resp = client.post("/api/v1/comments", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "content": "To delete",
        "post_id": post.id,
    })
    comment_id = create_resp.json()["id"]

    resp = client.delete(f"/api/v1/comments/{comment_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 204


def test_delete_comment_cascades_children(client, admin_token, db_session):
    db = db_session
    post = Post(title="Test", slug="test", summary="s", content_markdown="c")
    db.add(post)
    db.commit()

    parent_resp = client.post("/api/v1/comments", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "content": "Parent",
        "post_id": post.id,
    })
    parent_id = parent_resp.json()["id"]

    client.post("/api/v1/comments", headers={"Authorization": f"Bearer {admin_token}"}, json={
        "content": "Child",
        "post_id": post.id,
        "parent_id": parent_id,
    })

    resp = client.delete(f"/api/v1/comments/{parent_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 204

    remaining = db.query(Comment).filter(Comment.post_id == post.id).count()
    assert remaining == 0


def test_delete_comment_not_owner(client, db_session):
    db = db_session
    post = Post(title="Test", slug="test", summary="s", content_markdown="c")
    db.add(post)

    from app.core.security import hash_password
    from app.models.user import User
    other = User(username="otheruser", password_hash=hash_password("Otherpass1"), role="user")
    db.add(other)
    db.commit()

    from app.core.security import create_access_token
    other_token = create_access_token({"sub": str(other.id)})

    comment_resp = client.post("/api/v1/comments", headers={"Authorization": f"Bearer {other_token}"}, json={
        "content": "Other's comment",
        "post_id": post.id,
    })
    comment_id = comment_resp.json()["id"]

    from app.core.security import create_access_token
    reader_token = create_access_token({"sub": str(db.query(User).filter(User.username == "testreader").first().id)})
    resp = client.delete(f"/api/v1/comments/{comment_id}", headers={"Authorization": f"Bearer {reader_token}"})
    assert resp.status_code == 403
