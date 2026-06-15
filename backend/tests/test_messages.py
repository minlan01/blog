import hashlib
import random
import time

from app.core.config import settings


def _get_valid_captcha(client):
    resp = client.get("/api/v1/messages/captcha")
    assert resp.status_code == 200
    data = resp.json()
    return data


def _solve_captcha(question: str) -> int:
    parts = question.replace("=", "").replace("?", "").strip().split("+")
    return int(parts[0].strip()) + int(parts[1].strip())


def test_get_captcha(client):
    resp = client.get("/api/v1/messages/captcha")
    assert resp.status_code == 200
    data = resp.json()
    assert "question" in data
    assert "token" in data
    assert "ts" in data


def test_list_messages_empty(client):
    resp = client.get("/api/v1/messages")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_message_with_captcha(client):
    captcha = _get_valid_captcha(client)
    answer = _solve_captcha(captcha["question"])

    resp = client.post("/api/v1/messages", json={
        "name": "Visitor",
        "content": "Hello!",
        "captcha_answer": answer,
        "captcha_token": captcha["token"],
        "captcha_ts": captcha["ts"],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Visitor"
    assert data["content"] == "Hello!"


def test_create_message_wrong_captcha(client):
    captcha = _get_valid_captcha(client)

    resp = client.post("/api/v1/messages", json={
        "name": "Spammer",
        "content": "Spam!",
        "captcha_answer": 99999,
        "captcha_token": captcha["token"],
        "captcha_ts": captcha["ts"],
    })
    assert resp.status_code == 400


def test_create_message_no_captcha(client):
    resp = client.post("/api/v1/messages", json={
        "name": "NoCaptcha",
        "content": "Skip captcha",
    })
    assert resp.status_code == 400


def test_create_message_expired_captcha(client):
    old_ts = int(time.time()) - 601
    a, b = 5, 3
    raw = f"{a}+{b}:{old_ts}:{settings.SECRET_KEY}"
    fake_token = hashlib.sha256(raw.encode()).hexdigest()[:16]

    resp = client.post("/api/v1/messages", json={
        "name": "Expired",
        "content": "Old captcha",
        "captcha_answer": a + b,
        "captcha_token": fake_token,
        "captcha_ts": old_ts,
    })
    assert resp.status_code == 400


def test_create_reply_message(client):
    captcha = _get_valid_captcha(client)
    answer = _solve_captcha(captcha["question"])

    parent_resp = client.post("/api/v1/messages", json={
        "name": "Parent",
        "content": "Original message",
        "captcha_answer": answer,
        "captcha_token": captcha["token"],
        "captcha_ts": captcha["ts"],
    })
    parent_id = parent_resp.json()["id"]

    captcha2 = _get_valid_captcha(client)
    answer2 = _solve_captcha(captcha2["question"])

    reply_resp = client.post("/api/v1/messages", json={
        "name": "Replier",
        "content": "Reply message",
        "parent_id": parent_id,
        "captcha_answer": answer2,
        "captcha_token": captcha2["token"],
        "captcha_ts": captcha2["ts"],
    })
    assert reply_resp.status_code == 201
    assert reply_resp.json()["parent_id"] == parent_id


def test_delete_message_admin(client, admin_token, db_session):
    db = db_session
    from app.models.message import Message
    msg = Message(name="ToDelete", content="bye", color="#818cf8")
    db.add(msg)
    db.commit()
    msg_id = msg.id

    resp = client.delete(f"/api/v1/messages/{msg_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 204


def test_delete_message_non_admin(client, db_session):
    db = db_session
    from app.models.message import Message
    msg = Message(name="Protected", content="can't delete", color="#818cf8")
    db.add(msg)
    db.commit()

    from app.core.security import create_access_token
    from app.models.user import User
    reader = db.query(User).filter(User.username == "testreader").first()
    reader_token = create_access_token({"sub": str(reader.id)})

    resp = client.delete(f"/api/v1/messages/{msg.id}", headers={"Authorization": f"Bearer {reader_token}"})
    assert resp.status_code == 403
