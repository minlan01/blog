def test_rss_feed(client):
    resp = client.get("/api/v1/rss")
    assert resp.status_code == 200
    assert "xml" in resp.headers["content-type"]
    assert b"<rss" in resp.content
    assert b"<channel>" in resp.content


def test_sitemap(client):
    resp = client.get("/api/v1/sitemap.xml")
    assert resp.status_code == 200
    assert "xml" in resp.headers["content-type"]
    assert b"<urlset" in resp.content
    assert b"<url>" in resp.content
