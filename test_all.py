"""Full blog system test suite — run with: python test_all.py"""
import requests, io, base64

BASE = 'http://localhost:6965/api/v1'
P = 0
F = 0

def t(name, ok, detail=''):
    global P, F
    if ok:
        P += 1
        print(f'  PASS  {name}')
    else:
        F += 1
        print(f'  FAIL  {name}  {detail}')


# ========== 1. Health ==========
r = requests.get('http://localhost:6965/health')
t('Health', r.status_code == 200)

# ========== 2. Auth ==========
r = requests.post(f'{BASE}/auth/register', json={'username': 'testbot', 'password': 'bot12345'})
t('Auth: Register', r.status_code in (201, 409), f'got {r.status_code}')

r = requests.post(f'{BASE}/auth/login', json={'username': 'minlan01', 'password': 'minlan01'})
t('Auth: Login (minlan01)', r.status_code == 200, f'got {r.status_code}')

if r.status_code != 200:
    r = requests.post(f'{BASE}/auth/login', json={'username': 'testbot', 'password': 'bot12345'})
token = r.json()['access_token']
uid = r.json().get('user_id') or r.json().get('id')
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# Ensure admin role
from app.db.session import SessionLocal
from app.models.user import User
from sqlalchemy import select
db = SessionLocal()
u = db.scalar(select(User).where(User.id == r.json().get('user_id', 0) if 'user_id' in r.json() else 0))
if not u:
    # find by token
    for attempt_user in db.scalars(select(User)).all():
        if attempt_user.username in ('minlan01', 'testbot'):
            u = attempt_user
            break
if u and u.role != 'super_admin':
    u.role = 'super_admin'
    db.commit()
db.close()

# Re-login
r2 = requests.post(f'{BASE}/auth/login', json={'username': 'minlan01', 'password': 'minlan01'})
if r2.status_code != 200:
    r2 = requests.post(f'{BASE}/auth/login', json={'username': 'testbot', 'password': 'bot12345'})
token = r2.json()['access_token']
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

r = requests.get(f'{BASE}/auth/me', headers=headers)
t('Auth: Get profile', r.status_code == 200)

# ========== 3. Site Profile ==========
r = requests.get(f'{BASE}/site/profile')
t('Site: Get profile', r.status_code == 200 and r.json().get('site_name') == 'minlan01')

r = requests.put(f'{BASE}/admin/site/profile', headers=headers, json={'hero_subtitle': 'Test'})
t('Site: Update profile', r.status_code == 200)
requests.put(f'{BASE}/admin/site/profile', headers=headers, json={'hero_subtitle': 'SYSTEM ONLINE'})

# ========== 4. Stats ==========
r = requests.get(f'{BASE}/stats')
t('Stats', r.status_code == 200 and isinstance(r.json().get('posts'), int))

# ========== 5. Categories ==========
r = requests.get(f'{BASE}/categories')
t('Categories: List', r.status_code == 200 and len(r.json()) > 0)

r = requests.post(f'{BASE}/admin/categories', headers=headers, json={'name': 'TestCat', 'slug': 'test-cat'})
t('Categories: Create', r.status_code == 201)
cat_id = r.json().get('id')

r = requests.put(f'{BASE}/admin/categories/{cat_id}', headers=headers, json={'name': 'TestCatX'})
t('Categories: Update', r.status_code == 200)

r = requests.delete(f'{BASE}/admin/categories/{cat_id}', headers=headers)
t('Categories: Delete', r.status_code == 204)

# ========== 6. Tags ==========
r = requests.get(f'{BASE}/tags')
t('Tags: List', r.status_code == 200 and len(r.json()) > 0)

r = requests.post(f'{BASE}/admin/tags', headers=headers, json={'name': 'TestTag', 'slug': 'test-tag'})
t('Tags: Create', r.status_code == 201)
tag_id = r.json().get('id')

r = requests.delete(f'{BASE}/admin/tags/{tag_id}', headers=headers)
t('Tags: Delete', r.status_code == 204)

# ========== 7. Posts CRUD ==========
r = requests.get(f'{BASE}/posts')
t('Posts: Public list', r.status_code == 200)

r = requests.post(f'{BASE}/admin/posts', headers=headers, json={
    'title': 'Published Post', 'slug': 'pub-test', 'summary': 'Test pub',
    'content_markdown': '# Hello\n\n```python\nprint(1)\n```', 'status': 'published', 'tag_ids': []
})
t('Posts: Create published', r.status_code == 201)
pub_id = r.json()['id']

r = requests.get(f'{BASE}/posts/pub-test')
t('Posts: Get by slug', r.status_code == 200)

r = requests.put(f'{BASE}/admin/posts/{pub_id}', headers=headers, json={'title': 'Updated Title'})
t('Posts: Update', r.status_code == 200 and r.json()['title'] == 'Updated Title')

r = requests.put(f'{BASE}/admin/posts/{pub_id}', headers=headers, json={'is_featured': True})
t('Posts: Toggle featured', r.json()['is_featured'] == True)

r = requests.get(f'{BASE}/posts', params={'search': 'Updated'})
t('Posts: Search', r.status_code == 200)

