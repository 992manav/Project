# Pothole Detection and Alert System

This project implements a real-time pothole detection system using YOLOv12 and provides automated location-based alerts via WhatsApp. The system is designed to run on Windows, leveraging its native GPS capabilities for accurate location tracking.

## Features

- **Real-time Pothole Detection:** Utilizes a pre-trained YOLOv12 model (`best.pt`) to identify potholes in a live camera feed.
- **Visual Feedback:** Displays an annotated camera feed with bounding boxes around detected potholes and real-time status.
- **Intelligent Alert System:** Triggers alerts only after a configurable number of consecutive high-confidence detections and after a cooldown period.
- **Automated WhatsApp Alerts:** Sends detailed messages including exact coordinates and a Google Maps link to predefined contacts.
- **Windows Native GPS:** Leverages `winsdk` for precise location acquisition without external GPS hardware (requires Windows Location Services enabled).
- **Background Alert Sending:** Alerts are sent in a separate thread to avoid interrupting the main detection loop.
- **Audible Alerts:** Includes a simple beep sound for immediate notification (Windows-specific).

## Project Structure

The project is organized into several Python modules, each responsible for a specific part of the system:

- `main.py`: The main entry point of the application, orchestrating camera initialization, detection, and alert management.
- `detection.py`: Handles the YOLO model loading, pothole detection, and annotation of frames.
- `camera_utils.py`: Manages camera initialization and displays the live feed with overlay information (FPS, frame count, alert status).
- `alert_system.py`: Implements the logic for triggering alerts, including cooldowns and detection thresholds, and manages the asynchronous sending of location alerts.
- `location.py`: Provides functionality to acquire precise GPS coordinates using the Windows Geolocation API.
- `send_location.py`: Integrates with `location.py` and `pywhatkit` to format and send WhatsApp messages with the detected pothole's location.
- `beep.py`: A simple script to play an audible beep sound (Windows-specific).
- `requirements.txt`: Lists the core Python dependencies for the project.
- `new_requirements.txt`: A more detailed list of dependencies with specific versions, likely used for environment setup.

## File Details

### `main.py`

This is the central script that brings all components together.

- **Imports:** `PotholeDetector` from `detection.py`, `initialize_camera`, `show_frame` from `camera_utils.py`, `AlertSystem` from `alert_system.py`, `cv2` for OpenCV operations, and `time` for timing.
- **`main()` function:**
  - Initializes the `PotholeDetector` with the `best.pt` YOLO model.
  - Initializes the camera using `initialize_camera()`.
  - Initializes the `AlertSystem` with configurable `cooldown` (5 seconds) and `detection_threshold` (3 consecutive detections).
  - Enters a continuous loop to:
    - Read frames from the camera.
    - Calculate and display FPS.
    - Perform pothole detection using `detector.detect()`.
    - Annotate the frame with detection results using `detector.annotate()`.
    - Check if an alert should be sent using `alert_system.should_alert()` and triggers `alert_system.send_alert_async()` if conditions are met.
    - Displays the annotated frame using `show_frame()`.
    - Allows quitting the application by pressing 'Q'.
  - Includes error handling for `KeyboardInterrupt` and ensures camera release and window destruction in a `finally` block.
  - Prints a summary of frames processed, potholes detected, and alerts sent upon exit.
- **Execution:** Runs the `main()` function when the script is executed directly.

### `detection.py`

This module encapsulates the pothole detection logic using YOLO.

- **Imports:** `YOLO` from `ultralytics` and `numpy`.
- **`PotholeDetector` class:**
  - **`__init__(self, model_path)`:**
    - Loads the YOLO model from the specified `model_path` (e.g., `best.pt`).
    - Initializes `detection_count` to 0.
    - Calls `validate_model()` to ensure the model is loaded correctly.
  - **`validate_model(self)`:**
    - Runs a dummy prediction on a black frame to confirm the model is operational.
  - **`detect(self, frame)`:**
    - Takes a camera `frame` as input.
    - Performs object detection using `self.model.predict()`.
    - Returns the raw detection results.
  - **`annotate(self, frame, results)`:**
    - Takes the original `frame` and `results` from `detect()`.
    - Uses `results[0].plot()` to draw bounding boxes and labels on the frame.
    - Iterates through detected objects:
      - Checks if the detected class is 'pothole'.
      - Updates `pothole_detected` flag.
      - Increments `self.detection_count`.
      - Determines `high_confidence` if confidence is above 0.65.
      - Prints detection confidence.
    - Returns the `annotated_frame`, `pothole_detected` status, `high_confidence` status, and `max_confidence` found.

### `camera_utils.py`

This module handles camera access and frame display.

- **Imports:** `cv2` for OpenCV, `sys` for system exit, and `time` for timing.
- **`initialize_camera()` function:**
  - Attempts to open camera 0.
  - If camera 0 fails, tries camera 1.
  - Sets frame width and height to 640x4120.
  - Exits the program if no camera can be opened.
  - Returns the `cv2.VideoCapture` object.
