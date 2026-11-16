"""
camera.py – Real-time video capture module for Smart Eco-Box

Threaded capture keeps the latest frame ready, avoiding blocking reads and
reducing perceived latency. Buffers are kept at size 1 to avoid stale frames.
"""
import cv2
import threading
import time
from typing import Optional, Tuple


class Camera:
    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480,
                 fps: int = 30, threaded: bool = True):
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera index {camera_index}")

        # Low-latency settings
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        # MJPEG reduces USB bandwidth / latency on many webcams
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

        self.width = width
        self.height = height

        # FPS (smoothed)
        self._prev_time = time.time()
        self.fps = 0.0
        self._alpha = 0.1

        # Threaded capture state
        self._threaded = threaded
        self._latest = None
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        if threaded:
            self._running = True
            self._thread = threading.Thread(target=self._capture_loop, daemon=True)
            self._thread.start()

    def _capture_loop(self):
        while self._running:
            ok, frame = self.cap.read()
            if ok:
                with self._lock:
                    self._latest = frame
            else:
                time.sleep(0.005)

    def read(self):
        if not self._threaded:
            return self.cap.read()
        with self._lock:
            frame = self._latest
        if frame is None:
            return False, None
        return True, frame.copy()

    def update_fps(self) -> float:
        now = time.time()
        dt = now - self._prev_time
        if dt > 0:
            instant = 1.0 / dt
            self.fps = instant if self.fps == 0 else (self._alpha * instant + (1 - self._alpha) * self.fps)
        self._prev_time = now
        return self.fps

    def release(self):
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=1.0)
        self.cap.release()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.release()
        return False