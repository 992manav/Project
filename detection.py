from ultralytics import YOLO
import numpy as np

class PotholeDetector:
    def __init__(self, model_path):
        print("\nLoading YOLO model...")
        self.model = YOLO(model_path)
        self.detection_count = 0
        self.validate_model()

    def validate_model(self):
        dummy_frame = np.zeros((640, 640, 3), dtype=np.uint8)
        _ = self.model.predict(dummy_frame, conf=0.5, verbose=False)
        print("✓ Model validation successful!")

    def detect(self, frame):
        return self.model.predict(frame, conf=0.5, verbose=False)

    def annotate(self, frame, results):
        annotated_frame = results[0].plot()
        pothole_detected = False
        high_confidence = False
        max_confidence = 0

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = self.model.names[cls]
                if 'pothole' in class_name.lower():
                    pothole_detected = True
                    self.detection_count += 1
                    max_confidence = max(max_confidence, conf)
                    if conf > 0.65:
                        high_confidence = True
                    print(f"🚨 POTHOLE DETECTED! | Confidence: {conf*100:.1f}%")

        return annotated_frame, pothole_detected, high_confidence, max_confidence
