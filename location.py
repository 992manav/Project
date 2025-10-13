# METHOD 1: Using Windows COM API (Built-in, No installation needed!)
import asyncio
import sys

# Check if on Windows
if sys.platform != 'win32':
    print("This script only works on Windows")
    sys.exit(1)

try:
    import winsdk.windows.devices.geolocation as wdg
except ImportError:
    print("Installing required package...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "winsdk"])
    import winsdk.windows.devices.geolocation as wdg


async def get_exact_location():
    """
    Get exact GPS location using Windows native geolocation API.
    No external packages needed except winsdk.
    """
    try:
        # Request access to location
        locator = wdg.Geolocator()
        
        # Get current position
        pos = await locator.get_geoposition_async()
        
        return {
            'latitude': pos.coordinate.point.position.latitude,
            'longitude': pos.coordinate.point.position.longitude,
            'accuracy': pos.coordinate.accuracy,
            'altitude': pos.coordinate.point.position.altitude,
            'timestamp': pos.coordinate.timestamp
        }
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure Location Services are enabled:")
        print("Settings > Privacy > Location > ON")
        return None


async def track_location_continuous(duration=30):
    """
    Track location continuously for better accuracy.
    """
    print(f"Tracking location for {duration} seconds...\n")
    
    locator = wdg.Geolocator()
    locator.desired_accuracy = wdg.PositionAccuracy.HIGH
    
    locations = []
    
    try:
        for i in range(duration // 2):
            pos = await locator.get_geoposition_async()
            location = {
                'latitude': pos.coordinate.point.position.latitude,
                'longitude': pos.coordinate.point.position.longitude,
                'accuracy': pos.coordinate.accuracy
            }
            locations.append(location)
            print(f"📍 Reading {i+1}: Lat={location['latitude']:.6f}, Lon={location['longitude']:.6f}, Acc=±{location['accuracy']:.1f}m")
            await asyncio.sleep(2)
    except Exception as e:
        print(f"Error during tracking: {e}")
    
    if locations:
        # Return most accurate reading
        best = min(locations, key=lambda x: x['accuracy'])
        print(f"\n✓ Best accuracy: ±{best['accuracy']:.1f}m")
        return best
    return None


def dd_to_dms(dd):
    """Convert decimal degrees to degrees, minutes, seconds"""
    d = int(dd)
    m = int((dd - d) * 60)
    s = (dd - d - m/60) * 3600
    return d, m, s


async def main():
    print("=" * 70)
    print("WINDOWS GPS LOCATION - EXACT COORDINATES")
    print("=" * 70)
    print("\nAccessing Windows Location Services...")
    print("(Ensure Location is ON in Windows Settings)\n")
    
    # Get location
    location = await get_exact_location()
    
    if location:
        lat = location['latitude']
        lon = location['longitude']
        acc = location['accuracy']
        
        print("=" * 70)
        print("✓ LOCATION ACQUIRED")
        print("=" * 70)
        print(f"Latitude:  {lat:.8f}°")
        print(f"Longitude: {lon:.8f}°")
        print(f"Accuracy:  ±{acc:.1f} meters")
        print(f"Altitude:  {location['altitude']:.1f} meters")
        print("=" * 70)
        
        # Google Maps link
        maps_url = f"https://www.google.com/maps?q={lat},{lon}"
        print(f"\n🌍 Google Maps: {maps_url}")
        
        # Different coordinate formats
        print(f"\n📋 Coordinate Formats:")
        print(f"   Decimal:       {lat:.8f}, {lon:.8f}")
        
        # DMS format
        lat_d, lat_m, lat_s = dd_to_dms(abs(lat))
        lon_d, lon_m, lon_s = dd_to_dms(abs(lon))
        lat_dir = 'N' if lat >= 0 else 'S'
        lon_dir = 'E' if lon >= 0 else 'W'
        print(f"   DMS:           {lat_d}°{lat_m}'{lat_s:.2f}\"{lat_dir} {lon_d}°{lon_m}'{lon_s:.2f}\"{lon_dir}")
        
        print("\n" + "=" * 70)
    else:
        print("\n❌ FAILED TO GET LOCATION")
        print("\nTroubleshooting:")
        print("1. Open Settings (Win + I)")
        print("2. Go to: Privacy & Security > Location")
        print("3. Enable 'Location services'")
        print("4. Enable 'Let apps access your location'")
        print("5. Restart this script")


if __name__ == "__main__":
    # Run async main function
    if sys.platform == 'win32':
        asyncio.run(main())
    else:
        print("This script only works on Windows 10/11")