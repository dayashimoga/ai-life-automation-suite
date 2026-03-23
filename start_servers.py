import subprocess
import time
import os

# Define applications and their target ports
APPS = {
    "unified-dashboard-app": 8000,
    "memory-journal-app": 8001,
    "doomscroll-breaker-app": 8002,
    "visual-intelligence-app": 8003,
    "micro-habit-engine": 8004,
}

# Original apps_config with environment variables (kept for now, as the instruction only modified APPS)
apps_config = [
    ("memory-journal-app", 8001, os.environ.copy()),
    ("doomscroll-breaker-app", 8002, os.environ.copy()),
    ("visual-intelligence-app", 8003, dict(os.environ, EVENT_THRESHOLD="3")),
    ("micro-habit-engine", 8004, os.environ.copy()),
    ("unified-dashboard-app", 8005, os.environ.copy()),
]

for name, port, env_dict in apps_config:

    app_dir = os.path.join(os.getcwd(), f"apps/{name}")
    py_bin = os.path.join(app_dir, ".venv_tmp", "Scripts", "python.exe")
    if not os.path.exists(py_bin):
        print(f"venv not found in {app_dir}. Skipping?")

    subprocess.Popen(
        [py_bin, "-m", "uvicorn", "main:app", "--port", str(port)],
        cwd=app_dir,
        env=env_dict,
    )

print("Starting Gradio... (assuming visual-intelligence-app venv has gradio installed)")
py_bin_vis = os.path.join(
    os.getcwd(), "apps/visual-intelligence-app/.venv_tmp/Scripts/python.exe"
)
subprocess.Popen([py_bin_vis, "gradio_ui.py"])

print("All servers running. Waiting for them to boot...")
time.sleep(10)
print("Ready on http://127.0.0.1:7860")
# Sleep forever
while True:
    time.sleep(100)
