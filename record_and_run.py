import cv2
import numpy as np
import mss
import subprocess
import time
import sys
from pathlib import Path

def main():
    # 1. Configuration
    output_filename = "rose_empire_full_workflow.mp4"
    fps = 20.0
    # Using fleet_scraper.py as the primary lead generator
    scraper_script = "fleet_scraper.py" 
    # Target mission for high-end leads
    scraper_args = ["-3", "fleet_scraper.py", "--limit", "10", "--mission", "luxury care homes nursing homes UK mattress protector bulk buyers", "--headed"]
    
    # 2. Screen Resolution Setup via mss
    # mss.mss().monitors[1] is the primary monitor's full bounding box
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screen_width = monitor["width"]
        screen_height = monitor["height"]
        print(f"Detected Absolute Fullscreen Resolution: {screen_width}x{screen_height}")
        
        # 3. Video Writer Setup
        # 'mp4v' codec for high-quality .mp4
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_filename, fourcc, fps, (screen_width, screen_height))
        
        if not out.isOpened():
            print("Error: Could not open video writer.")
            sys.exit(1)

        print(f"Starting ultra-smooth recording: {output_filename}")
        print(f"Launching scraper: {scraper_script}...")

        # 4. Kick off the lead generator as a background subprocess
        try:
            process = subprocess.Popen(
                ["py"] + scraper_args, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True,
                shell=True if sys.platform == "win32" else False
            )
        except Exception as e:
            print(f"Failed to start scraper: {e}")
            out.release()
            sys.exit(1)

        # 5. Recording and Monitoring Loop
        try:
            while True:
                # Check if the scraper process has finished
                poll = process.poll()
                if poll is not None:
                    print(f"\nScraper finished with exit code {poll}. Stopping recording...")
                    break
                
                # High-speed capture using mss (captures everything including cursor/taskbar)
                # mss captures raw BGRA pixels
                img = sct.grab(monitor)
                
                # Convert to numpy array
                frame = np.array(img)
                
                # mss captures in BGRA, OpenCV needs BGR
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                
                # Write the frame to the video file
                out.write(frame)
                
                # Precision frame rate pacing
                time.sleep(1/fps)
                
        except KeyboardInterrupt:
            print("\nRecording interrupted by user.")
        finally:
            # 6. Cleanup and Safe Exit
            out.release()
            process.terminate()
            print(f"High-quality video saved successfully as {output_filename}")

if __name__ == "__main__":
    main()
