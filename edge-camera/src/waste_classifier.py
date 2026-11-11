"""
waste_classifier.py – Optimized waste classification for Smart Eco-Box
Uses YOLOv8 Nano + frame skipping for better FPS
"""

from ultralytics import YOLO
import cv2
import numpy as np
from typing import List, Dict


class WasteClassifier:
    def __init__(self, model_path: str = "yolov8n.pt", conf_threshold: float = 0.45):
        print("Loading YOLOv8 Nano model...")
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold

        # Optimization variables (same strategy as face recognition)
        self.frame_count = 0
        self.process_every_n_frames = 3          # Process only 1 out of 3 frames
        self.last_detections = []                # Keep last results

        # Mapping COCO → our waste categories
        self.class_mapping = {
            "bottle": "Plastique",
            "cup": "Plastique",
            "wine glass": "Plastique",
            "fork": "Métal",
            "knife": "Métal",
            "spoon": "Métal",
            "book": "Papier / Carton",
        }

        self.ignored_classes = { "person" }  # Ignore people in waste detection

        self.colors = {
            "Plastique": (255, 150, 0),
            "Métal": (0, 255, 255),
            "Papier / Carton": (255, 0, 150),
            "Non Recyclable": (0, 0, 255),
            "Unknown": (180, 180, 180)
        }

        print("YOLOv8 model loaded successfully.\n")

    def classify(self, frame: np.ndarray) -> List[Dict]:
        """
        Optimized classification – runs heavy inference only every N frames.
        """
        self.frame_count += 1

        # Skip heavy processing on most frames
        if self.frame_count % self.process_every_n_frames != 0:
            return self.last_detections

        results = self.model(frame, conf=self.conf_threshold, verbose=False)[0]

        detections = []

        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = results.names[cls_id]

            if class_name in self.ignored_classes:
                continue

            waste_class = self.class_mapping.get(class_name, "Non Recyclable")

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            detections.append({
                "class": waste_class,
                "confidence": conf,
                "original_class": class_name,
                "box": (x1, y1, x2, y2)
            })

        self.last_detections = detections
        return detections

    def draw_detections(self, frame: np.ndarray, detections: List[Dict]):
        for det in detections:
            x1, y1, x2, y2 = det["box"]
            label = f"{det['class']} {det['confidence']:.2f}"
            color = self.colors.get(det["class"], (180, 180, 180))

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(frame, (x1, y1 - 25), (x1 + w, y1), color, -1)
            cv2.putText(frame, label, (x1, y1 - 7),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)