// Micro-Habit Engine — Frontend Logic

async function logHabit(name) {
    const fb = document.getElementById('logFeedback');
    try {
        const res = await fetch('/habit/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ habit_name: name })
        });
        const data = await res.json();
        fb.textContent = `✅ ${name.replace('_', ' ')} logged at ${new Date().toLocaleTimeString()}!`;
        fb.classList.add('show');
        setTimeout(() => fb.classList.remove('show'), 3000);
        refreshDashboard();
    } catch (e) {
        fb.textContent = '❌ Failed to log habit.';
        fb.classList.add('show');
    }
}

async function refreshDashboard() {
    await Promise.all([loadScores(), loadInsights()]);
}

async function loadScores() {
    const container = document.getElementById('scoresContainer');
    try {
        const res = await fetch('/habit/score');
        const scores = await res.json();
        if (!scores.length) {
            container.innerHTML = '<div class="empty-state">No habits tracked yet. Start by logging one above! 🚀</div>';
            return;
        }
        container.innerHTML = scores.map(s => {
            const pct = Math.min(100, (s.decayed_score / 100) * 100);
            const emoji = s.habit_name === 'drink_water' ? '💧' : s.habit_name === 'stretch' ? '🧘' : '🚶';
            return `
                <div class="score-card">
                    <div class="habit-label">${emoji} ${s.habit_name.replace('_', ' ')}</div>
                    <div class="score-value">${s.decayed_score.toFixed(1)}</div>
                    <div class="streak">🔥 ${s.streak_days} day streak</div>
                    <div class="progress-bar"><div class="progress-fill" style="width:${pct}%"></div></div>
                </div>
            `;
        }).join('');
    } catch (e) {
        container.innerHTML = '<div class="empty-state">Could not load scores.</div>';
    }
}

async function loadInsights() {
    const container = document.getElementById('insightsContainer');
    try {
        const res = await fetch('/habit/insights');
        const insights = await res.json();
        if (!insights.length) {
            container.innerHTML = '<div class="empty-state">Log some habits to unlock AI insights! 🧠</div>';
            return;
        }
        container.innerHTML = insights.map(i => `
            <div class="insight-item">
                <div class="insight-status ${i.status}"></div>
                <div class="insight-text">
                    <div class="name">${i.habit_name.replace('_', ' ')} — ${i.status.toUpperCase()}</div>
                    ${i.nudge ? `<div class="nudge">${i.nudge}</div>` : '<div class="nudge">Keep it up! 💪</div>'}
                </div>
            </div>
        `).join('');
    } catch (e) {
        container.innerHTML = '<div class="empty-state">Could not load insights.</div>';
    }
}

// Theme toggle
const themeBtn = document.getElementById('themeToggle');
const saved = localStorage.getItem('habit-theme');
if (saved === 'light') { document.body.setAttribute('data-theme', 'light'); themeBtn.textContent = '☀️'; }

themeBtn.addEventListener('click', () => {
    const isLight = document.body.getAttribute('data-theme') === 'light';
    document.body.setAttribute('data-theme', isLight ? 'dark' : 'light');
    themeBtn.textContent = isLight ? '🌙' : '☀️';
    localStorage.setItem('habit-theme', isLight ? 'dark' : 'light');
});

// Auto-refresh
refreshDashboard();
setInterval(refreshDashboard, 15000);
