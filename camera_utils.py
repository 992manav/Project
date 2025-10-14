import cv2
import sys
import time

def initialize_camera():
    print("\nOpening camera...")
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("✗ Cannot open camera 0, trying camera 1...")
        cap = cv2.VideoCapture(1)
        if not cap.isOpened():
            print("✗ Could not open any camera")
            sys.exit(1)
    print("✓ Camera opened successfully!")
    return cap

def show_frame(window_name, frame, fps, frame_count, alerts, alert_system, detected_objects):
    cv2.rectangle(frame, (5, 5), (350, 150), (0, 0, 0), -1)
    cv2.putText(frame, f'FPS: {int(fps)}', (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(frame, f'Frame: {frame_count}', (15, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, f'Alerts Sent: {alerts}', (15, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    time_since_last_alert = time.time() - alert_system.last_alert_time
    if time_since_last_alert < alert_system.cooldown:
        cooldown_remaining = alert_system.cooldown - time_since_last_alert
        cv2.putText(frame, f'Cooldown: {cooldown_remaining:.1f}s', (15, 125),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)

    if detected_objects:
        # Extract unique class names for display
        detected_class_names = list(set([obj['class_name'].replace('_0', '').replace('_detection', '').replace('_water', '') for obj in detected_objects]))
        status_text = f">>> {', '.join(detected_class_names).upper()} DETECTED! <<<"
        status_color = (0, 0, 255)
        cv2.rectangle(frame, (0, 0), (frame.shape[1]-1, frame.shape[0]-1), (0, 0, 255), 5)
    else:
        status_text = 'Status: Scanning...'
        status_color = (0, 255, 0)

    cv2.putText(frame, status_text, (15, frame.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

    cv2.imshow(window_name, frame)