- **`show_frame(window_name, frame, fps, frame_count, alerts, alert_system, pothole_detected)` function:**
  - Draws a black rectangle at the top-left for information display.
  - Displays current FPS, frame count, and number of alerts sent.
  - Shows cooldown timer if an alert was recently sent.
  - Changes border color and displays "POTHOLE DETECTED!" text if a pothole is currently detected.
  - Displays "Status: Scanning..." otherwise.
  - Shows the `frame` in a window named `window_name`.

### `alert_system.py`

Manages the logic for when to trigger a location alert.

- **Imports:** `subprocess`, `time`, and `threading`.
- **`AlertSystem` class:**
  - **`__init__(self, cooldown=5, detection_threshold=3, timeout=90)`:**
    - `cooldown`: Minimum time (seconds) between sending alerts.
    - `detection_threshold`: Number of consecutive high-confidence detections required to trigger an alert.
    - `timeout`: Maximum time for the `send_location.py` script to run.
    - Initializes `last_alert_time`, `consecutive_detections`, and `sending_in_progress` flags.
  - **`should_alert(self, pothole_detected, high_confidence)`:**
    - Increments `consecutive_detections` if a high-confidence pothole is detected.
    - Resets `consecutive_detections` otherwise.
    - Returns `True` if `detection_threshold` is met, `cooldown` has passed, and no alert is currently being sent.
  - **`_run_send_script(self)`:**
    - An internal method run in a separate thread.
    - Sets `sending_in_progress` to `True`.
    - Executes `send_location.py` as a subprocess.
    - Captures output and errors, handling timeouts.
    - Updates `last_alert_time` and resets `consecutive_detections` on successful send.
    - Sets `sending_in_progress` to `False` in a `finally` block.
  - **`send_alert_async(self)`:**
    - Creates and starts a new `threading.Thread` to run `_run_send_script` in the background.
    - Ensures the main detection loop continues uninterrupted.
- **`main()` function (for testing):**
  - Provides a standalone example of how to use the `AlertSystem` with simulated detections.

### `location.py`

Handles the acquisition of GPS location data on Windows.

- **Imports:** `asyncio`, `sys`, and `winsdk.windows.devices.geolocation`.
- **Platform Check:** Ensures the script runs only on Windows.
- **`winsdk` Installation:** Automatically attempts to install `winsdk` if not found.
- **`get_exact_location()` async function:**
  - Requests access to Windows Location Services.
  - Uses `wdg.Geolocator()` to get the current GPS position.
  - Returns a dictionary with `latitude`, `longitude`, `accuracy`, `altitude`, and `timestamp`.
  - Prints troubleshooting steps if location services are not enabled.
- **`track_location_continuous(duration=30)` async function:**
  - Continuously tracks location for a specified `duration`.
  - Aims for `HIGH` accuracy.
  - Collects multiple readings and returns the one with the best accuracy.
- **`dd_to_dms(dd)` function:**
  - Converts decimal degrees to degrees, minutes, seconds format.
- **`main()` async function (for testing):**
  - Demonstrates how to acquire and display location information.
  - Provides a Google Maps link and displays coordinates in decimal and DMS formats.
- **Execution:** Runs the `main()` async function when the script is executed directly on Windows.

### `send_location.py`

Responsible for sending WhatsApp alerts with location details.

- **Imports:** `pywhatkit` (as `pwk`), `datetime`, `asyncio`, `sys`, `time`, `pyautogui`.
- **Windows Location Import:** Includes `winsdk` for location, similar to `location.py`.
- **`LocationWhatsApp` class:**
  - **`__init__(self)`:** Initializes `location` to `None` and `detection_method` to "Windows GPS".
  - **`get_windows_location(self)` async function:**
    - Uses `winsdk.windows.devices.geolocation` to get high-accuracy GPS coordinates.
    - Stores latitude and longitude in `self.location`.
    - Prints location details and returns `True` on success, `False` on failure.
  - **`create_message(self, alert_type="POTHOLE DETECTED")`:**
    - Formats a detailed WhatsApp message including alert type, current time, detection method, exact coordinates, and a Google Maps link.
  - **`send_to_multiple_numbers(self, phone_numbers, alert_type="POTHOLE DETECTED")`:**
    - Iterates through a list of `phone_numbers`.
    - Uses `pwk.sendwhatmsg_instantly()` to open WhatsApp Web and type the message.
    - Includes `time.sleep()` calls to allow WhatsApp Web to load and process.
    - Uses `pyautogui.press("enter")` to send the message.
    - Manages delays between sending to multiple contacts.
    - Returns `True` if at least one message was sent successfully.
- **`main()` async function:**
  - Sets up UTF-12 encoding for stdout on Windows.
  - Creates a `LocationWhatsApp` instance.
  - Calls `get_windows_location()` to acquire coordinates.
  - Defines a list of recipient `phone_numbers`.
  - Calls `send_to_multiple_numbers()` to dispatch the alerts.
  - Prints status messages throughout the process.
