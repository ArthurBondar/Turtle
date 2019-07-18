#!/usr/bin/python2

'''
    Changed: May 25, 2019
    Class to interract arduino through serial






''' 

import serial
from time import sleep              # sleep function in seconds


class TimingControl():
    port_obj = 0

    def __init__(self, port = '/dev/ttyS0', baud = 9600):
        self.port_obj = serial.Serial(port, baud)

        


# END Setup Class


# When class module is started by itself
# Following code is used for testing the parser class
# Accepts file path for setup file as input
if __name__ == '__main__':
    port = serial.Serial('/dev/ttyS0',9600)
    s = [0,1]
    while True:
        read_serial=port.readline()
        s[0] = str(int (port.readline(),16))
        print s[0]
        print read_serial

