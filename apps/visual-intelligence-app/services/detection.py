import cv2
import numpy as np

from typing import Tuple, List
from models.vision import Detection, BoundingBox
from uuid import uuid4

# Initialize model globally to handle ImportError at module load time
_yolo_model = None
try:
    from ultralytics import YOLO

    _yolo_model = YOLO("yolov8m.pt")  # load pretrained Medium model
except ImportError:
    _yolo_model = None


class RealDetectionModule:
    def __init__(self):
        # We upgraded from yolov8n to yolov8m for better silhouette and contextual accuracy.
        self.model = _yolo_model

    def detect_and_draw(self, image_data: bytes) -> Tuple[List[Detection], np.ndarray]:
        # Decode image
        np_arr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        detections = []
        if self.model and img is not None:
            # Enforce 75% confidence gating to eliminate silhouette hallucinations (like Meerkats -> Horses)
            results = self.model.track(img, persist=True, conf=0.75, tracker="bytetrack.yaml")
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    label = self.model.names[cls]
                    track_id = int(box.id[0]) if box.id is not None else None

                    det = Detection(
                        id=str(uuid4()),
                        track_id=track_id,
                        label=label,
                        confidence=conf,
                        bbox=BoundingBox(x=x1, y=y1, width=x2 - x1, height=y2 - y1),
                    )
                    detections.append(det)

                    # Draw on image
                    cv2.rectangle(
                        img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2
                    )
                    cv2.putText(
                        img,
                        f"{label} {conf:.2f}",
                        (int(x1), int(max(0, y1 - 10))),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2,
                    )
                    
        return detections, img

detection_module = RealDetectionModule()
