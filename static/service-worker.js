// Service Worker for PWA - Offline Support
// Enables offline functionality and caching

const CACHE_NAME = 'ai-grading-v2.0.0';
const RUNTIME_CACHE = 'runtime-cache-v2';

// Assets to cache on install
const PRECACHE_ASSETS = [
    '/',
    '/static/css/main.css',
    '/static/css/dark-mode.css',
    '/static/css/accessibility.css',
    '/static/js/theme-manager.js',
    '/static/icons/icon-192x192.png',
    '/offline.html'
];

// Install event - cache essential assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Caching app shell');
                return cache.addAll(PRECACHE_ASSETS);
            })
            .then(() => self.skipWaiting())
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames
                    .filter((name) => name !== CACHE_NAME && name !== RUNTIME_CACHE)
                    .map((name) => caches.delete(name))
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
    // Skip cross-origin requests
    if (!event.request.url.startsWith(self.location.origin)) {
        return;
    }

    // Network-first for API calls
    if (event.request.url.includes('/api/')) {
        event.respondWith(networkFirst(event.request));
        return;
    }

    // Cache-first for static assets
    if (event.request.url.match(/\.(js|css|png|jpg|jpeg|svg|gif|woff2?)$/)) {
        event.respondWith(cacheFirst(event.request));
        return;
    }

    // Stale-while-revalidate for HTML pages
    event.respondWith(staleWhileRevalidate(event.request));
});

// Network-first strategy
async function networkFirst(request) {
    try {
        const networkResponse = await fetch(request);
        const cache = await caches.open(RUNTIME_CACHE);
        cache.put(request, networkResponse.clone());
        return networkResponse;
    } catch (error) {
        const cachedResponse = await caches.match(request);
        return cachedResponse || caches.match('/offline.html');
    }
}

// Cache-first strategy
async function cacheFirst(request) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
        return cachedResponse;
    }

    try {
        const networkResponse = await fetch(request);
        const cache = await caches.open(RUNTIME_CACHE);
        cache.put(request, networkResponse.clone());
        return networkResponse;
    } catch (error) {
        return new Response('Offline', { status: 503 });
    }
}

// Stale-while-revalidate strategy
async function staleWhileRevalidate(request) {
    const cachedResponse = await caches.match(request);

    const fetchPromise = fetch(request).then((networkResponse) => {
        const cache = caches.open(RUNTIME_CACHE);
        cache.then((c) => c.put(request, networkResponse.clone()));
        return networkResponse;
    });

    return cachedResponse || fetchPromise;
}

// Background sync for offline submissions
self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-submissions') {
        event.waitUntil(syncSubmissions());
    }
});

async function syncSubmissions() {
    // Get pending submissions from IndexedDB
    const db = await openDB();
    const submissions = await db.getAll('pending-submissions');

    for (const submission of submissions) {
        try {
            await fetch('/api/submissions/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(submission.data)
            });
            await db.delete('pending-submissions', submission.id);
        } catch (error) {
            console.error('Failed to sync submission:', error);
        }
    }
}

// Push notifications
self.addEventListener('push', (event) => {
    const data = event.data.json();

    const options = {
        body: data.body,
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/badge-72x72.png',
        vibrate: [200, 100, 200],
        data: {
            url: data.url
        }
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

// Notification click
self.addEventListener('notificationclick', (event) => {
    event.notification.close();

    event.waitUntil(
        clients.openWindow(event.notification.data.url)
    );
});
