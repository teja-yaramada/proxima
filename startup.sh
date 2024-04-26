#!/bin/bash

# Set the current working directory to /home/pi2/payload/proxima/
cd /home/pi2/payload/proxima/ || {
    # directory change failed
    logger "Proxima Service: Failed to change working directory to /home/pi2/payload/proxima/"
    exit 1  # error
}

logger "Proxima Service: Starting sensor data collection..."

# Start capture scripts 
#python3 capture.py 1 &

