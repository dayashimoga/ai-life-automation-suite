document.addEventListener('DOMContentLoaded', () => {
    const navItems = document.querySelectorAll('.nav-item');
    const iframe = document.getElementById('app-frame');
    const loader = document.getElementById('loader');

    // Polling interval for microservices health checks (every 10 seconds)
    const HEALTH_CHECK_INTERVAL = 10000;

    // Default load memory journal
    loadApp(navItems[0].dataset.target);

    // Sidebar Navigation Logic
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            // Remove active style
            navItems.forEach(nav => nav.classList.remove('active'));
            // Add active to clicked target
            item.classList.add('active');
            
            // Switch IFrame Context
            const targetUrl = item.dataset.target;
            loadApp(targetUrl);
        });
    });

    /**
     * Helper to load the app in the iframe gracefully
     */
    function loadApp(url) {
        iframe.classList.remove('loaded');
        loader.style.display = 'flex';
        
        iframe.src = url;
        
        iframe.onload = () => {
            loader.style.display = 'none';
            iframe.classList.add('loaded');
        };

        // Fallback if iframe fails to emit load event
        setTimeout(() => {
            loader.style.display = 'none';
            iframe.classList.add('loaded');
        }, 1500);
    }

    /**
     * Real-time services telemetry poll
     */
    async function checkServiceHealth() {
        try {
            const res = await fetch('/api/v1/status');
            const data = await res.json();
            
            updateDot('status-journal', data.journal);
            updateDot('status-doomscroll', data.doomscroll);
            updateDot('status-vision', data.vision);
            updateDot('status-habit', data.habit);
        } catch (err) {
            console.error('Failed to poll gateway telemetry:', err);
        }
    }

    function updateDot(id, status) {
        const el = document.getElementById(id);
        if (!el) return;
        el.className = 'dot'; // reset
        if (status === 'online') {
            el.classList.add('online');
        } else if (status === 'error' || status === 'offline') {
            el.classList.add('error');
        }
    }

    // Initial Health Check
    checkServiceHealth();
    setInterval(checkServiceHealth, HEALTH_CHECK_INTERVAL);

    // ==========================================
    // Push Notifications & SSE Stream
    // ==========================================
    let swRegistration = null;

    if ('serviceWorker' in navigator && 'PushManager' in window) {
        navigator.serviceWorker.register('/static/sw.js')
            .then(reg => {
                swRegistration = reg;
                console.log('Service Worker Registered');
                requestNotificationPermission();
            })
            .catch(err => console.error('Service Worker Error', err));
    }

    function requestNotificationPermission() {
        if (Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }

    // Connect to SSE stream
    const evtSource = new EventSource('/api/v1/notifications/stream');
    evtSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (Notification.permission === 'granted' && swRegistration) {
                // Route to Service Worker for background native display
                swRegistration.active.postMessage({
                    type: 'SHOW_NOTIFICATION',
                    payload: data
                });
            } else if (Notification.permission === 'granted') {
                // Fallback direct HTML5
                new Notification(data.title, { body: data.body, icon: '/static/icon.png' });
            }
        } catch(e) { console.error('SSE Error:', e); }
    };
});
