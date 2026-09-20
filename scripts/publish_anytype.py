import json
import urllib.request
import ssl

API = "https://www.chiyeblog.cn/api/v1"
TOKEN = "pat_22b74d22cc199cfa2d76684ab06c522b10ce713d"
POST_ID = 7

payload = {
    "status": "published",
    "is_featured": True,
    "featured_order": 99,
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(
    f"{API}/admin/posts/{POST_ID}",
    data=data,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    },
    method="PUT",
)

ctx = ssl.create_default_context()

try:
    with urllib.request.urlopen(req, context=ctx) as resp:
        body = resp.read().decode("utf-8")
        result = json.loads(body)
        print(f"Status: {resp.status}")
        print(f"Title: {result.get('title')}")
        print(f"Slug: {result.get('slug')}")
        print(f"Status: {result.get('status')}")
        print(f"Featured: {result.get('is_featured')} (order={result.get('featured_order')})")
        print(f"URL: https://www.chiyeblog.cn/post/anytype-personal-knowledge-base")
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode('utf-8')[:500]}")
