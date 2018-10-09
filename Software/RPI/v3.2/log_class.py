#!/usr/bin/python2

'''
    Changed: October 9, 2018

    Class to log data in a log file
    Every message is timestamped and
    Opens and closes the file on every log

'''

import datetime, subprocess, os
from time import sleep              # sleep function in seconds

class LogClass():
    PATH = "/home/pi/log.txt"   # default path for storing file


    # set file path on creation of the file
    def __init__(self, file_path):
        self.PATH = file_path
    

    # writing single line statement starting with the date
    def write(self, _str):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " | "
        with open(self.PATH, "a") as _file:
            _file.write(now + _str + '\n')
    

    # log CPU temperature into the file
    def logTemp(self):
        temp, err = subprocess.Popen(['/opt/vc/bin/vcgencmd', 'measure_temp'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
        temp = temp.splitlines()[0]
        self.write("CPU "+temp)
  

    # log CPU usage 
    def logCPU(self):
        # Return % of CPU used by user as a character string       
        # copied from a forum                         
        cpu, err = subprocess.Popen(['uptime'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
        cpu = cpu.splitlines()[0]
        self.write("CPU "+cpu[30:-1])


    # logs CPU throttling register
    # 0: under-voltage
    # 1: arm frequency capped
    # 2: currently throttled 
    # 16: under-voltage has occurred
    # 17: arm frequency capped has occurred
    # 18: throttling has occurred
    def logThrottle(self):
        cpu, err = subprocess.Popen(['/opt/vc/bin/vcgencmd', 'get_throttled'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
        cpu = cpu.splitlines()[0]
        self.write("CPU " + cpu[:-1])


    # logs RAM usage
    def logRAM(self):
        ram, err = subprocess.Popen(['free', '-h'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
        ram = (ram.splitlines())[1]
        self.write("free RAM "+ram[39:-36]+"B")

    # log CPU frequency
    def logFreq(self):
        cpu, err = subprocess.Popen(['/opt/vc/bin/vcgencmd', 'measure_clock', 'arm'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
        cpu = cpu.splitlines()[0]
        self.write("CPU "+cpu[:-1])

    # logs all the parameters in a row
    def logParam(self):
        self.logTemp()
        self.logCPU()
        self.logThrottle()
        self.logRAM()
        self.logFreq()

# When class module is started by itself
# Following code is used for testing the LED's
if __name__ == '__main__':

    # Create instance of log class
    _log = log = LogClass("/home/pi/log_test.txt")

    print "Debugging logging class"
    # Running a series test prints to the log
    _log.write("DEBUG START")
    _log.write("This is a debug run to check class performace")
    _log.logParam()
    _log.write("DEBUG FINISHED\n")
    # debug finished
    print "Debug session finished"
    print "Output file = /home/pi/log_test.txt"
    exit()