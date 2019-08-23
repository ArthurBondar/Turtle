#!/bin/bash

#
# Changed: October 7, 2018
# Arthur Bondar
#
# Cleanup Script for Raspberry Pi
# To list all apps use: $dpkg-query -l> list_packages.txt 
#

sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y dist-upgrade

sudo apt-get remove --purge wolfram-engine scratch nuscratch sonic-pi idle3 smartsim penguinspuzzle java-common minecraft-pi python-minecraftpi python3-minecraftpi
sudo apt-get remove --purge wolfram-engine bluej Greenfoot nodered nuscr
sudo apt-get remove --purge libreoffice*

sudo apt-get clean
sudo apt-get remove 
sudo apt-get -y autoclean
sudo apt-get -y autoremove