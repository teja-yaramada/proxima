#!/usr/bin/env python

import numpy as np
import cv2
from pylepton.Lepton3 import Lepton3

def centi_kelvins_to_celsius(kelvins):
  return (kelvins / 100) - 273
  

def capture(flip_v = False, device = "/dev/spidev0.0"):
  with Lepton3(device) as l:
    a,_ = l.capture(debug_print=True)
  if flip_v:
    cv2.flip(a,0,a)

  lowest_temp = greatest_temp = centi_kelvins_to_celsius(a[0,0])
  for y in range(160):
    for x in range(120):
        pixel_temp = centi_kelvins_to_celsius(a[x,y]) 
        if pixel_temp > greatest_temp:
          greatest_temp = pixel_temp
        
        if pixel_temp < lowest_temp:
          lowest_temp = pixel_temp
    
  print('High:{}, Low:{}'.format(greatest_temp, lowest_temp))

  cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(a, 8, a)
  return np.uint8(a)


image = capture()
cv2.imwrite('ircam_output.png', image)
