import gradio as gr
import requests
import base64
from io import BytesIO
from PIL import Image


def process_vision(image):
    if image is None:
        return None, "No image", "No events"

    # Gradio image is a numpy array (RGB) or PIL depending on type.
    # Convert to PIL then to bytes
    img = Image.fromarray(image)
    buf = BytesIO()
    img.save(buf, format="JPEG")
    img_bytes = buf.getvalue()

    files = {"file": ("webcam.jpg", img_bytes, "image/jpeg")}
    try:
        res = requests.post("http://127.0.0.1:8003/api/v1/process", files=files)
        if res.status_code == 200:
            data = res.json()
            counts_dict = data.get("counts", {})
            b64_img = data.get("annotated_image_base64", "")

            # format the string
            out_str = " | ".join(
                [f"{k.capitalize()}: {v}" for k, v in counts_dict.items()]
            )
            if not out_str:
                out_str = "No objects detected"

            # get events
            events_res = requests.get("http://127.0.0.1:8003/api/v1/events").json()
            events_text = "\n".join(
                [f"[{e['timestamp']}] {e['description']}" for e in events_res]
            )

            out_img = None
            if b64_img:
                out_img = Image.open(BytesIO(base64.b64decode(b64_img)))
            return out_img, out_str, events_text
    except Exception as e:
        return None, f"Error: {e}", ""
    return None, "Server error", ""


def upload_journal(image):
    if image is None:
        return "No image"
    img = Image.fromarray(image)
    buf = BytesIO()
    img.save(buf, format="JPEG")
    files = {"file": ("journal.jpg", buf.getvalue(), "image/jpeg")}
    try:
        res = requests.post("http://127.0.0.1:8001/api/v1/upload", files=files).json()
        return f"Caption: {res['caption']}\nTags: {', '.join(res['tags'])}\nLocation: {res['mock_location']}"
    except Exception as e:
        return f"Error: {e}"


def get_timeline():
    try:
        res = requests.get("http://127.0.0.1:8001/api/v1/timeline").json()
        return "\n\n".join(
            [f"{e['timestamp']}: {e['caption']}" for e in res.get("entries", [])]
        )
    except Exception as e:
        return f"Error: {e}"


def track_usage(app_name, mins):
    try:
        requests.post(
            "http://127.0.0.1:8002/api/v1/track",
            json={"app_name": app_name, "minutes": int(mins)},
        )
        alerts = requests.get("http://127.0.0.1:8002/api/v1/alerts").json()
        return (
            f"Logged {mins} mins for {app_name}. Total Alerts: {len(alerts)}\n"
            + "\n".join([a["message"] for a in alerts])
        )
    except Exception as e:
        return f"Error: {e}"


def start_focus(app_name, mins):
    try:
        res = requests.post(
            "http://127.0.0.1:8002/api/v1/focus",
            json={"app_to_block": app_name, "duration_minutes": int(mins)},
        ).json()
        return f"Started Focus Session! Blocking {res['app_blocked']} for {res['duration_minutes']} mins. Active: {res['is_active']}"
    except Exception as e:
        return f"Error: {e}"


with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# AI Life Automation Suite - Live Demo Interface 🚀")

    with gr.Tab("Visual Intelligence App 👁️"):
        gr.Markdown(
            "Real-time YOLOv8 object detection on your uploaded image or webcam."
        )
        with gr.Row():
            vision_in = gr.Image(
                sources=["webcam", "upload"], label="Input Camera/Image"
            )
            with gr.Column():
                vision_out_img = gr.Image(label="Annotated Output")
                vision_out_stats = gr.Textbox(label="Detection Counts")
                vision_out_events = gr.Textbox(
                    label="Event Engine Logs (e.g. Queue Detected)"
                )

        vision_in.change(
            process_vision,
            inputs=vision_in,
            outputs=[vision_out_img, vision_out_stats, vision_out_events],
        )

    with gr.Tab("Memory Journal App 📔"):
        gr.Markdown("Upload memories to get mock AI captioning, tagging, and location.")
        with gr.Row():
            journal_in = gr.Image(sources=["upload"], label="Upload Memory")
            with gr.Column():
                journal_out = gr.Textbox(label="AI Output")
                timeline_btn = gr.Button("Fetch Timeline")
                timeline_out = gr.Textbox(label="Timeline History")

        journal_in.upload(upload_journal, inputs=journal_in, outputs=journal_out)
        timeline_btn.click(get_timeline, outputs=timeline_out)

    with gr.Tab("Doomscroll Breaker App 📵"):
        gr.Markdown(
            "Track usage of addictive apps, receive alerts, and initiate focus sessions."
        )
        with gr.Row():
            with gr.Column():
                app_input = gr.Textbox(value="Instagram", label="App Name")
                mins_input = gr.Number(value=30, label="Minutes Used")
                track_btn = gr.Button("Log Usage")
                track_out = gr.Textbox(label="Alerts & Status")
            with gr.Column():
                focus_app = gr.Textbox(value="Instagram", label="App to Block")
                focus_mins = gr.Number(value=60, label="Session Duration (mins)")
                focus_btn = gr.Button("Start Focus Session")
                focus_out = gr.Textbox(label="Focus Status")

        track_btn.click(track_usage, inputs=[app_input, mins_input], outputs=track_out)
        focus_btn.click(start_focus, inputs=[focus_app, focus_mins], outputs=focus_out)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
