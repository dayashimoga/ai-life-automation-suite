# AI Life Automation Suite - Comprehensive Guide

## 🌟 Introduction & Vision
The **AI Life Automation Suite** is a unified, locally-deployable ecosystem of 5 microservices and a native React-Native mobile application. It acts as a "Deep Brain" for your digital and physical life, aggregating data to provide actionable, intelligent insights into your habits, focus, mental wellness, and security.

### ❓ The Problem It Solves
Modern digital life is incredibly fragmented:
- You use one app for habit tracking, another for journaling, a third for screen-time management, and separate closed-ecosystem hardware for security.
- **The Gap**: None of these tools talk to each other. They cannot correlate your late-night doomscrolling with your failed morning meditation, nor can they detect burnout before it happens.
- **The Solution**: This suite unifies these pillars. By tracking habits, screen time, journal sentiments, and security events in one local, AI-powered ecosystem, it correlates insights (the "Deep Brain") to give you a holistic understanding of your wellbeing.

---

## 🚀 The 5 Core Projects & Features

### 1. Unified Dashboard (`unified-dashboard-app`)
The central command center.
- **Features**: Aggregates data from all other services into a seamless Glassmorphism UI. Features a **Cross-App Intelligence Layer** (`/api/v1/intelligence`) that parses data across habits, screen time, and journaling to provide predictive correlations (e.g., "High screen time on Sundays disrupts your Monday morning workout routine").
- **How it works**: Acts as an API Gateway, fetching status and data from sibling microservices using asynchronous HTTP requests, ensuring fast, non-blocking UI loads.

### 2. Micro-Habit Engine (`micro-habit-engine`)
A gamified, intelligent habit tracker.
- **Features**: Tracks streaks, generates dynamic achievement badges, leverages AI predictive decay (warning you *before* a habit decays), and includes viral "Share Streak" capabilities.
- **How it works**: Uses a weighted decay algorithm rather than a binary pass/fail system, allowing for human error without destroying user motivation.

### 3. Doomscroll Breaker (`doomscroll-breaker-app`)
A digital wellbeing and focus monitor.
- **Features**: Tracks app usage, calculates a real-time risk score for "doomscrolling," triggers focus/Pomodoro sessions, and predicts risky sessions using historical Exponential Weighted Moving Average (EWMA).
- **How it works**: Tracks session duration against historical baselines to determine if usage is productive or compulsive. Integrates with the Dashboard to correlate screen time with habit success.

### 4. Memory Journal (`memory-journal-app`)
An AI-powered digital diary.
- **Features**: Auto-captions uploaded images (DeepFace/Vision), provides semantic search over historical entries, and includes a **Burnout & Wellness Sentiment Engine** that analyzes recent entries to predict mental fatigue.
- **How it works**: Processes text through a weighted keyword scoring algorithm to detect early markers of burnout, distress, or high motivation.

### 5. Visual Intelligence (`visual-intelligence-app`)
A smart security and environment monitor.
- **Features**: Converts standard webcams or video streams into smart security feeds using YOLOv8 object detection. Includes zone monitoring and webhook alerting.
- **How it works**: Processes video frames through a local machine learning model, tracking object bounding boxes. If a person enters a predefined pixel zone, it fires a real-time alert to the Dashboard.

### 📱 AI Life Suite Mobile App (React Native/Expo)
The native companion app.
- **Features**: Extends the web suite into a native iOS/Android experience. Includes 5 distinct tabs matching the microservices, system-level push notifications for habit reminders, and a dedicated "Intelligence" screen for cross-app insights.
- **How it works**: Built with React Native and Expo, connects directly to the REST APIs of the 5 microservices, using `expo-notifications` for deep OS-level integration.

---

## 🧠 Why This Project Works (The Architecture)
1. **Decoupled but Integrated**: Built as independent FastAPI microservices. If the Vision app crashes or updates, your Habit tracker stays online.
2. **Local & Private by Default**: Uses lightweight decentralized SQLite databases. Your most private data (journal entries, habits, camera feeds) is not locked in a corporate cloud.
3. **Cross-App Intelligence**: By utilizing a central Dashboard to cross-reference data, the suite identifies patterns an isolated app never could.

---

## 🎯 Applications & Use Cases

1. **The Ultimate Personal Operating System (Individuals)**
   - Correlate diet/exercise habits with screen time and mood. Detect burnout 3 days in advance based on journal sentiment and doomscrolling spikes.
2. **Digital Detox Therapy (Health Coaches & Therapists)**
   - Health professionals can white-label the suite, using the predictive risk APIs to monitor client adherence to sleep schedules and screen-time reductions.
3. **Smart Home Security (Homeowners & Small Businesses)**
   - Small shops can deploy the Visual Intelligence module to existing CCTV cameras to get high-end enterprise alerting (zone incursions) without enterprise costs.
4. **Digital Legacies (Families)**
   - Using the Memory Journal's semantic search and auto-tagging to build a highly accessible, searchable family archive of photos and thoughts.

---

## 📖 Step-by-Step User Guide (How to Run and Use)

### Phase 1: Installation & Startup
1. **Prerequisites**: Ensure Python 3.10+ and Node.js 18+ are installed.
2. **Start the Backend**:
   - Open a terminal in the root directory.
   - Run the local orchestrator: `python run_demo.py`
   - This automatically provisions virtual environments for all 5 apps, installs dependencies, and boots them on ports 8001-8005.
3. **Access the Dashboard**:
   - Open your browser to `http://localhost:8005`. This is your Unified Command Center.

### Phase 2: Daily Usage Workflow
1. **Morning (The Habit Engine)**:
   - Navigate to the **Habits** tab. Log your morning routines (e.g., "Meditation", "Hydration"). Watch your streak increase and collect badges.
2. **Mid-Day (Focus & Doomscroll)**:
   - Keep the **Doomscroll Breaker** active. If your screen time spikes, the unified dashboard will alert you that your "Doomscroll Risk" is high. Start a "Focus Session" to block out noise.
3. **Evening (Memory Journal)**:
   - Go to the **Journal** tab. Upload a photo from your day or type a brief thought. The AI will auto-caption the image and analyze your text for burnout patterns.
4. **Anytime (Visual Intelligence)**:
   - The security feed runs silently. Check the **Security** tab to see if the YOLOv8 model detected any anomalous movement in your defined zones.
5. **Weekly (Deep Brain Review)**:
   - Check the **Intelligence** section on the Dashboard. Read the AI correlations (e.g., "Your 'Read 30 mins' habit failed this week because your Doomscroll risk hit 80% on Tuesday").

### Phase 3: Going Mobile (Optional)
If you want the experience on your phone:
1. Open a terminal and `cd mobile`.
2. Run `npm install` followed by `npx expo start`.
3. Download the **Expo Go** app on your iPhone/Android.
4. Scan the QR code in the terminal to load the native app with push notifications.

---

## 🧪 Testing & Verification
The entire suite is verified with an automated test runner. Run tests from the root directory to verify >90% coverage with 100% pass rates:
```bash
.\test_all.ps1
```

## Conclusion
The AI Life Automation Suite isn't just a collection of apps; it is a unified, intelligent observer of your digital lifecycle, designed to foster productivity, secure your physical space, and protect your mental wellbeing.
