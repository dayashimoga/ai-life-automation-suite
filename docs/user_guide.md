# General User Guide - AI Life Automation Suite

## Overview
This monorepo contains three totally decoupled, independent AI progressive web applications running natively on your hardware.

## Quick Start
1. Ensure you have activated standard Python environments.
2. Run `python start_servers.py` in the root directory.
3. Access each unique tool on its dedicated UI Port:
    - **Memory Journal**: `http://localhost:8001`
    - **Doomscroll Breaker**: `http://localhost:8002`
    - **Visual Intelligence**: `http://localhost:8003`
    - **Micro-Habit Engine**: `http://localhost:8004`

*(Note: All applications utilize a responsive, premium glassmorphism design mapped to a dark-first aesthetic. You can toggle to light mode using the sun/moon icon in the navigation bar.)*

## Application Manuals

### Memory Journal (Port 8001)
Upload `.jpg` or `.mp4` video files to create timeless memory blobs. The system automatically ingests memory media, isolates keyframes to invoke the local YOLOv8 backend, and constructs rich search-tags. Use the top timeline to browse or filter dynamically.

### Doomscroll Breaker (Port 8002)
To stop spiraling into dopaminergic loops, enter any target app (e.g., `TikTok` or `Reddit`). The native Predictive LSTM AI models your current behavioral usage context combined with the exact Server UTC time, aggressively deploying 15-Minute focus locks *before* the doomscroll event spirals via heuristic analysis.

### Visual Intelligence (Port 8003)
Connect any Local Camera. The zero-latency WebSocket stream instantly bounds active YOLOv8m objects, sending telemetry dynamically to the UI.
- **Biometric Security**: DeepFace embeds authorized persons out-of-the-box. Add known photos of faces into the `authorized_faces/` local root folder to whitelist individuals from `unauthorized_presence` arrays.
- **Video Logs**: Upload local `.mp4` video files to parse historic scenes. The local SQLite database (`history.db`) actively binds the telemetry logs so you can browse the timeline natively across browser restarts.

### Micro-Habit Engine (Port 8004)
Track and reinforce tiny behavioral changes. Instead of tracking massive goals, this application uses a custom exponential-decay algorithm to track micro-actions (like "drinking water" or "standing up"). It assigns dynamic reinforcement loops and calculates streak retention metrics locally in SQLite.

## Android / PWA Support
Navigate to any of the 3 Localhost IPs on your mobile device (if bound on LAN). Because every HTML endpoint binds a localized `manifest.json` and strict Service Worker architecture, Android and iOS allow you to click **"Add To Home Screen"**, instantly installing them as native Progressive Web Applications.
