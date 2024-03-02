#!/usr/bin/env python

import numpy as np
import cv2
from pylepton.Lepton3 import Lepton3
from picamera2 import Picamera2
from adafruit_lsm6ds.ism330dhcx import ISM330DHCX

def centi_kelvins_to_celsius(kelvins):
  return (kelvins / 100) - 273
  

def capture(flip_v = False, device = "/dev/spidev0.0"):
  with Lepton3(device) as l:
    a,_ = l.capture()
  if flip_v:
    cv2.flip(a,0,a)

  greatest_temp = centi_kelvins_to_celsius(a[0,0])
  lowest_temp = a[0,0] / 100 - 273
  for y in range(160):
    for x in range(120):
        pixel = a[x,y] / 100 - 273 
        if pixel > greatest_temp:
          greatest_temp = pixel
        
        if pixel < lowest_temp:
          lowest_temp = pixel
    
  print('High:{}, Low:{}'.format(greatest_temp, lowest_temp))

  cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(a, 8, a)
  return np.uint8(a)


image = capture()
cv2.imwrite('ircam_output.png', image)

picam = Picamera2()
picam.start()
#picam.capture_file('/home/pi/payload/proxima/picam_output.png')
picam.capture_file('picam_output.png')
# size = picam.sensor_resolution

# if size[0] > 4096:
#   height = size[1] * 4096 // size[0]
#   height -= height % 2
#   size = (4096, height)

# config = picam.create