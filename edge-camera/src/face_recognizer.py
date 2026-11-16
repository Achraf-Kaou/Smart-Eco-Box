"""
face_recognizer.py – Optimized facial recognition for Smart Eco-Box
"""
import os
import cv2
import numpy as np
import face_recognition
from typing import List, Tuple
from .base_detector import BaseDetector


class FaceRecognizer(BaseDetector):
    def __init__(self, known_faces_dir: str = "models/known_faces", tolerance: float = 0.5,
                 process_every_n_frames: int = 2, scale: float = 0.5):
        super().__init__(process_every_n_frames=process_every_n_frames, scale=scale)
        self.tolerance = tolerance
        self.known_face_encodings: List[np.ndarray] = []
        self.known_face_names: List[str] = []
        self._load_known_faces(known_faces_dir)

    def _load_known_faces(self, folder: str):
        if not os.path.exists(folder):
            print(f"[WARNING] Folder '{folder}' does not exist. Creating it...")
            os.makedirs(folder, exist_ok=True)
            return
        print(f"Loading known faces from: {folder}")
        for filename in os.listdir(folder):
            if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                path = os.path.join(folder, filename)
                name = os.path.splitext(filename)[0]
                image = face_recognition.load_image_file(path)
                # num_jitters=0 -> faster encoding at load time
                encodings = face_recognition.face_encodings(image, num_jitters=0)
                if encodings:
                    self.known_face_encodings.append(encodings[0])
                    self.known_face_names.append(name)
                    print(f"  ✓ Loaded: {name}")
                else:
                    print(f"  ✗ No face found in: {filename}")
        print(f"Total known faces loaded: {len(self.known_face_names)}\n")

    def recognize(self, frame) -> List[Tuple[str, Tuple[int, int, int, int]]]:
        if not self._should_process():
            return self._cached()
        small = self._resize(frame)
        rgb_small = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        # HOG is much faster than CNN on CPU
        locations = face_recognition.face_locations(rgb_small, model="hog")
        encodings = face_recognition.face_encodings(rgb_small, locations, num_jitters=0)

        results = []
        for (top, right, bottom, left), enc in zip(locations, encodings):
            name = "Unknown"
            if self.known_face_encodings:
                distances = face_recognition.face_distance(self.known_face_encodings, enc)
                best = int(np.argmin(distances))
                if distances[best] <= self.tolerance:
                    name = self.known_face_names[best]
            inv = 1.0 / self.scale
            results.append((name, (
                int(top * inv), int(right * inv), int(bottom * inv), int(left * inv)
            )))
        return self._cache(results)

    def detect(self, frame):
        return self.recognize(frame)

    def draw_results(self, frame, results):
        self.draw(frame, results)

    def draw(self, frame, results):
        for name, (top, right, bottom, left) in results:
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 10),
                        cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1)