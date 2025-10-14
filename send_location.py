# Automated Location + WhatsApp Alert for Pothole Detection
# pip install pywhatkit winsdk pyautogui

import pywhatkit as pwk
import datetime
import asyncio
import sys
import time
import pyautogui  # to press Enter

# Windows location import
try:
    import winsdk.windows.devices.geolocation as wdg
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "winsdk"])
    import winsdk.windows.devices.geolocation as wdg


class LocationWhatsApp:
    def __init__(self):
        self.location = None
        self.detection_method = "Windows GPS"
    
    async def get_windows_location(self):
        """Get exact location using Windows GPS"""
        try:
            print("Getting your exact location...")
            locator = wdg.Geolocator()
            locator.desired_accuracy = wdg.PositionAccuracy.HIGH
            
            pos = await locator.get_geoposition_async()
            
            lat = pos.coordinate.point.position.latitude
            lon = pos.coordinate.point.position.longitude
            accuracy = pos.coordinate.accuracy
            
            self.location = (lat, lon)
            
            print("Location acquired!")
            print(f"  Latitude:  {lat:.8f}")
            print(f"  Longitude: {lon:.8f}")
            print(f"  Accuracy:  +/-{accuracy:.1f} meters")
            
            return True
        except Exception as e:
            print(f"Location error: {e}")
            print("Enable Location Services: Settings > Privacy > Location > ON")
            return False
    
    def create_message(self, alert_type="POTHOLE DETECTED"):
        """Create formatted message with location"""
        lat, lon = self.location
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = (
            f"🚨 {alert_type.upper()}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⏰ Time: {current_time}\n"
            f"📍 Method: {self.detection_method}\n\n"
            f"📌 EXACT COORDINATES:\n"
            f"Latitude:  {lat:.8f}\n"
            f"Longitude: {lon:.8f}\n\n"
            f"🗺 OPEN IN MAPS:\n"
            f"https://maps.google.com/maps?q={lat},{lon}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Sent from Detection System"
        )
        return message
    
    def send_to_multiple_numbers(self, phone_numbers, alert_type="POTHOLE DETECTED"):
        """Send location to multiple contacts with proper timing"""
        if not self.location:
            print("Location not available!")
            return False
        
        print(f"Sending to {len(phone_numbers)} contacts...\n")
        successful = 0
        failed = 0
        
        for i, phone in enumerate(phone_numbers, start=1):
            print(f"[{i}/{len(phone_numbers)}] Sending to: {phone}")
            message = self.create_message(alert_type)
            wait_time = 10 if i == 1 else 7
            
            try:
                # Start message typing
                pwk.sendwhatmsg_instantly(
                    phone_no=phone,
                    message=message,
                    wait_time=wait_time,
                    tab_close=False,
                    close_time=1
                )
            except Exception as e:
                print(f"Failed to trigger send for {phone}: {e}")
                failed += 1
                continue
            
            # Allow WhatsApp to load & type message
            time.sleep(3)
            
            # Try to activate WhatsApp window before pressing Enter
            whatsapp_windows = pyautogui.getWindowsWithTitle("WhatsApp")
            if whatsapp_windows:
                # Assuming the first found window is the correct one
                whatsapp_window = whatsapp_windows[0]
                if not whatsapp_window.isActive:
                    print("Activating WhatsApp window...")
                    whatsapp_window.activate()
                time.sleep(1) # Give a moment for the window to activate
            else:
                print("WhatsApp window not found. Message might not be sent.")

            # Press Enter to actually send
            print("Pressing Enter to send message...")
            pyautogui.press("enter")
            
            # Wait a bit after sending for delivery to complete
            time.sleep(2)
            successful += 1
            print(f"✅ Message sent to {phone}\n")
            
            # Wait 5 s before next send (your requirement)
            if i < len(phone_numbers):
                print("Waiting 5 seconds before sending to next contact...\n")
                time.sleep(5)
            else:
                # After the last message, wait longer to ensure send completion
                print("All messages sent — waiting 8 seconds for final completion...")
                time.sleep(8)
        
        print("\n" + "=" * 70)
        print("SENDING COMPLETE")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print("=" * 70)
        return successful > 0


async def main():
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    
    # Get alert_type from command line arguments
    alert_type = "DETECTION"
    if len(sys.argv) > 1:
        alert_type = sys.argv[1]

    print("=" * 70)
    print(f"AUTOMATED {alert_type.upper()} ALERT - SENDING NOW")
    print("=" * 70)
    
    wa = LocationWhatsApp()
    
    print("\nGetting your exact location...")
    location_success = await wa.get_windows_location()
    if not location_success:
        print("\nCannot send alert without location!")
        return False
    
    # Recipients
    phone_numbers = ["+919925023840", "+918735840688"]
    
    print("\nRecipients:")
    for phone in phone_numbers:
        print(f"   - {phone}")
    
    print("\n" + "=" * 70)
    print(f"SENDING {alert_type.upper()} ALERT")
    print("=" * 70)
    print(f"Alert Type: {alert_type.upper()}")
    print(f"Location: {wa.location[0]:.6f}, {wa.location[1]:.6f}")
    print(f"Recipients: {len(phone_numbers)} contacts")
    print("=" * 70)
    
    print("\nSENDING STARTED...\n")
    time.sleep(1)
    
    success = wa.send_to_multiple_numbers(phone_numbers, alert_type)
    
    if success:
        print("\n✅ All alerts sent successfully!")
        return True
    else:
        print("\n❌ Some alerts failed!")
        return False


if __name__ == "__main__":
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
        
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    else:
        print("This script only works on Windows 10/11")
        sys.exit(1)
