/**
 * Voice Command Engine — Web Speech API integration for hands-free control.
 * Supports: habit logging, journal search, dashboard navigation, and status queries.
 */

class VoiceCommandEngine {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.commands = {};
        this._initRecognition();
        this._registerDefaultCommands();
    }

    _initRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.warn('Web Speech API not supported in this browser.');
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'en-US';

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript.toLowerCase().trim();
            console.log(`🎤 Voice: "${transcript}"`);
            this._processCommand(transcript);
        };

        this.recognition.onerror = (event) => {
            console.warn('Speech recognition error:', event.error);
            this.isListening = false;
            this._updateUI(false);
        };

        this.recognition.onend = () => {
            this.isListening = false;
            this._updateUI(false);
        };
    }

    _registerDefaultCommands() {
        // Habit Commands
        this.register('log water', () => this._logHabit('drink_water'));
        this.register('log stretch', () => this._logHabit('stretch'));
        this.register('log walk', () => this._logHabit('walk'));
        this.register('drink water', () => this._logHabit('drink_water'));

        // Navigation Commands
        this.register('show journal', () => this._navigate('journal'));
        this.register('show habits', () => this._navigate('habit'));
        this.register('show vision', () => this._navigate('vision'));
        this.register('show doomscroll', () => this._navigate('doomscroll'));
        this.register('go home', () => this._navigate('dashboard'));

        // Query Commands
        this.register('show my streaks', () => this._showStreaks());
        this.register('what are my habits', () => this._showStreaks());
        this.register('status', () => this._showStatus());
        this.register('export data', () => this._exportData());
    }

    register(phrase, callback) {
        this.commands[phrase] = callback;
    }

    toggle() {
        if (!this.recognition) {
            this._showFeedback('⚠️ Voice not supported in this browser');
            return;
        }
        if (this.isListening) {
            this.recognition.stop();
        } else {
            this.recognition.start();
            this.isListening = true;
            this._updateUI(true);
            this._showFeedback('🎤 Listening...');
        }
    }

    _processCommand(transcript) {
        let matched = false;
        for (const [phrase, callback] of Object.entries(this.commands)) {
            if (transcript.includes(phrase)) {
                callback();
                matched = true;
                break;
            }
        }
        if (!matched) {
            this._showFeedback(`❓ Unknown command: "${transcript}"`);
        }
    }

    async _logHabit(name) {
        try {
            const resp = await fetch('http://localhost:8004/api/v1/habit/log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ habit_name: name })
            });
            if (resp.ok) {
                this._showFeedback(`✅ Logged: ${name.replace('_', ' ')}`);
            }
        } catch (e) {
            this._showFeedback(`❌ Failed to log ${name}`);
        }
    }

    _navigate(section) {
        const navItems = document.querySelectorAll('.nav-item');
        for (const item of navItems) {
            if (item.dataset.app === section || item.textContent.toLowerCase().includes(section)) {
                item.click();
                this._showFeedback(`📍 Navigating to ${section}`);
                return;
            }
        }
        this._showFeedback(`❓ Section "${section}" not found`);
    }

    async _showStreaks() {
        try {
            const resp = await fetch('http://localhost:8004/api/v1/habit/score');
            if (resp.ok) {
                const scores = await resp.json();
                const lines = scores.map(s => `${s.habit_name}: ${s.streak_days}d streak (${Math.round(s.decayed_score)}%)`);
                this._showFeedback('📊 ' + lines.join(' | '));
            }
        } catch (e) {
            this._showFeedback('❌ Could not fetch streaks');
        }
    }

    async _showStatus() {
        try {
            const resp = await fetch('/api/v1/status');
            if (resp.ok) {
                const data = await resp.json();
                const lines = Object.entries(data).map(([k, v]) => `${k}: ${v}`);
                this._showFeedback('🔍 ' + lines.join(' | '));
            }
        } catch (e) {
            this._showFeedback('❌ Status unavailable');
        }
    }

    _exportData() {
        window.location.href = '/api/v1/export';
        this._showFeedback('📦 Downloading data export...');
    }

    _showFeedback(message) {
        // Try to use existing notification area, or create toast
        let toast = document.getElementById('voice-feedback');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'voice-feedback';
            toast.style.cssText = `
                position: fixed; bottom: 24px; right: 24px; z-index: 9999;
                background: rgba(15, 23, 42, 0.95); color: #e2e8f0;
                padding: 14px 22px; border-radius: 12px;
                font-size: 14px; font-family: 'Inter', sans-serif;
                border: 1px solid rgba(99, 102, 241, 0.4);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
                backdrop-filter: blur(12px);
                transition: opacity 0.3s ease;
            `;
            document.body.appendChild(toast);
        }
        toast.textContent = message;
        toast.style.opacity = '1';
        clearTimeout(this._feedbackTimeout);
        this._feedbackTimeout = setTimeout(() => {
            toast.style.opacity = '0';
        }, 3000);
    }

    _updateUI(isActive) {
        const btn = document.getElementById('voice-btn');
        if (btn) {
            btn.classList.toggle('active', isActive);
            btn.textContent = isActive ? '🎤 Listening...' : '🎤 Voice';
        }
    }
}

// Auto-initialize
window.voiceEngine = new VoiceCommandEngine();
