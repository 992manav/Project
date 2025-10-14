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
        _ = self.model.predict(dummy_frame, conf=0.25, verbose=False)
        print("✓ Model validation successful!")

    def detect(self, frame):
        return self.model.predict(frame, conf=0.35, verbose=False)

    def annotate(self, frame, results):
        annotated_frame = results[0].plot()
        detected_objects = []

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = self.model.names[cls]
                
                self.detection_count += 1 # Increment for any detection
                detected_objects.append({'class_name': class_name, 'confidence': conf})
                print(f"🚨 {class_name.upper()} DETECTED! | Confidence: {conf*100:.1f}%")

        return annotated_frame, detected_objects
