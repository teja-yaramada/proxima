#!/usr/bin/env bash

# Set the auto-start flag (1 to enable, 0 to disable)
AUTO_START=1

# Set the current working directory to PROXIMA_DIR
PROXIMA_DIR="/home/pi2/payload/proxima/"
cd "$PROXIMA_DIR" || {
    logger "Proxima Service: Failed to change working directory to $PROXIMA_DIR. Exiting."
    exit 1  # critical error
}

logger "Proxima Service: Successfully changed to $PROXIMA_DIR."

# Stop processes based on PID files
if [ -f "proxima_picamera.pid" ]; then
    kill "$(cat proxima_picamera.pid)" && logger "Proxima Service: Stopped picamera_capture process."
    rm "proxima_picamera.pid"
fi
if [ -f "proxima_flircamera.pid" ]; then
    kill "$(cat proxima_flircamera.pid)" && logger "Proxima Service: Stopped flir_capture process."
    rm "proxima_flircamera.pid"
fi

# Check if 'stop' parameter is provided
if [ "$1" == "stop" ]; then
    exit 0  # graceful exit
fi

# If auto-start is disabled, exit the script
if [ "$AUTO_START" -ne 1 ]; then
    logger "Proxima Service: Auto-start is disabled. Exiting script."
    exit 0  # graceful exit
fi

# Verify Python is installed
if ! command -v python3 &> /dev/null; then
    logger "Proxima Service: Python3 is not installed or not in PATH. Exiting."
    exit 1  # critical error
fi

logger "Proxima Service: Starting sensor data collection..."

# Identify the CPU core assignments
CPU_CORE_PICAMERA=3
CPU_CORE_FLIRCAMERA=2

# Validate CPU core assignments
MAX_CPU_CORE=3  # Modify based on the system's CPU cores
if [ "$CPU_CORE_PICAMERA" -gt "$MAX_CPU_CORE" ] || [ "$CPU_CORE_FLIRCAMERA" -gt "$MAX_CPU_CORE" ]; then
    logger "Proxima Service: Invalid CPU core assignment. Exiting."
    exit 2  # non-critical error
fi

# Function to start a script on a specified CPU core and write the PID to a file
start_script_on_core() {
    local script_name="$1"
    local cpu_core="$2"
    local pid_file="$3"

    # Stop process if already running based on the PID file
    if [ -f "$pid_file" ]; then
        existing_pid="$(cat $pid_file)"
        if ps -p "$existing_pid" &> /dev/null; then
            kill "$existing_pid" && logger "Proxima Service: Stopped existing process for $script_name."
        fi
        rm "$pid_file"
    fi

    if [ -f "$PROXIMA_DIR/$script_name" ]; then
        # Launch the process and get its PID
        taskset -c "$cpu_core" python3 "$PROXIMA_DIR/$script_name" &
        new_pid=$!
        echo "$new_pid" > "$pid_file"  # write PID to the specified file
        logger "Proxima Service: Launched $script_name on CPU core $cpu_core. PID: $new_pid."
    else
        logger "Proxima Service: $script_name not found in the current directory. Exiting."
        exit 1  # critical error
    fi
}

# Start the picamera_capture script and record the PID
start_script_on_core "picamera_capture.py" "$CPU_CORE_PICAMERA" "proxima_picamera.pid"

# Start the flir_capture script and record the PID
start_script_on_core "flir_capture.py" "$CPU_CORE_FLIRCAMERA" "proxima_flircamera.pid"
