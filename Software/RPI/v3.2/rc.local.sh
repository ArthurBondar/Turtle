#!/bin/bash

# starting the script
# waiting for system to boot
echo 'rc.local START'
sleep 10

# file directories
USB="/home/pi/USB"
VID="/home/pi/Video"

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

# mounting the USB
sudo mount /dev/sda1 /home/pi/USB
sleep 5

# checking for debu semaphore
# if semaphore file - debug exist script doesnt run
sem="/home/pi/USB/debug"
if [ -f "$sem" ]; then
        echo 'Sempahore found - debug session'
else
        echo 'Launching Script'
        #sudo python /home/pi/code/main.py &
fi

echo 'rc.local STOP'

exit 0

