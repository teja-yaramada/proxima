#This is a smaple from: https://github.com/adafruit/Adafruit_CircuitPython_LSM6DS/blob/main/examples/lsm6ds_ism330dhcx_simpletest.py
import time
import board
from adafruit_lsm6ds.ism330dhcx import ISM330DHCX
#from picamera2 import Picamera2

#picam = Picamera2()
#picam.start()
#picam.capture_file('picam_output.png')

i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
sensor = ISM330DHCX(i2c)

while True:
    print("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2" % (sensor.acceleration))
    print("Gyro X:%.2f, Y: %.2f, Z: %.2f radians/s" % (sensor.gyro))
    print("")
    time.sleep(0.5)
