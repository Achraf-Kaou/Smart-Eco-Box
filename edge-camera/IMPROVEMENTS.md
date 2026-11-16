# Smart Eco-Box – Edge Camera Improvements

## What is already well done
- Frame skipping in both `FaceRecognizer` and `WasteClassifier` (run inference every N frames, cache last result).
- Face recognition already downscales frames (0.5x) before detection/encoding.
- COCO -> waste category mapping exists, keeping domain-specific labels.
- MQTT client is decoupled (publish/subscribe) with a command callback.
- Decision logic is isolated in `decision.py` and returns a ready-to-publish payload.
- Config is centralized in `config.py` + `.env`.

## What was improved
### Performance
- `Camera` now uses a background capture thread with a size-1 buffer; `read()` returns the latest frame without blocking on the driver. This stabilizes FPS and removes lag.
- Camera sets `CAP_PROP_BUFFERSIZE=1`, MJPEG fourcc, and target FPS; FPS is smoothed with an EMA instead of noisy instantaneous values.
- `FaceRecognizer` defaults to HOG (fast on CPU), `num_jitters=0`, and a configurable skip/scale via `BaseDetector`.
- `WasteClassifier` runs YOLO at `imgsz=320`, `agnostic_nms=True`, `max_det=30`, with per-class confidence thresholds and a minimum box-area filter to drop tiny false positives.
- Shared `BaseDetector` centralizes frame-skip + result caching (less duplicated code, consistent behavior).

### Architecture / code quality
- `BaseDetector` base class for detectors (inheritance + composition).
- `Camera` is a context manager (`with Camera(...) as cam`).
- `register_face.py` now reuses `Camera` instead of a raw `VideoCapture`.
- `decision.py` fixed to use the filtered `valid_waste` list for the best detection and added `Verre` points.

### Waste detection accuracy (pipeline-level)
- Expanded `CLASS_MAPPING` with more COCO aliases and waste-specific names (plastic bottle, can, cardboard, glass, paper).
- Added `Verre` category and color.
- Lowered base confidence to 0.35 and per-class minimums to recover missed items while filtering tiny boxes.
- Allow-list via `target_classes` for faster, focused inference when a custom model is used.

## What still needs improvement (priority)
1. **HIGH – No real waste-trained model.** `yolov8n.pt` is COCO; it cannot reliably detect cans/cardboard/glass as waste. Need a waste-specific dataset/model.
2. **HIGH – Face registration robustness.** `anas.jpg` had no detectable face; validate faces at registration time and store multiple encodings per person.
3. **MEDIUM – Threading safety.** Detectors are called from the main loop only; if moved to worker threads, add locks (BaseDetector already has one for cache).
4. **MEDIUM – No persistence of events.** Events are published only via MQTT; add local queue/retry for offline operation.
5. **LOW – Hard-coded French labels/colors.** Externalize i18n/theme config.
6. **LOW – No tests.** Add unit tests for `decision.build_event` and mapping logic.

## Concrete next steps (better waste accuracy)
1. Collect/label a waste dataset (classes: plastic bottle, aluminum can, cardboard, paper, glass, plastic bag, organic, other) using Roboflow or CVAT; target >= 1k images per class with varied lighting/angles.
2. Fine-tune `yolov8n.pt` (or `yolov8s.pt`) on that dataset: `yolo train data=waste.yaml model=yolov8n.pt imgsz=640 epochs=100`; export to ONNX/OpenVINO for CPU.
3. Or use an open-vocabulary model: download `yolov8n-worldv2.pt` and set `target_classes=["bottle","can","cardboard","paper","glass bottle","plastic bag"]` in `WasteClassifier`; tune text prompts per deployment.
4. Add a second-stage classifier (e.g. a small CNN) on cropped detections to refine material type (plastic vs metal) and reduce COCO confusion.
5. Calibrate confidence thresholds per class from a validation set (precision/recall curves) instead of hand-tuned values.
6. Add temporal smoothing: require the same waste class in >= 2 consecutive processed frames before publishing (reduces flicker).
7. Improve post-processing: per-class NMS, min/max aspect ratio, and reject detections overlapping a person box.
8. Consider exporting the model to OpenVINO/ONNX and using `model.predict(..., device='cpu')` with `half=False`; benchmark `imgsz=320` vs `640`.
9. Track metrics (mAP@0.5, per-class recall) on a held-out test set after each change.

## Suggested architecture (final)
```
Camera (capture, threaded) -> Pipeline (main loop)
  -> FaceRecognizer(BaseDetector)  (HOG, downscaled)
  -> WasteClassifier(BaseDetector) (YOLO, downscaled inference)
  -> Decision.build_event
  -> MQTTClient.publish_event
```
Keep modules independent and testable; inject models/paths via constructor.
"""