const themeToggle = document.getElementById('theme-toggle');
const body = document.body;
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const rawImage = document.getElementById('raw-image');
const annotatedImage = document.getElementById('annotated-image');
const countsContainer = document.getElementById('counts-container');
const eventsContainer = document.getElementById('events-container');
const refreshEventsBtn = document.getElementById('refresh-events');
const startCameraBtn = document.getElementById('start-camera');
const resetWorkflowBtn = document.getElementById('reset-workflow');
const webcamVideo = document.getElementById('webcam-video');
const cameraCanvas = document.getElementById('camera-canvas');

const viewHistoryBtn = document.getElementById('view-history');
const historyModal = document.getElementById('history-modal');
const closeHistoryBtn = document.getElementById('close-history');
const historyContent = document.getElementById('history-content');

let stream = null;
let cameraInterval = null;

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

// Live WebRTC Camera Stream
startCameraBtn.addEventListener('click', async () => {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        webcamVideo.srcObject = stream;
        webcamVideo.classList.remove('hidden');
        dropzone.classList.add('hidden');
        startCameraBtn.classList.add('hidden');
        resetWorkflowBtn.classList.remove('hidden');
        
        // Ping YOLOv8 every 3 seconds for anomalies
        cameraInterval = setInterval(() => captureAndProcessFrame(), 3000);
    } catch(err) {
        alert("Camera access denied or unavailable: " + err.message);
    }
});

function captureAndProcessFrame() {
    if(!stream) return;
    cameraCanvas.width = webcamVideo.videoWidth;
    cameraCanvas.height = webcamVideo.videoHeight;
    const ctx = cameraCanvas.getContext('2d');
    ctx.drawImage(webcamVideo, 0, 0, cameraCanvas.width, cameraCanvas.height);
    
    cameraCanvas.toBlob((blob) => {
        if(blob) processFile(blob, true);
    }, 'image/jpeg', 0.8);
}

// Reset Global State
resetWorkflowBtn.addEventListener('click', () => {
    if(stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    if(cameraInterval) clearInterval(cameraInterval);
    
    webcamVideo.classList.add('hidden');
    dropzone.classList.remove('hidden');
    startCameraBtn.classList.remove('hidden');
    resetWorkflowBtn.classList.add('hidden');
    results.classList.add('hidden');
    annotatedImage.src = "";
    countsContainer.innerHTML = '';
});

// History Modal
viewHistoryBtn.addEventListener('click', async () => {
    historyModal.classList.remove('hidden');
    historyContent.innerHTML = 'Querying local SQLite Database...';
    try {
        const res = await fetch("/api/v1/vision/history");
        if(res.ok) {
            const data = await res.json();
            if(data.length === 0) {
                historyContent.innerHTML = 'No historic analyses found yet.';
                return;
            }
            let html = '<ul style="list-style:none; padding:0; margin:0;">';
            data.forEach(item => {
                html += `
                <li style="border-bottom:1px solid rgba(255,255,255,0.1); padding:1rem 0;">
                    <strong style="color:var(--text-color);">${new Date(item.timestamp).toLocaleString()}</strong><br>
                    <span style="color:#80c6ff; font-family:monospace; font-size: 0.9rem;">Counts: ${JSON.stringify(item.counts)}</span><br>
                    <span style="color:var(--accent-color); font-size: 0.9rem;">Anomalies Auto-Generated: ${item.events.length}</span>
                </li>`;
            });
            html += '</ul>';
            historyContent.innerHTML = html;
        } else {
            historyContent.innerHTML = 'Error loading history API.';
        }
    } catch(err) {
        historyContent.innerHTML = 'Network error hitting backend.';
    }
});

closeHistoryBtn.addEventListener('click', () => {
    historyModal.classList.add('hidden');
});

// Drag and Drop
dropzone.addEventListener('click', () => fileInput.click());
dropzone.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.style.transform = "scale(1.02)"; });
dropzone.addEventListener('dragleave', () => dropzone.style.transform = "scale(1)");
dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.style.transform = "scale(1)";
    if (e.dataTransfer.files.length) {
        processFile(e.dataTransfer.files[0]);
    } else {
        alert("Unable to grab file from drag-and-drop. Try clicking instead.");
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
        processFile(e.target.files[0]);
        e.target.value = ''; // allow uploading same file again
    }
});

