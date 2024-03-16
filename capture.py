import threading
import os
import time
import logging
import numpy as np
from datetime import datetime
from picamera2 import Picamera2
from pylepton.Lepton3 import Lepton3
import cv2
from adafruit_lsm6ds.ism330dhcx import ISM330DHCX

start_time = datetime.now()
prev_time = start_time
velocity = np.array([0,0,0])
position = np.array([0,0,0])


def capture_from_picam(filename):

    logging.info("PICAM creation")
    picam2 = Picamera2()
    
    logging.info("PICAM configure")
    # Configure the camera
    # picam2.start_preview()
    # Capture an image
    logging.info("PICAM catpture start")
    picam2.start()
    logging.info(f"PICAM write to {filename}")
    picam2.capture_file(filename)
    picam2.stop()

    logging.info("PICAM image saved")

    picam2.__del__()

    # Convert the captured image to a format suitable for saving
    # This example converts it to a PIL Image, but you can adjust it as needed
    #from PIL import Image
    #captured_image = Image.fromarray(np.uint8(image)).convert('RGB')

    return None

# Placeholder functions for capturing images from FLIR and PiCamera
def capture_from_flir(filename):
    def centi_kelvins_to_celsius(kelvins):
      return (kelvins / 100) - 273

    def capture_and_convert(flip_v = False, device = "/dev/spidev0.0"):
        logging.info("FLIR image capture start")
        with Lepton3(device) as l:
          a,_ = l.capture()
        if flip_v:
          cv2.flip(a,0,a)
        logging.info("FLIR image capture done")

        lowest_temp = greatest_temp = centi_kelvins_to_celsius(a[0,0])
        for y in range(160):
          for x in range(120):
              pixel_temp = centi_kelvins_to_celsius(a[x,y]) 
              if pixel_temp > greatest_temp:
                greatest_temp = pixel_temp
              
              if pixel_temp < lowest_temp:
                lowest_temp = pixel_temp
          
        logging.info('FLIR temperatures High:{}, Low:{}'.format(greatest_temp, lowest_temp))

        cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
        np.right_shift(a, 8, a)
        return np.uint8(a)
    
    image = capture_and_convert()
    cv2.imwrite(filename, image)
    return image

# Function to create a directory for storing images
def create_directory():
    dir_name = 'logs/' + datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    return dir_name



# Function for a thread to continuously capture images from a camera
def capture_images(camera_name, capture_function, save_dir):
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"{save_dir}/{camera_name}_{timestamp}.jpg"
        # Save the image with the filename
        #image.save(filename)
        capture_function(filename)
        time.sleep(0.1)  # Adjust the sleep time as needed

def get_flight_time():
    return datetime.now() - start_time

def get_time_delta():
    delta = get_flight_time() - prev_time
    prev_time = get_flight_time()
    return delta

def capture_position():
    logging.info("IMU Logging Activated")
    sensor = ISM330DHCX(board.I2C())
    while True:
        x_acc, y_acc, z_acc = sensor.acceleration
        acceleration = np.array([a_acc, y_acc, z_acc])
        velocity = np.add(velcoity, acceleration * get_time_delta())
        position = np.add(position, velcoity * get_time_delta())
        logging.info("Acceleration: " + acceleration)
        logging.info("Velocity: " + velocity)
        logging.info("Position: " + position)
  
# Main function to start the threads
def main():
    save_dir = create_directory()
    log_filename = os.path.join(save_dir, 'capture.log')
    logging.basicConfig(filename=log_filename, level=logging.INFO,
            format='%(asctime)s %(levelname)s: %(message)s')

    # logging.info("PICAM creation")
    #picam2 = Picamera2()

    # Creating threads for FLIR, PiCamera and IMU
    flir_thread = threading.Thread(target=capture_images, args=("flir", capture_from_flir, save_dir))
    picam_thread = threading.Thread(target=capture_images, args=("picam", capture_from_picam, save_dir))
    imu_thread = threading.Thread(target=capture_position, args=())

    # Starting the threads
    flir_thread.start()
    picam_thread.start()
    imu_thread.start()

    flir_thread.join()
    picam_thread.join()
    imu_thread.join()

if __name__ == "__main__":
    main()

