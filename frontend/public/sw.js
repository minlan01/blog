// 简易 Service Worker — 缓存静态资源，离线时回退
const CACHE_NAME = 'blog-v4';
const PRECACHE = [
  '/',
  '/manifest.json',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE)).catch(() => {})
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  // 只处理 GET
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // API 请求和跨域请求不缓存
  if (url.pathname.startsWith('/api/')) return;

  // 静态资源（带 hash 的 assets）：stale-while-revalidate
  if (url.pathname.startsWith('/assets/')) {
    event.respondWith(
      caches.open(CACHE_NAME).then(async (cache) => {
        const cached = await cache.match(req);
        const network = fetch(req).then((res) => {
          if (res.ok) cache.put(req, res.clone());
          return res;
        }).catch(() => cached);
        return cached || network;
      })
    );
    return;
  }

  // 页面导航：network-first，失败回退缓存
  // cache: 'no-cache' 强制 revalidate——部署后浏览器里残留的无 Cache-Control 旧
  // index.html 条目（启发式新鲜期内）只有靠 SW 侧绕过 HTTP 缓存才能立即失效
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req, { cache: 'no-cache' }).then((res) => {
        const clone = res.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(req, clone));
        return res;
      }).catch(() => caches.match(req).then((cached) => cached || caches.match('/')))
    );
    return;
  }
});
