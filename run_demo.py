import subprocess
import time
import urllib.request
import urllib.parse
import json
import os


def post_json(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())


def get_json(url):
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read().decode())


def post_multipart(url, filename, file_content):
    import uuid

    boundary = uuid.uuid4().hex
    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}

    body = (
        (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            f"Content-Type: image/jpeg\r\n\r\n"
        ).encode("utf-8")
        + file_content
        + f"\r\n--{boundary}--\r\n".encode("utf-8")
    )

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())


print("Starting apps for demo...")
apps = [
    {"name": "memory-journal-app", "port": 8001, "env": os.environ.copy()},
    {"name": "doomscroll-breaker-app", "port": 8002, "env": os.environ.copy()},
    {
        "name": "visual-intelligence-app",
        "port": 8003,
        "env": {**os.environ.copy(), "EVENT_THRESHOLD": "1"},
    },  # set threshold to 1 so mock detection triggers it
    {"name": "micro-habit-engine", "port": 8004, "env": os.environ.copy()},
    {"name": "unified-dashboard-app", "port": 8005, "env": os.environ.copy()},
]

processes = []
for app in apps:
    app_dir = f"apps/{app['name']}"

    venv_dir = os.path.join(app_dir, ".venv_tmp")
    py_bin = os.path.join(venv_dir, "Scripts", "python.exe")
    
    if not os.path.exists(py_bin):
        print(f"Creating venv for {app['name']}...")
        subprocess.run(["python", "-m", "venv", ".venv_tmp"], cwd=app_dir)
        print(f"Installing requirements for {app['name']}...")
        subprocess.run([py_bin, "-m", "pip", "install", "-q", "-r", "requirements.txt"], cwd=app_dir)
        
    p = subprocess.Popen(
        [py_bin, "-m", "uvicorn", "main:app", "--port", str(app["port"])],
        cwd=app_dir,
        env=app["env"],
    )
    processes.append(p)

time.sleep(20)  # wait for boot
print("\n=== DEMO TIME ===\n")

try:
    print("1) Testing Memory Journal App (Port 8001)")
    print("-> Uploading 'vacation.jpg'...")
    res1 = post_multipart(
        "http://127.0.0.1:8001/api/v1/journal/upload", "vacation.jpg", b"fake_image_bytes"
    )
    print("   Upload Response:", json.dumps(res1, indent=2))

    print("-> Fetching timeline...")
    res2 = get_json("http://127.0.0.1:8001/api/v1/journal/timeline")
    print("   Timeline Total:", res2["total"])
    if res2["total"] > 0:
        print("   Timeline First Entry Caption:", res2["entries"][0]["caption"])

    print("\n2) Testing Doomscroll Breaker App (Port 8002)")
    print("-> Logging 30 mins usage on Instagram...")
    post_json(
        "http://127.0.0.1:8002/api/v1/usage/track", {"app_name": "Instagram", "minutes": 30}
    )

    print("-> Logging 40 mins usage on Instagram (Triggers Alert)...")
    post_json(
        "http://127.0.0.1:8002/api/v1/usage/track", {"app_name": "Instagram", "minutes": 40}
    )

    print("-> Fetching alerts...")
    alerts = get_json("http://127.0.0.1:8002/api/v1/usage/alerts")
    print("   Alerts count:", len(alerts))
    if alerts:
        print("   Alert message:", alerts[0]["message"])

    print("-> Starting Focus Session blocking Instagram...")
    res_focus = post_json(
        "http://127.0.0.1:8002/api/v1/usage/focus",
        {"duration_minutes": 60, "app_to_block": "Instagram"},
    )
    print(
        "   Focus session started for app:",
        res_focus["app_blocked"],
        "- Active:",
        res_focus["is_active"],
    )

    print("\n3) Testing Visual Intelligence App (Port 8003)")
    print("-> Processing CCTV Frame...")
    img_data = b"fake_frame_bytes"
    if os.path.exists("busy_street.jpg"):
        with open("busy_street.jpg", "rb") as f:
            img_data = f.read()

    res_cv = post_multipart(
        "http://127.0.0.1:8003/api/v1/vision/process", "frame.jpg", img_data
    )
    print(
        "   Counts:",
        res_cv["counts"].get("person", 0),
        "people,",
        res_cv["counts"].get("vehicle", 0),
        "vehicles",
    )

    print("-> Checking for Queue Detection Events (Threshold=1)...")
    events = get_json("http://127.0.0.1:8003/api/v1/vision/events")
    print("   Events count:", len(events))
    if events:
        print("   Event type:", events[0]["event_type"], "-", events[0]["description"])

    print("\n=== DEMO SUCCESSFUL ===")
    print("SERVERS RUNNING INDEFINITELY on Ports 8001-8005. Waiting for browser demo...")
    while True:
        time.sleep(100)

except Exception as e:
    print(f"\nDemo failed: {e}")
    for p in processes:
        p.terminate()
