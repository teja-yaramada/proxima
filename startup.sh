#!/bin/bash

# Set the auto-start flag (1 to enable, 0 to disable)
AUTO_START=1

# If auto-start is disabled, exit the script
if [ "$AUTO_START" -ne 1 ]; then
    logger "Proxima Service: Auto-start is disabled."
    exit 0  # exit gracefully
fi

# Set the current working directory to /home/pi2/payload/proxima/
cd /home/pi2/payload/proxima/ || {
    # Directory change failed
    logger "Proxima Service: Failed to change working directory to /home/pi2/payload/proxima/"
    exit 1  # error
}

logger "Proxima Service: Starting sensor data collection..."

# Start capture scripts 
python3 picamera_capture.py
# python3 capture.py 1 &
