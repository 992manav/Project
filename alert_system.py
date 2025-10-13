import subprocess
import time
import threading


class AlertSystem:
    def __init__(self, cooldown=5, detection_threshold=3, timeout=90):
        """
        cooldown: minimum time (seconds) between alerts
        detection_threshold: how many consecutive detections before triggering alert
        timeout: maximum time (seconds) for send_location.py to finish
        """
        self.cooldown = cooldown
        self.detection_threshold = detection_threshold
        self.timeout = timeout
        self.last_alert_time = 0
        self.consecutive_detections = 0
        self.sending_in_progress = False  # prevent multiple alerts at once

    def should_alert(self, pothole_detected, high_confidence):
        """Check if an alert should be sent."""
        if pothole_detected and high_confidence:
            self.consecutive_detections += 1
        else:
            self.consecutive_detections = 0

        time_since_last_alert = time.time() - self.last_alert_time

        # Send only if threshold reached, cooldown passed, and no alert is currently sending
        return (
            self.consecutive_detections >= self.detection_threshold
            and time_since_last_alert >= self.cooldown
            and not self.sending_in_progress
        )

    def _run_send_script(self):
        """Internal function to run send_location.py as a subprocess in a background thread."""
        self.sending_in_progress = True
        print("\n" + "🌍" * 20)
        print("📍 [ALERT THREAD] Sending pothole location alert in background...")
        print(f"🕒 Timeout = {self.timeout} seconds")

        try:
            # Run send_location.py (your WhatsApp sending logic)
            result = subprocess.run(
                ['python', 'send_location.py'],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            if result.returncode == 0:
                print("✅ Alert sent successfully!")
                if result.stdout.strip():
                    print(f"   Output: {result.stdout.strip()}")
                self.last_alert_time = time.time()
                self.consecutive_detections = 0
            else:
                print(f"⚠️ Error code {result.returncode}: {result.stderr.strip()}")

        except subprocess.TimeoutExpired:
            print(f"❌ Timeout: send_location.py exceeded {self.timeout} seconds.")
        except Exception as e:
            print(f"❌ Error while sending alert: {e}")
        finally:
            print("🌍" * 20 + "\n")
            self.sending_in_progress = False

    def send_alert_async(self):
        """Launch send_location.py in a separate background thread."""
        thread = threading.Thread(target=self._run_send_script, daemon=True)
        thread.start()
        print("🚀 Alert thread started (main detection continues...)")


def main():
    # Create alert system (you can tune cooldown & timeout here)
    alert_system = AlertSystem(cooldown=10, detection_threshold=3, timeout=90)

    print("\n🚗 Starting pothole monitoring system...")
    print("--------------------------------------------------")

    while True:
        # 🔹 Replace with your actual detection logic:
        pothole_detected = True         # Example: sensor/model detection result
        high_confidence = True          # Example: confidence > threshold

        # Check if we should send an alert
        if alert_system.should_alert(pothole_detected, high_confidence):
            alert_system.send_alert_async()

        # Simulate ongoing processing (e.g., ML inference)
        print("🔎 Monitoring road... (main thread alive)")
        time.sleep(1)  # simulate frame processing delay


if __name__ == "__main__":
    main()
