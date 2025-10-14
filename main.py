from detection import PotholeDetector
from camera_utils import initialize_camera, show_frame
from alert_system import AlertSystem
import cv2
import time
from beep import play_beep

def main():
    print("\n" + "="*60)
    print("STARTING MULTI-OBJECT DETECTION SYSTEM WITH LOCATION ALERTS")
    print("="*60)

    # Initialize YOLO detector
    detector = PotholeDetector('best.pt')

    # Initialize camera
    cap = initialize_camera()

    # Initialize alert system
    alert_system = AlertSystem(cooldown=5, detection_threshold=3)

    frame_count = 0
    location_alerts_sent = 0
    prev_time = time.time()

    window_name = '🔴 LIVE OBJECT DETECTION - Press Q to Quit'

    print("\n" + "="*60)
    print("CAMERA FEED WINDOW OPENED")
    print("="*60)
    print("📹 Live camera feed running...")
    print("⚠️ Detecting objects in real-time...")
    print("📍 Location will be sent when NEW object detected")
    print("❌ Press 'Q' to quit")
    print("="*60 + "\n")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("✗ Cannot receive frame from camera")
                break

            frame_count += 1
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
            prev_time = curr_time

            # Run detection
            results = detector.detect(frame)
            annotated_frame, detected_objects = detector.annotate(frame, results)

            # Check and trigger alert
            should_send_alert, alert_type = alert_system.should_alert(detected_objects)
            if should_send_alert:
                if alert_type == 'SPEED_BREAKER':
                    print(f"\n{'='*60}")
                    print(f"🚨 NEW {alert_type} CONFIRMED! Playing beep sound.")
                    print(f"{'='*60}")
                    play_beep()
                else:
                    print(f"\n{'='*60}")
                    print(f"🚨 NEW {alert_type} CONFIRMED!")
                    print(f"{'='*60}")
                    alert_system.send_alert_async(alert_type)  # ✅ runs in background
                location_alerts_sent += 1         # increment immediately when triggered


            # Display live frame
            show_frame(window_name, annotated_frame, fps, frame_count, location_alerts_sent, alert_system, detected_objects)

            # Quit with Q
            key = cv2.waitKey(1) & 0xFF
            if key in [ord('q'), ord('Q')]:
                break

    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"📊 Total frames processed: {frame_count}")
        print(f"🚨 Total objects detected: {detector.detection_count}")
        print(f"📍 Location alerts sent: {location_alerts_sent}")
        print(f"✓ Camera closed successfully")
        print("="*60 + "\n")

if __name__ == "__main__":
    main()
