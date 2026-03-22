import cv2
import numpy as np
from typing import List
from collections import defaultdict
from models.vision import Detection

class SpatialAnalyticsEngine:
    def __init__(self):
        self.trajectories = defaultdict(list)
        self.entry_count = 0
        self.exit_count = 0
        self.heatmap_layer = None
        self.queue_zones = [(100, 100, 400, 400)] # Example Wait Zone
        self.queued_objects = {} # Ticker array

    def process_frame(self, frame_np: np.ndarray, detections: List[Detection]) -> np.ndarray:
        if frame_np is None:
            return None
            
        if self.heatmap_layer is None or self.heatmap_layer.shape[:2] != frame_np.shape[:2]:
            self.heatmap_layer = np.zeros_like(frame_np, dtype=np.float32)

        for det in detections:
            if det.track_id is None:
                continue

            cx = int(det.bbox.x + det.bbox.width / 2)
            cy = int(det.bbox.y + det.bbox.height / 2)
            
            # Heatmap Local Accumulation
            self.heatmap_layer[cy, cx] += 15.0 

            # Trajectory Matrix for Line Crossing
            self.trajectories[det.track_id].append((cx, cy))
            if len(self.trajectories[det.track_id]) > 30:
                self.trajectories[det.track_id].pop(0) # cap size
            
            # Virtual Line crossing logic (mock spatial line Y = center view)
            center_y = int(frame_np.shape[0] / 2)
            if len(self.trajectories[det.track_id]) >= 2:
                prev_y = self.trajectories[det.track_id][-2][1]
                curr_y = self.trajectories[det.track_id][-1][1]
                
                if prev_y < center_y and curr_y >= center_y:
                    self.entry_count += 1
                elif prev_y > center_y and curr_y <= center_y:
                    self.exit_count += 1

            # Helmet Detection (Mock PPE heuristics mapping tracking ids to arbitrary rule)
            if det.label == "person":
                has_helmet = (det.track_id % 5) != 0 # 80% have helmets mock
                if has_helmet:
                    cv2.putText(frame_np, "HELMET", (int(det.bbox.x), int(det.bbox.y - 30)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,200,0), 2)
                else:
                    cv2.putText(frame_np, "NO HELMET", (int(det.bbox.x), int(det.bbox.y - 30)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)

        # Apply global heatmap thermal decay over time
        self.heatmap_layer = self.heatmap_layer * 0.95
        
        # Parse overlay mapping
        heatmap_norm = np.clip(self.heatmap_layer, 0, 255).astype(np.uint8)
        heatmap_color = cv2.applyColorMap(heatmap_norm, cv2.COLORMAP_JET)
        
        # Smart Blend keeping 0 values unaffected
        mask = (heatmap_norm > 5).any(axis=2)
        if np.any(mask):
            frame_np[mask] = cv2.addWeighted(frame_np[mask], 0.6, heatmap_color[mask], 0.4, 0)
        
        # Render the Virtual Crossing Boundary 
        center_y = int(frame_np.shape[0] / 2)
        cv2.line(frame_np, (0, center_y), (frame_np.shape[1], center_y), (0, 200, 255), 2, cv2.LINE_AA)
        
        # Render Telemetry overlay
        cv2.putText(frame_np, f"[TELEMETRY] LINE IN: {self.entry_count} | LINE OUT: {self.exit_count}", (10, center_y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return frame_np

spatial_analytics_global = SpatialAnalyticsEngine()
