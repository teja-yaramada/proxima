#!/usr/bin/env bash

# Set the auto-start flag (1 to enable, 0 to disable)
AUTO_START=1

# If auto-start is disabled, exit the script
if [ "$AUTO_START" -ne 1 ]; then
    logger "Proxima Service: Auto-start is disabled. Exiting script."
    exit 0  # exit gracefully
fi

# Set the current working directory to /home/pi2/payload/proxima/
cd /home/pi2/payload/proxima/ || {
    logger "Proxima Service: Failed to change working directory to /home/pi2/payload/proxima/. Exiting."
    exit 1  # error
}

logger "Proxima Service: Successfully changed to /home/pi2/payload/proxima/."

# Verify Python is installed
if ! command -v python3 &> /dev/null; then
    logger "Proxima Service: Python3 is not installed or not in PATH. Exiting."
    exit 1  # error
fi

logger "Proxima Service: Starting sensor data collection..."

# Identify the CPU core assignments
CPU_CORE_PICAMERA=3

# Start the capture script on the assigned core
if [ -f "picamera_capture.py" ]; then
    taskset -c $CPU_CORE_PICAMERA python3 picamera_capture.py &
    logger "Proxima Service: Launched picamera_capture.py on CPU core $CPU_CORE_PICAMERA."
else
    logger "Proxima Service: picamera_capture.py not found in the current directory. Exiting."
    exit 1  # error
fi