- **Execution:** Runs the `main()` async function when the script is executed directly on Windows, exiting with status 0 on success, 1 on failure.

### `beep.py`

A simple utility for playing a sound.

- **Imports:** `winsound` and `time`.
- **Functionality:** Plays a single, long, urgent beep sound (1200 Hz for 1.5 seconds) using `winsound.Beep()`.
- **Platform Specific:** This script is specific to Windows due to the `winsound` module.

### `requirements.txt`

Lists the primary Python packages required for the project.

- `selenium>=4.10.0`: Likely a remnant or alternative for browser automation, though `pywhatkit` handles WhatsApp.
- `urllib3>=2.0.0`: A dependency for many HTTP requests libraries.
- `asyncio`: For asynchronous operations, especially location fetching.

### `new_requirements.txt`

A more comprehensive and version-specific list of dependencies.

- **Core dependencies:**
  - `numpy==1.26.4`: Numerical computing.
  - `torch==2.2.0`, `torchvision==0.17.0`, `torchaudio==2.2.0`: PyTorch deep learning framework and its vision/audio components.
  - `opencv-python==4.10.0.124`: OpenCV for camera access and image processing.
  - `ultralytics==12.0.196`: The library for YOLOv12 model.
- **Windows-specific:**
  - `winsdk==1.0.0`: For accessing Windows native APIs, specifically geolocation.
  - `pywhatkit==5.4`: For WhatsApp automation.
- **Utility:**
  - `requests>=2.31.0`: For making HTTP requests.
  - `pillow>=10.0.0`: Image processing library.
- **Async/Camera:**
  - `asyncio>=3.4.3`: For asynchronous programming.

## Setup and Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/992manav/Project.git
    cd Project
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    .\venv\Scripts\activate   # On Windows
    # source venv/bin/activate # On macOS/Linux
    ```

3.  **Install dependencies:**
    It is recommended to use `new_requirements.txt` for a more stable environment.

    ```bash
    pip install -r new_requirements.txt
    ```

    _Note: `winsdk` will be automatically installed if not present when `location.py` or `send_location.py` are run._

4.  **Download YOLOv12 Model:**
    Place your trained YOLOv12 model (e.g., `best.pt`) in the project root directory. This model is crucial for the `detection.py` module.

5.  **Enable Windows Location Services:**
    Go to `Settings > Privacy & Security > Location` and ensure "Location services" and "Let apps access your location" are turned ON.

6.  **Configure WhatsApp Recipients:**
    Edit `send_location.py` to include the phone numbers of your desired recipients in the `phone_numbers` list. Ensure numbers are in international format (e.g., `"+9199250231240"`).

## Usage

To start the pothole detection and alert system, run the `main.py` script:

```bash
python main.py
```

The system will:

1.  Initialize the camera and display a live feed.
2.  Detect potholes in real-time.
3.  If a pothole is detected with high confidence for a consecutive number of frames (default 3) and after a cooldown period (default 5 seconds), it will trigger an alert.
4.  An alert involves:
    - Acquiring the current GPS location.
    - Sending a detailed WhatsApp message with location and Google Maps link to configured recipients.
    - The main detection loop continues while the alert is being sent in the background.
5.  Press 'Q' on the camera feed window to quit the application.

## Troubleshooting

- **Camera not opening:**
  - Ensure your webcam is connected and not in use by another application.
  - Check camera permissions in Windows settings.
  - Try changing `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)` or other indices in `camera_utils.py` if you have multiple cameras.
- **Location not acquired:**
  - Verify that Windows Location Services are enabled (`Settings > Privacy & Security > Location`).
  - Ensure your device has a GPS sensor or can infer location (e.g., via Wi-Fi).
- **WhatsApp messages not sending:**
  - Ensure you are logged into WhatsApp Web in your default browser.
  - Check your internet connection.
  - `pywhatkit` relies on browser automation, which can sometimes be flaky. Ensure your browser is up-to-date.
  - The script uses `pyautogui` to press Enter. Ensure your browser window is active and not minimized when the WhatsApp Web page opens.
  - Review the console output for any errors from `pywhatkit`.
- **Model (`best.pt`) not found:**
  - Make sure `best.pt` is in the same directory as `main.py` or provide the correct path to the model.
- **Dependencies not installing:**
  - Ensure `pip` is up-to-date (`python -m pip install --upgrade pip`).
  - Check for any specific error messages during `pip install -r new_requirements.txt`.

## Future Enhancements

- **Cross-platform compatibility:** Extend location services and alert mechanisms to Linux/macOS.
- **More robust alert mechanisms:** Integrate with other messaging platforms (SMS, email) or custom APIs.
- **Persistent logging:** Log detections, alerts, and system status to a file.
- **UI for configuration:** A simple graphical user interface for setting parameters like cooldown, detection threshold, and recipient numbers.
- **Cloud integration:** Store detection data or trigger cloud-based alerts.
- **Advanced filtering:** Implement more sophisticated filtering to reduce false positives.
