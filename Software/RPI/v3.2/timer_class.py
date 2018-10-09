#!/usr/bin/python2

'''
    Changed: October 9, 2018

    Class to make timing evens
    To toggle LED or make GPS recordings

'''

import datetime
from time import sleep              # sleep function in seconds

class Timer():

    INVERVAL_S = 0                  # inverval in seconds
    START = 0

    # Constructor
    # Uses min and seconds to set the timer
    def __init__(self, min, sec):
        # Save users time interval
        self.set_time(min, sec)
        # set the timer
        self.reset()

    # check if time since reset passed
    def check(self):
        # check if time elapsed
        if (datetime.datetime.now() - self.START).seconds > self.INVERVAL_S:
            return True
        else:
            return False

    # reset the stopwatch, start new count
    def reset(self):
        self.START = datetime.datetime.now()

    # set time for timer
    def set_time(self, min, sec):
        # Save users time interval
        if min > 0 and sec > 0:
            self.INVERVAL_S = min*60 + sec