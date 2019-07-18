#!/bin/bash

# starting the script
# waiting for system to boot
echo 'rc.local START'

# disable the wifi interface
sudo rfkill block 0

# wait for system to boot
sleep 5

# file directories
USB="/home/pi/USB"
VID="/home/pi/Video"
DISK="/dev/sda1"

# removing old files from Video dir
if [ "$(ls -A $VID)" ]; then
        sudo rm /home/pi/Video/*
        echo 'Video dir cleaned'
fi
# removing old file from USB dir
if [ "$(ls -A $USB)" ]; then
        sudo rm /home/pi/USB/*
        echo 'USB directory cleaned'
fi

# check if USB stick is present
# present - mount, not present - exit
if [ "$(ls -A $DISK)" ]; then
        sudo mount $DISK $USB
        sleep 5
        echo 'USB mounted'
else
        echo 'USB not present'
        # sudo rfkill unblock 0   # enabling wifi
        echo 'rc.local STOP'
        exit 0
fi

# checking for debug semaphore
# if semaphore file - debug exist script doesnt run
sem="/home/pi/USB/debug"
if [ -f "$sem" ]; then
        echo 'Sempahore found - debug session'
        # sudo rfkill unblock 0
        touch /home/pi/DEBUG_SESSION
else
        echo 'Disabeling WiFi'
        # sudo rfkill block 0
        echo 'Launching Script'
        sudo python /home/pi/code/main_code.py &
fi

echo 'rc.local STOP'
exit 0