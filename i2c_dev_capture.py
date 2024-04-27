import sys
import threading
import os
import time
import logging
import numpy as np
from datetime import datetime
from pylepton.Lepton3 import Lepton3
import cv2
import board
from adafruit_lsm6ds.ism330dhcx import ISM330DHCX

imu = ISM330DHCX(board.I2C())
acceleration_offset = np.asarray(imu.acceleration)
angular_velocity_offset = np.asarray(imu.gyro)

def capture_flir_images(save_dir):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"{save_dir}/flir_{timestamp}.jpg"

    def cK_to_C(kelvins):
      return (kelvins / 100) - 273

    def capture_and_convert(flip_v = False, device = "/dev/spidev0.0"):
        logging.info("FLIR image capture start")
        with Lepton3(device) as l:
          a,_ = l.capture()
        if flip_v:
          cv2.flip(a,0,a)
        logging.info("FLIR image capture done")

        lowest_temp = greatest_temp = cK_to_C(a[0,0])
        for y in range(160):
          for x in range(120):
              pixel_temp = cK_to_C(a[x,y]) 
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

def capture_imu_data(save_dir):
    global imu, acceleration_offset, angular_velocity_offset

    imu_log = open(save_dir + "/imu_log.txt", "a")

    acceleration = np.subtract(np.asarray(imu.acceleration), acceleration_offset)
    angular_velocity = np.subtract(np.asarray(imu.gyro), angular_velocity_offset)
    logging.info("IMU Acceleration: {}, IMU Angular Velocity: {}".format(acceleration, angular_velocity))
    imu_log.write(datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    imu_log.write("::: IMU Acceleration: {}, IMU Angular Velocity: {} \n".format(acceleration, angular_velocity))

    time.sleep(0.2)

    return "::: IMU Acceleration: {}, IMU Angular Velocity: {} \n".format(acceleration, angular_velocity)

def create_directory():
    dir_name = 'logs/i2c_dev/' + datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    os.makedirs(dir_name, exist_ok=True)
    print("Logging Directory created")
    return dir_name

def main():
    #func_list = [capture_flir_images, capture_imu_data]
    func_list = [capture_imu_data]

    '''
    # Check if the flir argument is supplied and append flir capture functionality if true
    if  'flir' in sys.argv:
        print("FLIR Functionality Added")
        func_list.append(capture_flir_images)

    # Check is the imu argument is supplied and append imu capture functionality if true
    if 'imu' in sys.argv:
        print("IMU Functionality Added")
        func_list.append(capture_imu_data)
    
    # Terminate program is no arguments are supplied or functionalities added
    if len(func_list) < 1:
        print("No program functionality selected and executing self termination")
        sys.exit(0)
    '''

    # Create file data directory and configure logging 
    save_dir = create_directory()
    log_filename = os.path.join(save_dir, 'capture.log')
    logging.basicConfig(filename=log_filename, level=logging.INFO,
            format='%(asctime)s %(levelname)s: %(message)s')

    # System execution loop
    while True:
        for func in func_list:
            func(save_dir)

if __name__ == "__main__":
    main()
