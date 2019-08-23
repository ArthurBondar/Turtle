#!/usr/bin/python2


'''
    August 17, 2019
    Arthur Bondar
    Board: Line Camera Rev. A 

    Class to use GPIO's of the Rapsberri Pi
    primary use is to display status LED's
    and enable 'Alive' pin to let arduino know Pi is up

'''

import RPi.GPIO as GPIO
from time import sleep

class Gpio_class():

    # default parameters
    # overwritten by parsed data from setup file
    LED1 = 10
    LED2 = 9
    MCU1 = 4
    MCU2 = 17
    SW1 = 21
    SW2 = 18
    led_state = False
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    def __init__(self):
        # declare IO
        GPIO.setup(self.LED1, GPIO.OUT)
        GPIO.setup(self.LED2, GPIO.OUT)
        GPIO.setup(self.MCU1, GPIO.OUT)
        GPIO.setup(self.MCU2, GPIO.IN)
        GPIO.setup(self.SW1, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.setup(self.SW2, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        # set initial states
        GPIO.output(self.LED1, GPIO.HIGH)
        GPIO.output(self.MCU1, GPIO.HIGH)

    # set recording ON and run led OFF
    def setRec(self):
        GPIO.output(self.LED2, GPIO.HIGH)
        GPIO.output(self.LED1, GPIO.LOW)

    # set run ON and recording led OFF
    def setRun(self):
        GPIO.output(self.LED2, GPIO.LOW)
        GPIO.output(self.LED1, GPIO.HIGH)

    # set both LED's low
    def clear(self):
        GPIO.output(self.LED1, GPIO.LOW)
        GPIO.output(self.LED2, GPIO.LOW)

    def toggleRec(self):
        if self.led_state == True:
            self.clear()
            self.led_state = False
        else:
            self.setRec()
            self.led_state = True

    # blink run led number of times
    def blink(self, times):
        self.clear()
        for i in range (0, times):
            GPIO.output(self.LED1, GPIO.LOW)
            sleep(0.2)
            GPIO.output(self.LED1, GPIO.HIGH)
            sleep(0.2)

    # check if switch pin is pulled low
    # num - number of the switch
    def checkSwitch(self, num):
        if num == 1:    return GPIO.input(self.SW1)
        if num == 2:    return GPIO.input(self.SW2)
        return 0

# END GPIO Class


# When class module is started by itself
# Following code is used for testing the LED's
if __name__ == '__main__':

    print "Testing LEDs -----------------------"

    # Create LED object
    _io = Gpio_class()
    _io.clear()

    # Testing Recording LED (RED)
    print "Recording LED ON for 5 sec"
    _io.setRec()
    sleep(5)

    # Testing Recording LED (RED)
    print "Run LED ON for 5 sec"
    _io.setRun()
    sleep(5)
    _io.clear()

    # Blink test
    print "Run LED blink 10 times"
    _io.blink(10)
    _io.clear()
    sleep(2)

        # Blink test
    print "Toggle REC LED"
    for i in range(0, 10):
        _io.toggleRec()
        sleep(0.5)
    _io.clear()

    print "Switch position = {}".format(str(_io.checkSwitch(1)))
    sleep(2)

    print "Test Done"
