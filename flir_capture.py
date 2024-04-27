import os
import logging
import datetime
import time
import numpy as np
import cv2
from pylepton.Lepton3 import Lepton3

# Function to create a directory for storing images
def create_flir_directory():
    dir_name = 'logs/flir/' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    os.makedirs(dir_name, exist_ok=True)
    return dir_name

# Convert centi-kelvins to Celsius
def centi_kelvins_to_celsius(kelvins):
    return (kelvins / 100) - 273

# Capture and convert FLIR images
def capture_and_convert(flip_v=False, device="/dev/spidev0.0"):
    try:
        with Lepton3(device) as l:
            a, _ = l.capture()
            if flip_v:
                cv2.flip(a, 0, a)

        return a
    except Exception as e:
        logging.error(f"Error capturing FLIR image: {e}")
        raise

# Capture from FLIR and save to a file
def capture_from_flir(filename):
    image_data = capture_and_convert()

    # Calculate temperature range
    temps = centi_kelvins_to_celsius(image_data)
    lowest_temp = np.min(temps)
    greatest_temp = np.max(temps)

    logging.info(f"FLIR temperatures - High: {greatest_temp}, Low: {lowest_temp}")

    # Normalize and save the image
    cv2.normalize(image_data, image_data, 0, 65535, cv2.NORM_MINMAX)
    np.right_shift(image_data, 8, image_data)
    cv2.imwrite(filename, np.uint8(image_data))

# Continuously capture images
def capture_images(camera_name, save_dir, forever=True, sleep_time=0.1):
    while True:
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            filename = f"{save_dir}/{camera_name}_{timestamp}.jpg"

            capture_from_flir(filename)

            if not forever:
                break

            time.sleep(sleep_time)  # Adjust as needed
        except Exception as e:
            logging.error(f"Error during image capture loop: {e}")
            break

# Main function to start capturing images
def main():
    try:
        save_dir = create_flir_directory()
        log_filename = os.path.join(save_dir, 'capture.log')
        logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

        logging.info("Starting FLIR image capture process")
        capture_images("flir", save_dir, False)
    except Exception as e:
        logging.error(f"Error in main function: {e}")

if __name__ == "__main__":
    main()
