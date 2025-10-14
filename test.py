import cv2
import argparse
from detection import PotholeDetector
import os

def process_video(video_path, model_path="best.pt", output_dir="output_videos"):
    """
    Processes a video file to detect objects using a YOLO model and saves the annotated video.

    Args:
        video_path (str): Path to the input video file.
        model_path (str): Path to the YOLO model file (e.g., "best.pt").
        output_dir (str): Directory to save the output video.
    """
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    detector = PotholeDetector(model_path)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return

    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Define the codec and create VideoWriter object
    output_video_path = os.path.join(output_dir, f"output_{os.path.basename(video_path)}")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Codec for .mp4 files
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    print(f"Processing video: {video_path}")
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        print(f"Processing frame {frame_count}...")

        # Perform detection
        results = detector.detect(frame)

        # Annotate the frame
        annotated_frame, detected_objects = detector.annotate(frame.copy(), results)

        # Write the annotated frame to the output video
        out.write(annotated_frame)

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Video processing complete. Output saved to {output_video_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a video file for object detection.")
    parser.add_argument("video_file", type=str, nargs='?', default="video.mp4",
                        help="Path to the input video file. Defaults to 'video.mp4' if not provided.")
    parser.add_argument("--model", type=str, default="best.pt", help="Path to the YOLO model file.")
    parser.add_argument("--output_dir", type=str, default="output_videos", help="Directory to save the output video.")
    args = parser.parse_args()

    process_video(args.video_file, args.model, args.output_dir)
