"""
camera.py – Real-time video capture module for Smart Eco-Box
"""

import cv2
import time


class Camera:
    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480):
        """
        Initialize the webcam.

        Args:
            camera_index: Usually 0 for the built-in webcam
            width, height: Desired resolution (lower = faster)
        """
        self.cap = cv2.VideoCapture(camera_index)

        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera index {camera_index}")

        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        # For FPS calculation
        self.prev_time = time.time()
        self.fps = 0

    def read(self):
        """
        Read one frame from the camera.
        Returns:
            success (bool), frame (numpy array)
        """
        success, frame = self.cap.read()
        return success, frame

    def update_fps(self):
        """Calculate and store current FPS."""
        current_time = time.time()
        self.fps = 1 / (current_time - self.prev_time + 1e-6)  # avoid division by zero
        self.prev_time = current_time
        return self.fps

    def release(self):
        """Release the camera resource."""
        self.cap.release()