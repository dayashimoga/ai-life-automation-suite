const CACHE_NAME = 'ai-suite-cache-v2';
const STATIC_ASSETS = [
    '/',
    '/static/index.html',
    '/static/style.css',
    '/static/app.js',
];

// ─── Install: Pre-cache static assets ─────────────────────
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(STATIC_ASSETS);
        }).then(() => self.skipWaiting())
    );
});

// ─── Activate: Clean old caches ───────────────────────────
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
            );
        }).then(() => self.clients.claim())
    );
});

// ─── Fetch: Network-first with cache fallback ─────────────
self.addEventListener('fetch', event => {
    // Skip non-GET and API requests
    if (event.request.method !== 'GET' || event.request.url.includes('/api/')) {
        return;
    }

    event.respondWith(
        fetch(event.request)
            .then(response => {
                // Cache successful responses
                const responseClone = response.clone();
                caches.open(CACHE_NAME).then(cache => {
                    cache.put(event.request, responseClone);
                });
                return response;
            })
            .catch(() => {
                // Serve from cache when offline
                return caches.match(event.request).then(cached => {
                    return cached || new Response('Offline — cached content unavailable.', {
                        headers: { 'Content-Type': 'text/plain' }
                    });
                });
            })
    );
});

// ─── Background Sync: Queue actions when offline ──────────
self.addEventListener('sync', event => {
    if (event.tag === 'habit-sync') {
        event.waitUntil(syncHabitLogs());
    }
});

async function syncHabitLogs() {
    try {
        const cache = await caches.open('habit-pending');
        const requests = await cache.keys();
        for (const req of requests) {
            try {
                await fetch(req.clone());
                await cache.delete(req);
            } catch (e) {
                // Will retry on next sync
            }
        }
    } catch (e) {
        // Silently fail
    }
}

// ─── Push Notifications ───────────────────────────────────
self.addEventListener('push', event => {
    if (event.data) {
        const data = event.data.json();
        event.waitUntil(
            self.registration.showNotification(data.title, {
                body: data.body,
                icon: '/static/icon.png',
                badge: '/static/badge.png',
                vibrate: [200, 100, 200],
                data: data
            })
        );
    }
});

self.addEventListener('notificationclick', event => {
    event.notification.close();
    event.waitUntil(clients.openWindow('/'));
});

// ─── SSE → Notification proxy ─────────────────────────────
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'SHOW_NOTIFICATION') {
        const { title, body } = event.data.payload;
        self.registration.showNotification(title, {
            body: body,
            icon: '/static/icon.png',
            vibrate: [100, 50, 100]
        });
    }
});
