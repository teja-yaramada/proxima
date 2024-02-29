# Overview

Payload subsystem for the Proxima project.

# Installations

## Prerequisites

Following is required for the `pylepton`.

    sudo apt-get install -y python3-opencv python3-numpy

This installed several native libraries supporting the `opencv` and `numpy` APIs in python3

## Pylepton

    git clone https://github.com/groupgets/pylepton.git -b lepton3-dev

As we aren't installing the pylepton library, setup a symlink to its relative location. For example for access from `proxima` project which is a peer folder to `pylepton` git repository.

    pi@raspberrypi:~/payload/proxima $ ln -s ../pylepton/pylepton ./

The above command will establish `pylepton` project usable from python code as `from pylepton import Lepton`. A long listing of the folder will show the sym-link as below:

    lrwxrwxrwx 1 pi pi  20 Feb 26 16:41 pylepton -> ../pylepton/pylepton

## LSM6DS Library

Clone the software

    git clone https://github.com/adafruit/Adafruit_CircuitPython_LSM6DS.git

Below install fetches the circuitpython drivers:
   
    sudo pip3 install adafruit-circuitpython-lsm6ds --break-system-packages

From proxima source folder, set up a symlink to the relative location of LSM6DS python library.

    pi@raspberrypi:~/payload/proxima $ ln -s ../Adafruit_CircuitPython_LSM6DS/adafruit_lsm6ds ./

Now the long listing of the folder should show the sym-links as below:

    lrwxrwxrwx 1 pi pi     48 Feb 29 01:19 adafruit_lsm6ds -> ../Adafruit_CircuitPython_LSM6DS/adafruit_lsm6ds
    lrwxrwxrwx 1 pi pi     20 Feb 26 16:41 pylepton -> ../pylepton/pylepton

# Lepton module

Lepton FLIR module interfaces with the RPI board over SPI and I2C bus.

## References

1. [Youtube video from GroupGets](https://www.youtube.com/watch?v=Gc3fSmK9eco&ab_channel=GroupGets)
2. [Module purchased from GroupGets] (https://groupgets.com/products/flir-lepton-3-5)
3. 

## I2C interface

Verify the i2c is enabled

    lsmod | grep i2c

if you see the `i2c_bcm2835` it means the kernel driver for i2c interfaces has been loaded.

Check the i2c devices are published in filesystem

    ls -l /dev/i2c-*

Install the `i2c-tools` package for handy tools to test `i2c` peripheral

    sudo apt-get install -y i2c-tools

Test the i2c device detection

    pi@raspberrypi:~/payload $ sudo i2cdetect -l
    i2c-1   i2c             bcm2835 (i2c@7e804000)                  I2C adapter
    i2c-20  i2c             fef04500.i2c                            I2C adapter
    i2c-21  i2c             fef09500.i2c                            I2C adapter

Check the address of the i2c device on i2c-1

    pi@raspberrypi:~/payload $ sudo i2cdetect -y 1
        0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
    00:                         -- -- -- -- -- -- -- -- 
    10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    20: -- -- -- -- -- -- -- -- -- -- 2a -- -- -- -- -- 
    30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 

Similarly on the `i2c-20` and `i2c-21`.

    pi@raspberrypi:~/payload $ sudo i2cdetect -y 20
        0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
    00:                         08 09 0a 0b 0c 0d 0e 0f 
    10: 10 11 12 13 14 15 16 17 18 19 1a 1b 1c 1d 1e 1f 
    20: 20 21 22 23 24 25 26 27 28 29 2a 2b 2c 2d 2e 2f 
    30: -- -- -- -- -- -- -- -- 38 39 3a 3b 3c 3d 3e 3f 
    40: 40 41 42 43 44 45 46 47 48 49 4a 4b 4c 4d 4e 4f 
    50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    60: 60 61 62 63 64 65 66 67 68 69 6a 6b 6c 6d 6e 6f 
    70: 70 71 72 73 74 75 76 77                         
    pi@raspberrypi:~/payload $ sudo i2cdetect -y 21
        0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
    00:                         08 09 0a 0b 0c 0d 0e 0f 
    10: 10 11 12 13 14 15 16 17 18 19 1a 1b 1c 1d 1e 1f 
    20: 20 21 22 23 24 25 26 27 28 29 2a 2b 2c 2d 2e 2f 
    30: -- -- -- -- -- -- -- -- 38 39 3a 3b 3c 3d 3e 3f 
    40: 40 41 42 43 44 45 46 47 48 49 4a 4b 4c 4d 4e 4f 
    50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    60: 60 61 62 63 64 65 66 67 68 69 6a 6b 6c 6d 6e 6f 
    70: 70 71 72 73 74 75 76 77                         

## SPI interface

### Driver references

    https://github.com/torvalds/linux/blob/master/drivers/spi/spi-bcm2835.c


# Raspberry PI Zero 2

This is a System-in-Package (SIP), a custom package, named [RP3A0](https://www.raspberrypi.com/documentation/computers/processors.html#rp3a0). The main Silicon inside, the real workhorse, is [BCM2837](https://www.raspberrypi.com/documentation/computers/processors.html#bcm2837). This is a 4 core Cortex-A53 CPU, each can run upto 1.2GHz, but optimal at 1GHz. The SIP also included 512MB of LPDDR2 RAM. Refer to this expert [blog](https://www.jeffgeerling.com/blog/2021/look-inside-raspberry-pi-zero-2-w-and-rp3a0-au) who performed an X-Ray study of the SIP.

# pylepton Error

Issue with lepton capture function which was throwing error in program. 
Issue traced back:
    
    ret = ioctl(handle, iow, xs_buf[xs_size * (60 - messages):], True)

[Link to github issue solution](https://github.com/groupgets/pylepton/issues/52).
Problem solves by reducing the message size of the library. Changed SPIDEV_MESSASGE_LIMIT from 24 to 8. Program now able to run, however, output images appeared to be flawed.
