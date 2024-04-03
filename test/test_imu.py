#This is a smaple from: https://github.com/adafruit/Adafruit_CircuitPython_LSM6DS/blob/main/examples/lsm6ds_ism330dhcx_simpletest.py
import time
import board
import numpy as np
from adafruit_lsm6ds.ism330dhcx import ISM330DHCX
#from picamera2 import Picamera2

#picam = Picamera2()
#picam.start()
#picam.capture_file('picam_output.png')

sensor = ISM330DHCX(board.I2C())

prev_time = time.time()
# x_acc, y_acc, z_acc = sensor.acceleration
acc_offset = np.array(sensor.acceleration)
prev_acc = np.array([0,0,0])
velocity = np.array([0,0,0])
position = np.array([0,0,0])
tolerance = 0.1

def get_time_delta():
    # global prev_time
    # current_time = time.time()
    # delta = current_time - prev_time
    # prev_time = current_time
    # return delta
    return 0.02

def capture_position():
    global velocity, position, sensor, prev_acc, tolerance
    acceleration = np.subtract(np.array(sensor.acceleration), acc_offset)
    if np.greater(np.absolute(np.subtract(acceleration, prev_acc)), tolerance)[0]:
        velocity = np.add(velocity, acceleration * get_time_delta())
        position = np.add(position, velocity * get_time_delta())
    prev_acc = acceleration 
    print("IMU Acceleration: {}, Velocity: {}, Position: {}".format(acceleration, velocity, position))
    time.sleep(0.02)  # Adjust the sleep time as needed


while True:
    capture_position()