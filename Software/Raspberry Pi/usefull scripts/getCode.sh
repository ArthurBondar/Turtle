#!/bin/bash

#
#	This script is used during development of the software
#	Used to remotely connect two Linux computer and transfer files
#	useful when writing code on a separate computer and uploading to the Pi
#

sudo rm -r /home/pi/code

echo "old code removed"
echo ""

scp -r arthur@192.168.2.31:/home/arthur/Projects/Turtle/Software/RPI/v3.2 /home/pi/code/

echo ""
echo "finished"