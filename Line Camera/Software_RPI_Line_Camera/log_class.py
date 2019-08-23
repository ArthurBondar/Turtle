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
        for line in _str:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " | "
            print(now + line)
            with open(self.PATH, "a") as _file:
                _file.write(now + line + '\r\n')

    def space(self):
        with open(self.PATH, "a") as _file:
            _file.write("\r\n")

    # log CPU temperature into the file
    def logTemp(self):
        out = "empty"
        try:
            out = subprocess.check_output(['/opt/vc/bin/vcgencmd', 'measure_temp'])
            out = out.decode().splitlines()[0]
        except subprocess.CalledProcessError as e:
            out = "ERROR: command failed code = "+str(e.returncode)+" msg = "+str(e.output)
        self.write("temp -> "+out)

    # log CPU usage
    def logCPU(self):
        # Return % of CPU used by user as a character string
        # copied from a forum
        out = "empty"
        try:
            out = subprocess.check_output(['uptime'])
            out = out.decode().splitlines()[0]
        except subprocess.CalledProcessError as e:
            out = "ERROR: command failed code = "+str(e.returncode)+" msg = "+str(e.output)
        self.write("cpu -> "+out[30:-1])

    # logs CPU throttling register
    # 0: under-voltage
    # 1: arm frequency capped
    # 2: currently throttled
    # 16: under-voltage has occurred
    # 17: arm frequency capped has occurred
    # 18: throttling has occurred
    def logThrottle(self):
        out = "empty"
        try:
            out = subprocess.check_output(['/opt/vc/bin/vcgencmd', 'get_throttled'])
            out = out.decode().splitlines()[0]
        except subprocess.CalledProcessError as e:
            out = "ERROR: command failed code = "+str(e.returncode)+" msg = "+str(e.output)
        self.write("overheat -> " + out)

    # logs RAM usage
    def logRAM(self):
        out = "empty"
        try:
            out = subprocess.check_output(['free', '-h'])
            out = (ram.decode().splitlines())[1]
            out = out[39:-36]
        except subprocess.CalledProcessError as e:
            out = "ERROR: command failed code = "+str(e.returncode)+" msg = "+str(e.output)      
        self.write("RAM -> "+out)

    # log CPU frequency
    def logFreq(self):
        out = "empty"
        try:
            out = subprocess.check_output(['/opt/vc/bin/vcgencmd', 'measure_clock', 'arm'])
            out = (out.decode().splitlines())[0]
        except subprocess.CalledProcessError as e:
            out = "ERROR: command failed code = "+str(e.returncode)+" msg = "+str(e.output)   
        self.write("clock -> "+out)

     # run iostat command to log
    def iostat(self):
        out = "empty\nempty"
        try:
            out = subprocess.check_output(['iostat', '-h', '1', '2'])
            out = (out.decode().splitlines())
        except subprocess.CalledProcessError as e:
            out = "ERROR: command failed code = "+str(e.returncode)+" msg = "+str(e.output)  
        for line in out:
            self.write("disk -> " +line)

        # logs all the parameters in a row
    def logParam(self):
        self.write("Parameters: ")
        self.logTemp()
        self.logCPU()
        self.logThrottle()
        self.logRAM()
        self.logFreq()
        self.iostat()
        self.write(" . . . . . . . ")

# When class module is started by itself
# Following code is used for testing the Class
if __name__ == '__main__':

    # Create instance of log class
    _log = LogClass("/home/pi/log_test.txt")

    print "Debugging logging class"
    # Running a series test prints to the log
    _log.write("DEBUG START")
    _log.write("This is a debug run to check class performace")
    _log.logParam()
    _log.write("DEBUG FINISHED")
    # debug finished
    print "Debug session finished"
    print "Output file = /home/pi/log_test.txt"
    exit()
