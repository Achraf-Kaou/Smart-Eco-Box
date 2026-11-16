"""
waste_classifier.py – Waste detection for Smart Eco-Box

Uses YOLOv8 Nano by default. Accuracy improvements:
- broader COCO -> waste mapping
- lower base confidence + per-class thresholds
- minimum box area filter (removes tiny false positives)
- NMS / agnostic NMS, capped detections
- inference at imgsz=320 for CPU speed
- frame skipping + cached results

For real waste accuracy, swap model_path for a waste-trained model or a
YOLO-World checkpoint and set target_classes (see IMPROVEMENTS.md).
"""
from ultralytics import YOLO
import cv2
import numpy as np
from typing import List, Dict, Optional
from .base_detector import BaseDetector


class WasteClassifier(BaseDetector):
    # Mapping from detector class names (COCO or waste-specific) to our categories
    CLASS_MAPPING = {
        # COCO -> waste
        "bottle": "Plastique",
        "cup": "Plastique",
        "wine glass": "Plastique",
        "fork": "Métal",
        "knife": "Métal",
        "spoon": "Métal",
        "book": "Papier / Carton",
        "cardboard": "Papier / Carton",
        # waste-specific aliases (for custom / YOLO-World models)
        "plastic_bottle": "Plastique",
        "pet_bottle": "Plastique",
        "plastic_bag": "Plastique",
        "aluminum_can": "Métal",
        "tin_can": "Métal",
        "can": "Métal",
        "cardboard_box": "Papier / Carton",
        "paper": "Papier / Carton",
        "newspaper": "Papier / Carton",
        "glass_bottle": "Verre",
        "glass": "Verre",
        "jar": "Verre",
    }

    def __init__(self, model_path: str = "yolov8n.pt", conf_threshold: float = 0.35,
                 process_every_n_frames: int = 2, scale: float = 1.0, imgsz: int = 320,
                 target_classes: Optional[List[str]] = None):
        super().__init__(process_every_n_frames=process_every_n_frames, scale=scale)
        print("Loading YOLO model...")
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.imgsz = imgsz
        self.iou = 0.45
        self.target_classes = target_classes  # optional COCO-name allow-list
        self.class_mapping = dict(self.CLASS_MAPPING)
        self.ignored_classes = {"person"}
        # per-category minimum confidence (reduces false positives)
        self.min_conf = {
            "Plastique": 0.30,
            "Métal": 0.30,
            "Papier / Carton": 0.30,
            "Verre": 0.35,
            "Non Recyclable": 0.50,
        }
        self.min_area_ratio = 0.002  # box must be >= 0.2% of frame
        self.colors = {
            "Plastique": (255, 150, 0),
            "Métal": (0, 255, 255),
            "Papier / Carton": (255, 0, 150),
            "Verre": (255, 255, 0),
            "Non Recyclable": (0, 0, 255),
            "Unknown": (180, 180, 180),
        }
        print("YOLO model loaded successfully.\n")

    def classify(self, frame) -> List[Dict]:
        if not self._should_process():
            return self._cached()
        h, w = frame.shape[:2]
        frame_area = h * w
        results = self.model.predict(
            frame, conf=self.conf_threshold, iou=self.iou, imgsz=self.imgsz,
            verbose=False, agnostic_nms=True, max_det=30,
        )[0]

        detections: List[Dict] = []
        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = results.names[cls_id]

            if class_name in self.ignored_classes:
                continue
            if self.target_classes is not None and class_name not in self.target_classes:
                continue

            waste_class = self.class_mapping.get(class_name, "Non Recyclable")
            if conf < self.min_conf.get(waste_class, self.conf_threshold):
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            if (x2 - x1) * (y2 - y1) < frame_area * self.min_area_ratio:
                continue

            detections.append({
                "class": waste_class,
                "confidence": conf,
                "original_class": class_name,
                "box": (x1, y1, x2, y2),
            })

        detections.sort(key=lambda d: d["confidence"], reverse=True)
        return self._cache(detections)

    def detect(self, frame):
        return self.classify(frame)

    def draw_detections(self, frame, detections):
        self.draw(frame, detections)

    def draw(self, frame, detections):
        for det in detections:
            x1, y1, x2, y2 = det["box"]
            label = f"{det['class']} {det['confidence']:.2f}"
            color = self.colors.get(det["class"], (180, 180, 180))
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(frame, (x1, y1 - 25), (x1 + tw, y1), color, -1)
            cv2.putText(frame, label, (x1, y1 - 7),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)