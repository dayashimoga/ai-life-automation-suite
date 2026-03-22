const themeToggle = document.getElementById('theme-toggle');
const body = document.body;
const logUsageBtn = document.getElementById('log-usage-btn');
const appNameInput = document.getElementById('app-name');
const appMinutesInput = document.getElementById('app-minutes');
const statusMessage = document.getElementById('status-message');

const startFocusBtn = document.getElementById('start-focus-btn');
const focusAppInput = document.getElementById('focus-app');
const focusDurationInput = document.getElementById('focus-duration');
const activeSessionsDiv = document.getElementById('active-sessions');
const predictBtn = document.getElementById('predict-btn');
const predictAppName = document.getElementById('predict-app-name');
const predictionResult = document.getElementById('prediction-result');

const refreshAlertsBtn = document.getElementById('refresh-alerts-btn');
const alertsContainer = document.getElementById('alerts-container');


// Theme Toggling (dark is default)
themeToggle.addEventListener('click', () => {
    if (body.getAttribute('data-theme') === 'light') {
        body.removeAttribute('data-theme');
        themeToggle.textContent = '🌙';
    } else {
        body.setAttribute('data-theme', 'light');
        themeToggle.textContent = '☀️';
    }
});

// Log Usage API call
logUsageBtn.addEventListener('click', async () => {
    const app = appNameInput.value.trim();
    const minutes = parseInt(appMinutesInput.value);
    
    if(!app || isNaN(minutes)) {
        statusMessage.innerText = "Please provide app name and valid minutes.";
        return;
    }

    try {
        logUsageBtn.disabled = true;
        const res = await fetch("/api/v1/usage/track", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ app_name: app, duration_minutes: minutes })
        });
        
        if (res.ok) {
            appNameInput.value = '';
            appMinutesInput.value = '';
            statusMessage.style.color = "var(--primary)";
            statusMessage.innerText = `Successfully tracked ${minutes} mins for ${app}.`;
            loadAlerts(); // refresh alerts because thresholds might have broke
            setTimeout(() => statusMessage.innerText = '', 3000);
        }
    } catch(err) {
        statusMessage.style.color = "var(--danger)";
        statusMessage.innerText = "Failed to track usage: " + err.message;
    } finally {
        logUsageBtn.disabled = false;
    }
});

// Focus Session API call
startFocusBtn.addEventListener('click', async () => {
    const app = focusAppInput.value.trim();
    const duration = parseInt(focusDurationInput.value);
    
    if(!app || isNaN(duration)) return;

    try {
        const res = await fetch("/api/v1/usage/focus", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ target_app: app, duration_minutes: duration })
        });
        if(res.ok) {
            focusAppInput.value = '';
            focusDurationInput.value = '';
            loadSessions();
        }
    } catch(err) { console.error(err); }
});

async function loadSessions() {
    try {
        const res = await fetch("/api/v1/usage/focus");
        const data = await res.json();
        activeSessionsDiv.innerHTML = '';
        if(data.length === 0) return;
        
        data.forEach(s => {
            const el = document.createElement('div');
            el.className = 'session-card';
            const end = new Date(s.end_time).toLocaleTimeString();
            el.innerHTML = `<span>🔒 Blocking ${s.target_app}</span><span>Until ${end}</span>`;
            activeSessionsDiv.appendChild(el);
        });
    } catch(err) { console.error(err); }
}

async function loadAlerts() {
    try {
        const res = await fetch("/api/v1/usage/alerts");
        const alerts = await res.json();
        alertsContainer.innerHTML = '';
        
        if(alerts.length === 0) {
            alertsContainer.innerHTML = '<p style="color:var(--text-muted);">All good! No excessive usage detected.</p>';
            return;
        }

        alerts.forEach(a => {
            const el = document.createElement('div');
            el.className = 'alert-card';
            const dateStr = new Date(a.timestamp).toLocaleString();
            el.innerHTML = `
                <div style="font-size:0.8rem; opacity:0.8;">${dateStr}</div>
                <div style="font-size:1.1rem; font-weight:700;">${a.message}</div>
            `;
            alertsContainer.appendChild(el);
        });
    } catch(err) { console.error(err); }
}

predictBtn.addEventListener('click', async () => {
    const app = predictAppName.value;
    if(!app) return alert("Please specify an app name to calculate vector risk.");
    
    predictBtn.innerText = "Analyzing Risk Tensor...";
    try {
        const res = await fetch('/api/v1/usage/predict', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ app_name: app, minutes: 1 })
        });
        
        if(res.ok) {
            const data = await res.json();
            predictionResult.classList.remove('hidden');
            predictionResult.innerHTML = `
                <div style="font-size:2rem; font-weight:bold; color:${data.will_doomscroll ? '#ef4444' : '#10b981'};">
                    ${Math.round(data.prediction_score * 100)}% RISK
                </div>
                <p style="margin-top:10px;">${data.message}</p>
            `;
            if (data.will_doomscroll) {
                // Pre-fill block app to encourage them to click
                document.getElementById('focus-app').value = app;
                document.getElementById('focus-duration').value = 15;
            }
        }
    } catch(e) {
        console.error("Predict fail:", e);
    } finally {
        predictBtn.innerText = "Analyze Risk Vector";
    }
});

refreshAlertsBtn.addEventListener('click', () => { loadAlerts(); loadSessions(); });

// Init
loadAlerts();
loadSessions();
