# AI Life Suite — Mobile App (React Native / Expo)

A native mobile companion to the AI Life Automation Suite backend services.

## Architecture

```
/mobile
  App.js                      # Root navigator (dark tab bar)
  app.json                    # Expo config (push notifications, API URLs)
  package.json                # Dependencies
  screens/
    HabitsScreen.js           # Habit tracking + push notification reminders
    FocusScreen.js            # Doomscroll risk gauge
    IntelligenceScreen.js     # Cross-App Deep Brain insights
    JournalScreen.js          # Memory Journal + Burnout wellness score
    SecurityScreen.js         # Visual Intelligence events
```

## Getting Started

### Prerequisites
- Node.js 18+
- Expo CLI: `npm install -g expo-cli`
- Expo Go app on your iPhone or Android phone

### Run

```bash
cd mobile
npm install
npx expo start
```

Scan the QR code with **Expo Go** on your phone. **The app will connect to your local backend services.**

## Configuring Backend URLs

Edit `app.json` and update the `extra` section with your Render deployment URLs:

```json
"extra": {
  "habitApiUrl": "https://micro-habit-engine.onrender.com",
  "doomscrollApiUrl": "https://doomscroll-breaker.onrender.com",
  "journalApiUrl": "https://memory-journal.onrender.com",
  "visionApiUrl": "https://visual-intelligence.onrender.com",
  "dashboardApiUrl": "https://unified-dashboard.onrender.com"
}
```

## Key Mobile Features
- 🔔 **System-level Push Notifications** for habit reminders (via `expo-notifications`)
- 🧠 **Deep Brain Intelligence** screen showing cross-app behavioral insights
- 📊 **Burnout Risk Score** from the Journal Wellness endpoint
- 🔒 **Real-time CCTV events** from Visual Intelligence
- 📱 **Native Home Screen** dark glassmorphism UI

## Building for Production (App Store / Google Play)

```bash
npm install -g eas-cli
eas build --platform ios
eas build --platform android
```

> **Requires Expo EAS account (free tier available)**
