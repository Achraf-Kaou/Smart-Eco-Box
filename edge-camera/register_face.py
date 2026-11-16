"""
register_face.py
Helper script to capture a face from the webcam and save it
into models/known_faces/ for later recognition.
"""
import os
import cv2
from datetime import datetime
from src.camera import Camera


def register_face():
    print("=== Smart Eco-Box – Face Registration ===")
    name = input("Enter the person's name (no spaces preferred): ").strip()

    if not name:
        print("Name cannot be empty.")
        return

    save_dir = "models/known_faces"
    os.makedirs(save_dir, exist_ok=True)
    filename = f"{name}.jpg"
    save_path = os.path.join(save_dir, filename)

    try:
        cam = Camera(camera_index=0, width=640, height=480)
    except RuntimeError as e:
        print(f"Error: {e}")
        return

    print("\nInstructions:")
    print("  - Look at the camera")
    print("  - Press 's' to SAVE the photo")
    print("  - Press 'q' to QUIT without saving\n")

    try:
        while True:
            success, frame = cam.read()
            if not success or frame is None:
                continue

            h, w = frame.shape[:2]
            cv2.rectangle(frame, (w // 4, h // 6), (3 * w // 4, 5 * h // 6), (0, 255, 0), 2)
            cv2.putText(frame, "Position your face inside the box", (30, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "Press 's' to save  |  'q' to quit", (30, h - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            cv2.imshow("Register Face - Smart Eco-Box", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("s"):
                cv2.imwrite(save_path, frame)
                print(f"\n✓ Face saved successfully as: {save_path}")
                break
            elif key == ord("q"):
                print("\nRegistration cancelled.")
                break
    finally:
        cam.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    register_face()