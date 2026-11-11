"""
face_recognizer.py – Optimized facial recognition for Smart Eco-Box
"""

import os
import face_recognition
import cv2
import numpy as np
from typing import List, Tuple


class FaceRecognizer:
    def __init__(self, known_faces_dir: str = "models/known_faces", tolerance: float = 0.5):
        self.tolerance = tolerance
        self.known_face_encodings: List[np.ndarray] = []
        self.known_face_names: List[str] = []

        # Optimization variables
        self.frame_count = 0
        self.process_every_n_frames = 3          # Process only 1 out of 3 frames
        self.last_results = []                   # Store last recognition results
        self.scale = 0.5                         # Resize factor (0.5 = half size → much faster)

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
                encodings = face_recognition.face_encodings(image)

                if len(encodings) > 0:
                    self.known_face_encodings.append(encodings[0])
                    self.known_face_names.append(name)
                    print(f"  ✓ Loaded: {name}")
                else:
                    print(f"  ✗ No face found in: {filename}")

        print(f"Total known faces loaded: {len(self.known_face_names)}\n")

    def recognize(self, frame: np.ndarray) -> List[Tuple[str, Tuple[int, int, int, int]]]:
        """
        Optimized recognition:
        - Only runs heavy detection every N frames
        - Works on a smaller resized image
        """
        self.frame_count += 1

        # Skip heavy processing on most frames
        if self.frame_count % self.process_every_n_frames != 0:
            return self.last_results

        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=self.scale, fy=self.scale)
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Detect faces on the small image
        face_locations = face_recognition.face_locations(rgb_small)
        face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

        results = []

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            name = "Unknown"

            if self.known_face_encodings:
                matches = face_recognition.compare_faces(
                    self.known_face_encodings, face_encoding, tolerance=self.tolerance
                )
                face_distances = face_recognition.face_distance(
                    self.known_face_encodings, face_encoding
                )
                best_match_index = np.argmin(face_distances)

                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]

            # Scale coordinates back to original size
            top = int(top / self.scale)
            right = int(right / self.scale)
            bottom = int(bottom / self.scale)
            left = int(left / self.scale)

            results.append((name, (top, right, bottom, left)))

        self.last_results = results
        return results

    def draw_results(self, frame: np.ndarray, results: List[Tuple[str, Tuple[int, int, int, int]]]):
        for name, (top, right, bottom, left) in results:
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(
                frame, name, (left + 6, bottom - 10),
                cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 1
            )