#!/bin/bash

#
#	This script updates the fotware packages on the Pi
#	Usefull during development, updates the camera module
#

sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y dist-upgrade
sudo apt-get -y autoclean
sudo apt-get -y autoremove

# Next line updates the Linux Kernel - comment out if not necessary
sudo apt-get rpi-update