async function processFile(file, isLive = false) {
    if(!file) return;
    
    if(!isLive) {
        // Show previews for static images
        const reader = new FileReader();
        reader.onload = (e) => {
            if(rawImage) rawImage.src = e.target.result;
        };
        reader.readAsDataURL(file);

        dropzone.classList.add('hidden');
        results.classList.add('hidden');
        loading.classList.remove('hidden');
        loading.innerText = "Transmitting to YOLOv8 Backend...";
        startCameraBtn.classList.add('hidden');
        resetWorkflowBtn.classList.remove('hidden');
    }

    const formData = new FormData();
    formData.append("file", file, "live_frame.jpg");

    try {
        const res = await fetch("/api/v1/vision/process", {
            method: "POST",
            body: formData
        });
        if(res.ok) {
            const data = await res.json();
            
            // Set annotated image
            if(data.annotated_image_base64) {
                annotatedImage.src = `data:image/jpeg;base64,${data.annotated_image_base64}`;
            }

            // Render counts dynamically
            countsContainer.innerHTML = '';
            const counts = data.counts || {};
            if(Object.keys(counts).length === 0) {
                countsContainer.innerHTML = '<p>No recognizable structures found.</p>';
            } else {
                for(const [label, num] of Object.entries(counts)) {
                    countsContainer.innerHTML += `<div class="count-row"><span>${label.toUpperCase()}</span><span>${num}</span></div>`;
                }
            }

            if(!isLive) {
                loading.classList.add('hidden');
            }
            results.classList.remove('hidden');
        } else {
            const errBody = await res.text();
            if(!isLive) alert(`API Error ${res.status}: ${errBody}`);
            resetUI();
        }
    } catch(err) {
        if(!isLive) alert("Javascript execution failure: " + err.message);
        resetUI();
    }
}

function resetUI() {
    loading.classList.add('hidden');
    if(!stream) dropzone.classList.remove('hidden');
    loading.innerText = "Processing via Neural Network...";
}

async function loadEvents() {
    try {
        const res = await fetch("/api/v1/vision/events");
        const events = await res.json();
        eventsContainer.innerHTML = '';
        
        if(events.length === 0) {
            eventsContainer.innerHTML = '<p style="color:var(--text-muted);">No density anomalies localized.</p>';
            return;
        }

        events.slice().reverse().forEach(e => {
            const dateStr = new Date(e.timestamp).toLocaleTimeString();
            eventsContainer.innerHTML += `
                <div class="event-card">
                    <div class="event-card-time">[${dateStr}] ${e.event_type}</div>
                    <div class="event-card-desc">${e.description}</div>
                </div>
            `;
        });
    } catch(err) { console.error(err); }
}

// Remove manual polling
if(refreshEventsBtn) {
    refreshEventsBtn.classList.add('hidden');
}

// Websocket Engine
const wsInputUrl = location.protocol === 'https:' ? 'wss:' : 'ws:';
const ws = new WebSocket(`${wsInputUrl}//${location.host}/api/v1/vision/ws`);

ws.onmessage = (event) => {
    try {
        const data = JSON.parse(event.data);
        const div = document.createElement('div');
        div.className = 'event-card glass-panel fade-in-up';
        div.innerHTML = `
            <div class="header" style="display:flex; justify-content:space-between;">
                <strong style="color:var(--accent-color);">${data.event_type.toUpperCase().replace(/_/g, ' ')}</strong>
                <span class="timestamp" style="font-size: 0.8rem; opacity: 0.7;">${new Date(data.timestamp).toLocaleTimeString()}</span>
            </div>
            <p style="margin-top:0.5rem;">${data.description}</p>
        `;
        eventsContainer.prepend(div);
        
        // Keep DOM clean
        if (eventsContainer.children.length > 20) {
            eventsContainer.removeChild(eventsContainer.lastChild);
        }
    } catch (e) {
        console.error("WS Parse Error", e);
    }
};

ws.onerror = (err) => console.error("WebSocket Error:", err);
ws.onclose = () => console.log("WebSocket Disconnected");

// Initial Load Backup
loadEvents();
