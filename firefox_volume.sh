#!/bin/sh

# Script to continuously monitor and set Firefox tab volumes to 10%
# Uses pactl to control PulseAudio/PipeWire sink inputs

TARGET_VOLUME=20

echo "Firefox Volume Controller - Setting all Firefox tabs to ${TARGET_VOLUME}%"
echo "Press Ctrl+C to stop"
echo ""

while true; do
    # Get all sink inputs (audio streams)
    pactl list sink-inputs | grep -E "Sink Input #|application.name" | while read -r line; do
        # Check if this is a sink input line
        if [[ "$line" =~ "Sink Input #"([0-9]+) ]]; then
            sink_input="${BASH_REMATCH[1]}"
            current_sink=$sink_input
        # Check if this belongs to Firefox
        elif [[ "$line" =~ "application.name".*\"Firefox\" ]] && [ -n "$current_sink" ]; then
            # Set volume to target percentage
            pactl set-sink-input-volume "$current_sink" "${TARGET_VOLUME}%"
            echo "Set Firefox sink input #${current_sink} to ${TARGET_VOLUME}%"
            current_sink=""
        fi
    done
    
    # Wait 1 second before checking again
    sleep 1
done
