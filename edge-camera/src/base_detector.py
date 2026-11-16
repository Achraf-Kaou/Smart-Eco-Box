"""
base_detector.py – Shared base for frame-skipping detectors (composition/inheritance).
"""
import threading
import time
from typing import Any, List


class BaseDetector:
    """Common frame-skip + result-cache machinery for detectors."""

    def __init__(self, process_every_n_frames: int = 2, scale: float = 1.0):
        self.process_every_n_frames = max(1, int(process_every_n_frames))
        self.scale = float(scale)
        self.frame_count = 0
        self._last_results: List[Any] = []
        self._lock = threading.Lock()
        self._last_process_time = time.time()

    def _should_process(self) -> bool:
        with self._lock:
            self.frame_count += 1
            return self.frame_count % self.process_every_n_frames == 0

    def _cache(self, results: List[Any]) -> List[Any]:
        with self._lock:
            self._last_results = results
            self._last_process_time = time.time()
        return results

    def _cached(self) -> List[Any]:
        with self._lock:
            return list(self._last_results)

    def _resize(self, frame):
        if self.scale == 1.0:
            return frame
        import cv2
        return cv2.resize(frame, (0, 0), fx=self.scale, fy=self.scale)

    def detect(self, frame):
        raise NotImplementedError

    def draw(self, frame, results):
        raise NotImplementedError