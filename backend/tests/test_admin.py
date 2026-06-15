from app.models.post import Post
from app.models.comment import Comment
from app.models.user import User
from app.core.security import create_access_token


def test_list_users(client, admin_headers):
    resp = client.get("/api/v1/admin/users", headers=admin_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


def test_update_user_role(client, admin_headers, db_session):
    db = db_session
    reader = db.query(User).filter(User.username == "testreader").first()

    resp = client.put(f"/api/v1/admin/users/{reader.id}", headers=admin_headers, json={
        "role": "super_admin",
    })
    assert resp.status_code == 200
    assert resp.json()["role"] == "super_admin"


def test_update_user_writable_fields_only(client, admin_headers, db_session):
    db = db_session
    reader = db.query(User).filter(User.username == "testreader").first()

    resp = client.put(f"/api/v1/admin/users/{reader.id}", headers=admin_headers, json={
        "bio": "New bio",
        "username": "hacked",
    })
    assert resp.status_code == 200
    assert resp.json()["bio"] == "New bio"

    db.expire_all()
    same_reader = db.get(User, reader.id)
    assert same_reader.username == "testreader"


def test_delete_user(client, admin_headers, db_session):
    db = db_session
    from app.core.security import hash_password
    victim = User(username="victim", password_hash=hash_password("Victim123"), role="user")
    db.add(victim)
    db.commit()
    victim_id = victim.id

    resp = client.delete(f"/api/v1/admin/users/{victim_id}", headers=admin_headers)
    assert resp.status_code == 204
    db.expire_all()
    assert db.get(User, victim_id) is None


def test_delete_self_forbidden(client, admin_headers, db_session):
    db = db_session
    admin = db.query(User).filter(User.username == "testadmin").first()

    resp = client.delete(f"/api/v1/admin/users/{admin.id}", headers=admin_headers)
    assert resp.status_code == 400


def test_delete_user_nullifies_comments(client, admin_headers, db_session):
    db = db_session
    from app.core.security import hash_password
    commenter = User(username="commenter", password_hash=hash_password("Comment123"), role="user")
    db.add(commenter)
    db.flush()

    post = Post(title="Test", slug="test", summary="s", content_markdown="c")
    db.add(post)
    db.flush()

    comment = Comment(content="My comment", post_id=post.id, user_id=commenter.id)
    db.add(comment)
    db.commit()
    comment_id = comment.id

    resp = client.delete(f"/api/v1/admin/users/{commenter.id}", headers=admin_headers)
    assert resp.status_code == 204

    db.expire_all()
    orphan_comment = db.get(Comment, comment_id)
    assert orphan_comment is not None
    assert orphan_comment.user_id is None


def test_admin_list_comments(client, admin_headers, db_session):
    db = db_session
    post = Post(title="Test", slug="test", summary="s", content_markdown="c")
    db.add(post)
    db.flush()

    admin = db.query(User).filter(User.username == "testadmin").first()
    comment = Comment(content="Test comment", post_id=post.id, user_id=admin.id)
    db.add(comment)
    db.commit()

    resp = client.get("/api/v1/admin/comments", headers=admin_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_admin_approve_comment(client, admin_headers, db_session):
    db = db_session
    post = Post(title="Test", slug="test", summary="s", content_markdown="c")
    db.add(post)
    db.flush()

    comment = Comment(content="Pending", post_id=post.id, is_approved=False)
    db.add(comment)
    db.commit()
    comment_id = comment.id

    resp = client.put(f"/api/v1/admin/comments/{comment_id}/approve", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["is_approved"] is True


def test_admin_delete_comment_cascades(client, admin_headers, db_session):
    db = db_session
    post = Post(title="Test", slug="test", summary="s", content_markdown="c")
    db.add(post)
    db.flush()

    parent = Comment(content="Parent", post_id=post.id)
    db.add(parent)
    db.flush()

    child = Comment(content="Child", post_id=post.id, parent_id=parent.id)
    db.add(child)
    db.commit()
    parent_id = parent.id
    child_id = child.id

    resp = client.delete(f"/api/v1/admin/comments/{parent_id}", headers=admin_headers)
    assert resp.status_code == 204

    db.expire_all()
    assert db.get(Comment, child_id) is None
    assert db.get(Comment, parent_id) is None


def test_batch_approve_comments(client, admin_headers, db_session):
    db = db_session
    post = Post(title="Test", slug="test", summary="s", content_markdown="c")
    db.add(post)
    db.flush()

    c1 = Comment(content="C1", post_id=post.id, is_approved=False)
    c2 = Comment(content="C2", post_id=post.id, is_approved=False)
    db.add_all([c1, c2])
    db.commit()

    resp = client.post("/api/v1/admin/comments/batch-action", headers=admin_headers, json={
        "ids": [c1.id, c2.id],
        "action": "approve",
    })
    assert resp.status_code == 200

    db.expire_all()
    assert db.get(Comment, c1.id).is_approved is True
    assert db.get(Comment, c2.id).is_approved is True


def test_batch_delete_comments_cascades(client, admin_headers, db_session):
    db = db_session
    post = Post(title="Test", slug="test", summary="s", content_markdown="c")
    db.add(post)
    db.flush()

    parent = Comment(content="P", post_id=post.id)
    db.add(parent)
    db.flush()

    child = Comment(content="Ch", post_id=post.id, parent_id=parent.id)
    db.add(child)
    db.commit()
    child_id = child.id

    resp = client.post("/api/v1/admin/comments/batch-action", headers=admin_headers, json={
        "ids": [parent.id],
        "action": "delete",
    })
    assert resp.status_code == 200
    db.expire_all()
    assert db.get(Comment, child_id) is None


def test_admin_reply_message(client, admin_headers, db_session):
    db = db_session
    from app.models.message import Message
    msg = Message(name="User", content="Hello admin", color="#818cf8")
    db.add(msg)
    db.commit()

    resp = client.put(f"/api/v1/admin/messages/{msg.id}/reply", headers=admin_headers, json={
        "content": "Admin reply here",
    })
    assert resp.status_code == 200
    assert resp.json()["admin_reply"] == "Admin reply here"


def test_admin_delete_message(client, admin_headers, db_session):
    db = db_session
    from app.models.message import Message
    msg = Message(name="ToDelete", content="bye", color="#818cf8")
    db.add(msg)
    db.commit()

    resp = client.delete(f"/api/v1/admin/messages/{msg.id}", headers=admin_headers)
    assert resp.status_code == 204


def test_update_site_profile(client, admin_headers):
    resp = client.put("/api/v1/admin/site/profile", headers=admin_headers, json={
        "site_name": "Updated Blog",
    })
    assert resp.status_code == 200
    assert resp.json()["site_name"] == "Updated Blog"


def test_update_site_profile_writable_fields_only(client, admin_headers, db_session):
    resp = client.put("/api/v1/admin/site/profile", headers=admin_headers, json={
        "site_name": "Safe Update",
        "id": 99999,
    })
    assert resp.status_code == 200
    assert resp.json()["site_name"] == "Safe Update"

    from app.models.site_config import SiteConfig
    db_session.expire_all()
    site = db_session.query(SiteConfig).first()
    assert site.id != 99999


def test_create_post_with_invalid_category(client, admin_headers):
    resp = client.post("/api/v1/admin/posts", headers=admin_headers, json={
        "title": "Bad Category",
        "slug": "bad-cat",
        "summary": "test",
        "content_markdown": "test",
        "category_id": 99999,
    })
    assert resp.status_code == 400


def test_create_post_duplicate_slug(client, admin_headers, db_session):
    db = db_session
    post = Post(title="Existing", slug="existing-slug", summary="s", content_markdown="c")
    db.add(post)
    db.commit()

    resp = client.post("/api/v1/admin/posts", headers=admin_headers, json={
        "title": "Duplicate",
        "slug": "existing-slug",
        "summary": "test",
        "content_markdown": "test",
    })
    assert resp.status_code == 409


def test_batch_delete_posts(client, admin_headers, db_session):
    db = db_session
    p1 = Post(title="P1", slug="p1", summary="s", content_markdown="c")
    p2 = Post(title="P2", slug="p2", summary="s", content_markdown="c")
    db.add_all([p1, p2])
    db.commit()

    resp = client.post("/api/v1/admin/posts/batch-delete", headers=admin_headers, json={
        "ids": [p1.id, p2.id],
    })
    assert resp.status_code == 204
    p1_id, p2_id = p1.id, p2.id
    db.expire_all()
    assert db.get(Post, p1_id) is None
    assert db.get(Post, p2_id) is None


def test_reject_comment_cascades(client, admin_headers, db_session):
    db = db_session
    post = Post(title="Test", slug="test", summary="s", content_markdown="c")
    db.add(post)
    db.flush()

    parent = Comment(content="Reject me", post_id=post.id, is_approved=False)
    db.add(parent)
    db.flush()

    child = Comment(content="Child of rejected", post_id=post.id, parent_id=parent.id)
    db.add(child)
    db.commit()
    child_id = child.id

    resp = client.put(f"/api/v1/admin/comments/{parent.id}/reject", headers=admin_headers)
    assert resp.status_code == 200

    db.expire_all()
    assert db.get(Comment, child_id) is None
