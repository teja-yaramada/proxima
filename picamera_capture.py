from picamera2 import Picamera2
import os
import logging
from datetime import datetime
import time
import signal


# Class to encapsulate camera capture functionality
class PicameraCapture:
    def __init__(self):
        self.picam2 = Picamera2()
        self.keep_capturing = True

    def stop_capture(self, signum, frame):
        self.keep_capturing = False

    def capture_image(self, filename):
        # Capture and save the image
        self.picam2.start()
        self.picam2.capture_file(filename)
        self.picam2.stop()

    def __enter__(self):
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.stop_capture)  # Handle Ctrl+C
        signal.signal(signal.SIGTERM, self.stop_capture)  # Handle termination
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup resources
        if self.picam2:
            self.picam2.close()
        if exc_type is not None:
            logging.error("Exception in camera capture", exc_info=(exc_type, exc_val, exc_tb))


# Function to create a directory for storing images
def create_picamera_directory():
    dir_name = 'logs/picamera/' + datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    os.makedirs(dir_name, exist_ok=True)
    return dir_name


# Function to capture images with configurable loop control
def capture_images(camera_name, capture_function, save_dir, num_captures=None, interval=0.5):
    # If num_captures is None or negative, capture forever
    capture_forever = (num_captures is None or num_captures < 1)

    count = 0
    while capture_function.keep_capturing and (capture_forever or count < num_captures):
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"{save_dir}/{camera_name}_{timestamp}.jpg"
        capture_function.capture_image(filename)
        time.sleep(interval)  # Time between captures
        count += 1


# Main function to start capturing images
def main():
    save_dir = create_picamera_directory()
    log_filename = os.path.join(save_dir, 'capture.log')
    logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

    with PicameraCapture() as camera_capture:
        # Capture 10 images or run forever based on the parameter
        # Set 'num_captures' to 10 for a fixed count, or None for infinite loop
        capture_images("picam", camera_capture, save_dir, num_captures=None, interval=0.5)


if __name__ == "__main__":
    main()
