import io
import os
import tempfile


def _make_png_bytes():
    return b'\x89PNG\r\n\x1a\n' + b'\x00' * 100


def _make_jpeg_bytes():
    return b'\xff\xd8\xff\xe0' + b'\x00' * 100


def _make_svg_bytes(content: str):
    return content.encode("utf-8")


def test_upload_png(client, admin_headers):
    resp = client.post(
        "/api/v1/upload",
        headers=admin_headers,
        files={"file": ("test.png", io.BytesIO(_make_png_bytes()), "image/png")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert "url" in data


def test_upload_requires_auth(client):
    resp = client.post(
        "/api/v1/upload",
        files={"file": ("test.png", io.BytesIO(_make_png_bytes()), "image/png")},
    )
    assert resp.status_code in (401, 403)


def test_upload_rejects_wrong_mime(client, admin_headers):
    resp = client.post(
        "/api/v1/upload",
        headers=admin_headers,
        files={"file": ("test.png", io.BytesIO(b'not an image'), "image/png")},
    )
    assert resp.status_code == 415


def test_upload_rejects_disallowed_type(client, admin_headers):
    resp = client.post(
        "/api/v1/upload",
        headers=admin_headers,
        files={"file": ("test.txt", io.BytesIO(b'hello'), "text/plain")},
    )
    assert resp.status_code == 415


def test_upload_svg_clean(client, admin_headers):
    svg = '<svg xmlns="http://www.w3.org/2000/svg"><rect width="10" height="10"/></svg>'
    resp = client.post(
        "/api/v1/upload",
        headers=admin_headers,
        files={"file": ("clean.svg", io.BytesIO(_make_svg_bytes(svg)), "image/svg+xml")},
    )
    assert resp.status_code == 200


def test_upload_svg_with_script_rejected(client, admin_headers):
    svg = '<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'
    resp = client.post(
        "/api/v1/upload",
        headers=admin_headers,
        files={"file": ("evil.svg", io.BytesIO(_make_svg_bytes(svg)), "image/svg+xml")},
    )
    assert resp.status_code == 415


def test_upload_svg_with_onerror_rejected(client, admin_headers):
    svg = '<svg xmlns="http://www.w3.org/2000/svg"><img onerror="alert(1)"/></svg>'
    resp = client.post(
        "/api/v1/upload",
        headers=admin_headers,
        files={"file": ("evil2.svg", io.BytesIO(_make_svg_bytes(svg)), "image/svg+xml")},
    )
    assert resp.status_code == 415


def test_upload_svg_with_iframe_rejected(client, admin_headers):
    svg = '<svg xmlns="http://www.w3.org/2000/svg"><iframe src="http://evil.com"/></svg>'
    resp = client.post(
        "/api/v1/upload",
        headers=admin_headers,
        files={"file": ("evil3.svg", io.BytesIO(_make_svg_bytes(svg)), "image/svg+xml")},
    )
    assert resp.status_code == 415


def test_get_uploaded_image(client, admin_headers):
    upload_resp = client.post(
        "/api/v1/upload",
        headers=admin_headers,
        files={"file": ("test.png", io.BytesIO(_make_png_bytes()), "image/png")},
    )
    image_id = upload_resp.json()["id"]

    resp = client.get(f"/api/v1/upload/{image_id}")
    assert resp.status_code == 200


def test_get_nonexistent_image(client):
    resp = client.get("/api/v1/upload/99999")
    assert resp.status_code == 404


def test_delete_image(client, admin_headers):
    upload_resp = client.post(
        "/api/v1/upload",
        headers=admin_headers,
        files={"file": ("test.png", io.BytesIO(_make_png_bytes()), "image/png")},
    )
    image_id = upload_resp.json()["id"]

    resp = client.delete(f"/api/v1/upload/{image_id}", headers=admin_headers)
    assert resp.status_code == 204

    get_resp = client.get(f"/api/v1/upload/{image_id}")
    assert get_resp.status_code == 404


def test_list_images(client, admin_headers):
    client.post(
        "/api/v1/upload",
        headers=admin_headers,
        files={"file": ("test.png", io.BytesIO(_make_png_bytes()), "image/png")},
    )

    resp = client.get("/api/v1/upload", headers=admin_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1
