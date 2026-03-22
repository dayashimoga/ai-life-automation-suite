const themeToggle = document.getElementById('theme-toggle');
const body = document.body;
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('media-input');
const imagePreview = document.getElementById('image-preview');
const uploadBtn = document.getElementById('upload-btn');
const timelineContainer = document.getElementById('timeline-container');
const refreshBtn = document.getElementById('refresh-btn');
const searchBtn = document.getElementById('search-btn');
const searchInput = document.getElementById('search-input');
const timelineDate = document.getElementById('timeline-date');

let currentFile = null;
let currentBase64 = null;

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

// Drag and Drop logic
dropzone.addEventListener('click', () => fileInput.click());
dropzone.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.style.transform = "scale(1.05)"; });
dropzone.addEventListener('dragleave', () => dropzone.style.transform = "scale(1)");
dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.style.transform = "scale(1)";
    if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
});

fileInput.addEventListener('change', (e) => {
    if(e.target.files.length > 0) {
        currentFile = e.target.files[0];
        if (currentFile.type.startsWith('video/')) {
            imagePreview.src = "https://cdn-icons-png.flaticon.com/512/3172/3172564.png";
            imagePreview.classList.remove('hidden');
            dropzone.classList.add('hidden');
            uploadBtn.style.display = 'block';
        } else {
            const reader = new FileReader();
            reader.onload = (event) => {
                currentBase64 = event.target.result;
                imagePreview.src = currentBase64;
                imagePreview.classList.remove('hidden');
                dropzone.classList.add('hidden');
                uploadBtn.style.display = 'block';
            };
            reader.readAsDataURL(currentFile);
        }
    }
});

function handleFile(file) {
    currentFile = file;
    if (currentFile.type.startsWith('video/')) {
        imagePreview.src = "https://cdn-icons-png.flaticon.com/512/3172/3172564.png";
        imagePreview.classList.remove('hidden');
        dropzone.classList.add('hidden');
        uploadBtn.style.display = 'block';
    } else {
        const reader = new FileReader();
        reader.onload = (e) => {
            currentBase64 = e.target.result;
            imagePreview.src = currentBase64;
            imagePreview.classList.remove('hidden');
            dropzone.classList.add('hidden');
            uploadBtn.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
}

// Upload Data
uploadBtn.addEventListener('click', async () => {
    if(!currentFile && !currentBase64) return;
    
    uploadBtn.innerText = "Extracting Metadata & Sentiment...";
    uploadBtn.disabled = true;

    try {
        let res;
        
        if (currentFile && currentFile.type.startsWith('video/')) {
            // Video FormData Flow
            const formData = new FormData();
            formData.append("file", currentFile);
            
            res = await fetch("/api/v1/journal/process_video", {
                method: "POST",
                body: formData
            });
        } else {
            // Standard Image Flow
            res = await fetch("/api/v1/journal/entries", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    text: "Uploading a new memory snippet from UI.",
                    image_base64: currentBase64
                })
            });
        }

        if(res.ok) {
            resetUpload();
            loadTimeline();
        } else {
            const text = await res.text();
            alert("Error saving memory: " + text);
        }
    } catch(err) {
        alert("Fatal Error: " + err.message);
    } finally {
        uploadBtn.innerText = "Journal It ➔";
        uploadBtn.disabled = false;
    }
});

function resetUpload() {
    currentBase64 = null;
    currentFile = null;
    imagePreview.src = '';
    imagePreview.classList.add('hidden');
    dropzone.classList.remove('hidden');
    uploadBtn.style.display = 'none';
}

function renderEntries(entries) {
    timelineContainer.innerHTML = '';
    if(!entries.length) {
        timelineContainer.innerHTML = '<p style="color:var(--text-muted);text-align:center;">No memories found. Start capturing!</p>';
        return;
    }
    entries.forEach(entry => {
        const tagsHtml = entry.tags.map(t => `<span class="tag">#${t}</span>`).join('');
        const dateStr = new Date(entry.timestamp).toLocaleString();
        
        const card = document.createElement('div');
        card.className = 'memory-card';
        card.innerHTML = `
            <div class="memory-meta">
                <span>📍 ${entry.location || 'Unknown'}</span>
                <span>${dateStr}</span>
            </div>
            <p class="memory-caption">"${entry.caption}"</p>
            <div class="tags">${tagsHtml}</div>
        `;
        timelineContainer.appendChild(card);
    });
}

async function loadTimeline() {
    try {
        const res = await fetch("/api/v1/journal/timeline");
        const data = await res.json();
        renderEntries(data.entries.reverse()); // latest first
    } catch(err) { console.error('Failed to load timeline', err); }
}

async function searchTimeline() {
    const q = searchInput.value;
    if(!q) return loadTimeline();
    try {
        const res = await fetch(`/api/v1/journal/search?query=${encodeURIComponent(q)}`);
        const data = await res.json();
        renderEntries(data.entries);
    } catch(err) { console.error('Failed to search timeline', err); }
}

refreshBtn.addEventListener('click', loadTimeline);
searchBtn.addEventListener('click', searchTimeline);
searchInput.addEventListener('keyup', (e) => { if (e.key === 'Enter') searchTimeline(); });

// Init
loadTimeline();
