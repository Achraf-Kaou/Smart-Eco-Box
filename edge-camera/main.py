"""
main.py – Full pipeline + Simulated Actuator (Visual + Sound)
"""

import cv2
import json
import time
import threading
from src.camera import Camera
from src.face_recognizer import FaceRecognizer
from src.waste_classifier import WasteClassifier
from src.decision import build_event
from src.mqtt_client import MQTTClient

# Optional sound
try:
    from playsound import playsound
    SOUND_AVAILABLE = True
except:
    SOUND_AVAILABLE = False
    print("[INFO] playsound not available – sound disabled")


# Global state for visual feedback
feedback_message = None
feedback_until = 0


def play_success_sound():
    """Play a short success sound in a separate thread"""
    if not SOUND_AVAILABLE:
        return
    try:
        # Put a short .mp3 or .wav file in the project (ex: success.mp3)
        playsound("assets/success.mp3", block=False)
    except Exception as e:
        print(f"[Sound] Error: {e}")


def handle_command(command: dict):
    """Called when backend sends feedback"""
    global feedback_message, feedback_until

    message = command.get("message", "Validation reçue !")
    points = command.get("points", 0)

    print("\n" + "★" * 55)
    print("FEEDBACK FROM BACKEND")
    print(f"→ {message}")
    print(f"→ Points: +{points}")
    print("★" * 55 + "\n")

    # Activate visual feedback for 3 seconds
    feedback_message = f"{message}"
    feedback_until = time.time() + 3.0

    # Play sound
    threading.Thread(target=play_success_sound, daemon=True).start()


def draw_feedback(frame):
    """Draw big success message on the frame"""
    global feedback_message, feedback_until

    if feedback_message and time.time() < feedback_until:
        h, w = frame.shape[:2]

        # Semi-transparent green overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, h//3), (w, 2*h//3), (0, 180, 0), -1)
        cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)

        # Text
        cv2.putText(
            frame,
            feedback_message,
            (40, h//2 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.1,
            (255, 255, 255),
            3
        )
        cv2.putText(
            frame,
            "Actionneur simulé activé",
            (40, h//2 + 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (220, 255, 220),
            2
        )
    else:
        feedback_message = None


def main():
    print("Starting Smart Eco-Box – Full Pipeline + Actuator")
    print("Press 'q' to quit.\n")

    cam = Camera(camera_index=0, width=640, height=480)
    face_recognizer = FaceRecognizer(known_faces_dir="models/known_faces", tolerance=0.5)
    waste_classifier = WasteClassifier(model_path="yolov8n.pt", conf_threshold=0.45)

    mqtt_client = MQTTClient(on_command=handle_command)
    mqtt_client.connect()

    last_event_time = 0
    cooldown_seconds = 4

    try:
        while True:
            success, frame = cam.read()
            if not success:
                break

            # AI
            face_results = face_recognizer.recognize(frame)
            face_recognizer.draw_results(frame, face_results)

            waste_detections = waste_classifier.classify(frame)
            waste_classifier.draw_detections(frame, waste_detections)

            # Decision + Publish
            event = build_event(face_results, waste_detections)
            current_time = time.time()

            if event and (current_time - last_event_time) > cooldown_seconds:
                last_event_time = current_time
                print("\nEVENT → PUBLISHING TO MQTT")
                print(json.dumps(event, indent=2, ensure_ascii=False))
                mqtt_client.publish_event(event)

            # Draw actuator feedback
            draw_feedback(frame)

            # FPS
            fps = cam.update_fps()
            cv2.putText(frame, f"FPS: {int(fps)}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            cv2.imshow("Smart Eco-Box - Actuator", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        mqtt_client.disconnect()
        cam.release()
        cv2.destroyAllWindows()
        print("Closed.")


if __name__ == "__main__":
    main()