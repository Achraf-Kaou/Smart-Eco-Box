"""
decision.py – Simple decision logic for Smart Eco-Box
Prepares the JSON payload when a known user + waste are detected
"""

from datetime import datetime, timezone
from typing import List, Tuple, Dict, Optional
import uuid


def build_event(
    face_results: List[Tuple[str, Tuple[int, int, int, int]]],
    waste_detections: List[Dict]
) -> Optional[Dict]:
    """
    Decision logic:
    - Need at least one known face (not "Unknown")
    - Need at least one waste detection

    Returns a ready-to-publish JSON dict, or None if conditions are not met.
    """

    # 1. Find known faces
    known_faces = [name for name, _ in face_results if name != "Unknown"]

    if not known_faces:
        return None

    # Keep only detections that are not "Non Recyclable" if possible
    valid_waste = [d for d in waste_detections if d["class"] != "Non Recyclable"]

    if not valid_waste:
        # If only Non Recyclable objects are present, we can still accept them
        valid_waste = waste_detections
        
    # 2. Need at least one waste object
    if not waste_detections:
        return None

    # Take the first known person and the highest-confidence waste
    user_name = known_faces[0]
    best_waste = max(waste_detections, key=lambda x: x["confidence"])

    # Build the event (ready for MQTT)
    event = {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_name.lower().replace(" ", "_"),
        "user_name": user_name,
        "waste_type": best_waste["class"],
        "confidence": round(best_waste["confidence"], 3),
        "original_class": best_waste.get("original_class", ""),
        "points": _calculate_points(best_waste["class"])
    }

    return event


def _calculate_points(waste_type: str) -> int:
    """Simple point system (can be improved later)."""
    points_table = {
        "Plastique": 10,
        "Métal": 15,
        "Papier / Carton": 8,
        "Non Recyclable": 0
    }
    return points_table.get(waste_type, 0)