import sys
import threading
import os
import time
import logging
import numpy as np
from datetime import datetime
from picamera2 import Picamera2
from pylepton.Lepton3 import Lepton3
import cv2
import board
from adafruit_lsm6ds.ism330dhcx import ISM330DHCX


prev_time = time.time()
acceleration_offset = np.asarray(ISM330DHCX(board.I2C()).acceleration)
velocity = np.array([0,0,0])
position = np.array([0,0,0])
orientation = np.array([0,0,0])


def capture_from_picam(filename):

    logging.info("PICAM creation")
    picam2 = Picamera2()
    
    logging.info("PICAM configure")
    # Configure the camera
    # picam2.start_preview()
    # Capture an image
    logging.info("PICAM capture start")
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

def create_file(dir_name):
    file = open(dir_name + "/imu.txt", "x")
    return file


# Function for a thread to continuously capture images from a camera
def capture_images(camera_name, capture_function, save_dir, forever=True):
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"{save_dir}/{camera_name}_{timestamp}.jpg"
        # Save the image with the filename
        #image.save(filename)
        capture_function(filename)
        if not forever:
            break
        time.sleep(0.1)  # Adjust the sleep time as needed

def get_time_delta():
    global prev_time
    current_time = time.time()
    delta = current_time - prev_time
    prev_time = current_time
    return delta

def log_file(file, message):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    file.write(timestamp + ": " + message + "\n")

def capture_position(file, forever=True):
    global velocity, position, acceleration_offset
    sensor = ISM330DHCX(board.I2C())
    while True:
        x_acc, y_acc, z_acc = sensor.acceleration
        # acceleration = np.array([x_acc, y_acc, z_acc])
        acceleration = np.subtract(np.asarray(sensor.acceleration), acceleration_offset)
        # if(np.less_equal(acceleration, np.array([0.1, 0.1, 0.1])[0])):
        #     break
        velocity = np.add(velocity, acceleration * get_time_delta())
        position = np.add(position, velocity * get_time_delta())
        logging.info("IMU Acceleration: {}, Velocity: {}, Position: {}".format(acceleration, velocity, position))
        file.write(datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        file.write("::: IMU Acceleration: {}, Velocity: {}, Position: {} \n".format(acceleration, velocity, position))
        if not forever:
            break
        time.sleep(0.02)  # Adjust the sleep time as needed

def capture_orientation(file, forever=True):
    global orientation
    sensor = ISM330DHCX(board.I2C())
    while True:
        x_vel, y_vel, z_vel = sensor.gyro
        angular_velocity = np.array([x_vel, y_vel, z_vel])
        orientation = np.add(orientation, angular_velocity * get_time_delta())
        logging.info("IMU Angular Velocity: {}, Angle: {}".format(angular_velocity, orientation))
        file.write(datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        file.write("::: IMU Angular Velocity: {}, Angle: {} \n".format(angular_velocity, orientation))
        if not forever:
            break
        time.sleep(0.02)  # Adjust the sleep time as needed

def sequential_run(save_dir, file):
    logging.info("PROXIMA Sequential Run")
    while True:
        capture_images("flir", capture_from_flir, save_dir, False)
        capture_images("picam", capture_from_picam, save_dir, False)
        capture_position(file, False)
        capture_orientation(file, False)

def multi_threaded_run(save_dir, file):
    logging.info("PROXIMA MultiThreaded Run")
    # Creating threads for FLIR, PiCamera and IMU
    flir_thread = threading.Thread(target=capture_images, args=("flir", capture_from_flir, save_dir))
    picam_thread = threading.Thread(target=capture_images, args=("picam", capture_from_picam, save_dir))
    imu_thread = threading.Thread(target=capture_position, args=(file, False))

    # Starting the threads
    flir_thread.start()
    picam_thread.start()
    imu_thread.start()

    flir_thread.join()
    picam_thread.join()
    imu_thread.join()

# Main function to start the threads
def main():
    save_dir = create_directory()
    file = create_file(save_dir)
    log_filename = os.path.join(save_dir, 'capture.log')
    logging.basicConfig(filename=log_filename, level=logging.INFO,
            format='%(asctime)s %(levelname)s: %(message)s')

    if int(sys.argv[1]) == 1:
        sequential_run(save_dir, file)
    else:
        multi_threaded_run(save_dir, file)

if __name__ == "__main__":
    main()

