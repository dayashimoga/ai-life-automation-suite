import requests
import base64
import os

ARTIFACT_DIR = r"C:\Users\dayan\.gemini\antigravity\brain\73c473bb-d1a8-4901-8e3d-6e3be44acb7f"

print("Sending busy_street.jpg to Visual Intelligence API...")
with open("busy_street.jpg", "rb") as f:
    res = requests.post("http://127.0.0.1:8003/api/v1/process", files={"file": f})

data = res.json()
print("Counts:", data.get("counts"))

b64 = data.get("annotated_image_base64")
if b64:
    out_path = os.path.join(ARTIFACT_DIR, "annotated_street.jpg")
    with open(out_path, "wb") as f_out:
        f_out.write(base64.b64decode(b64))
    print(f"Saved annotated image to: {out_path}")
else:
    print("No annotated image returned.")