requests.post(f'{BASE}/comments', headers=headers, json={'content': 'del', 'post_id': pub_id})
r = requests.delete(f'{BASE}/admin/posts/{pub_id}', headers=headers)
t('Posts: Delete (with comments)', r.status_code == 204)

# ========== 8. Draft System ==========
r = requests.post(f'{BASE}/admin/posts', headers=headers, json={
    'title': 'Draft', 'slug': 'draft-sys-test', 'summary': 'D', 'content_markdown': '# D', 'status': 'draft'
})
t('Draft: Create', r.status_code == 201 and r.json()['status'] == 'draft')
draft_id = r.json()['id']

r = requests.get(f'{BASE}/posts/draft-sys-test')
t('Draft: Hidden from public', r.status_code == 404)

r = requests.get(f'{BASE}/admin/posts', headers=headers)
drafts = [p for p in r.json() if p['status'] == 'draft']
t('Draft: Visible to admin', len(drafts) > 0)

r = requests.put(f'{BASE}/admin/posts/{draft_id}', headers=headers, json={'status': 'published'})
t('Draft: Publish', r.json()['status'] == 'published')

r = requests.get(f'{BASE}/posts/draft-sys-test')
t('Draft: Now public', r.status_code == 200)
requests.delete(f'{BASE}/admin/posts/{draft_id}', headers=headers)

# ========== 9. Comments ==========
r = requests.post(f'{BASE}/admin/posts', headers=headers, json={
    'title': 'CPost', 'slug': 'cpost', 'summary': 'C', 'content_markdown': '# C', 'status': 'published'
})
cp_id = r.json()['id']

r = requests.post(f'{BASE}/comments', headers=headers, json={'content': 'Root', 'post_id': cp_id})
t('Comments: Create', r.status_code == 201)
c1 = r.json()['id']

r = requests.post(f'{BASE}/comments', headers=headers, json={'content': 'Reply', 'post_id': cp_id, 'parent_id': c1})
t('Comments: Reply', r.status_code == 201)

r = requests.get(f'{BASE}/comments', params={'post_id': cp_id})
t('Comments: List', r.status_code == 200 and len(r.json()) >= 1)

r = requests.get(f'{BASE}/admin/comments', headers=headers)
t('Comments: Admin list', r.status_code == 200)

r = requests.delete(f'{BASE}/comments/{c1}', headers=headers)
t('Comments: Delete own', r.status_code == 204)
requests.delete(f'{BASE}/admin/posts/{cp_id}', headers=headers)

# ========== 10. Messages ==========
r = requests.post(f'{BASE}/messages', json={'name': 'Bot', 'email': 'b@b.com', 'content': 'Hi'})
t('Messages: Create', r.status_code == 201)

r = requests.get(f'{BASE}/messages')
t('Messages: List', r.status_code == 200 and len(r.json()) >= 1)

# ========== 11. Media Library ==========
png = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
)
r = requests.post(f'{BASE}/upload', headers={'Authorization': f'Bearer {token}'},
                  files={'file': ('test.png', io.BytesIO(png), 'image/png')})
t('Media: Upload', r.status_code == 200)
img_id = r.json()['id']

r = requests.get(f'{BASE}/upload', headers=headers)
t('Media: List', r.status_code == 200 and len(r.json()) >= 1)

r = requests.get(f'{BASE}/upload/{img_id}')
t('Media: Serve image', r.status_code == 200 and 'image' in r.headers.get('content-type', ''))

r = requests.delete(f'{BASE}/upload/{img_id}', headers=headers)
t('Media: Delete', r.status_code == 204)

# ========== 12. Admin Users ==========
r = requests.get(f'{BASE}/admin/users', headers=headers)
t('Admin: Users list', r.status_code == 200 and len(r.json()) >= 1)

# ========== 13. Friend Links ==========
r = requests.get(f'{BASE}/friend-links')
t('FriendLinks: List', r.status_code == 200)

r = requests.post(f'{BASE}/admin/friend-links', headers=headers, json={
    'name': 'TestLink', 'url': 'https://example.com', 'category': 'test'
})
t('FriendLinks: Create', r.status_code in (200, 201), f'got {r.status_code}')
fl_id = r.json()['id']

r = requests.delete(f'{BASE}/admin/friend-links/{fl_id}', headers=headers)
t('FriendLinks: Delete', r.status_code in (200, 204), f'got {r.status_code}')

# ========== 14. Security Headers ==========
r = requests.get(f'{BASE}/posts')
t('Security: X-Content-Type-Options', r.headers.get('X-Content-Type-Options') == 'nosniff')
t('Security: X-Frame-Options', r.headers.get('X-Frame-Options') == 'DENY')
t('Security: Referrer-Policy', 'strict-origin' in r.headers.get('Referrer-Policy', ''))

# ========== 15. RSS & Sitemap ==========
r = requests.get('http://localhost:6965/api/v1/rss')
t('RSS feed', r.status_code == 200)

r = requests.get('http://localhost:6965/api/v1/sitemap.xml')
t('Sitemap', r.status_code == 200)

# ========== Done ==========
print()
print('=' * 50)
print(f'  TOTAL: {P} passed, {F} failed')
print('=' * 50)
