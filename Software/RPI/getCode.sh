#!/bin/bash

sudo rm -r /home/pi/code

echo "old code removed"
echo ""

scp -r arthur@192.168.2.31:/home/arthur/Projects/Turtle/Software/RPI/v3.2 /home/pi/code/

echo ""
echo "finished"