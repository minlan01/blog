import json
import urllib.request
import ssl

API = "https://www.chiyeblog.cn/api/v1"
TOKEN = "pat_22b74d22cc199cfa2d76684ab06c522b10ce713d"
POST_ID = 7

payload = {
    "is_featured": True,
    "featured_order": 0,
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
        result = json.loads(resp.read().decode("utf-8"))
        print(f"featured_order 已改为: {result.get('featured_order')}")
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode('utf-8')[:500]}")
