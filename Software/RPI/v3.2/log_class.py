#!/usr/bin/python2

'''
    Changed: October 7, 2018

    Class to log data in a log file
    Every message is timestamped and
    Opens and closes the file on every log

'''

import datetime, subprocess, os

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
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " | CPU "
        p = subprocess.Popen(['/opt/vc/bin/vcgencmd', 'measure_temp'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        temp = p.stdout.readline()
        with open(self.PATH, "a") as _file:
            _file.write(now + str(temp))
  

    # log CPU usage 
    def logCPU(self):
        # Return % of CPU used by user as a character string       
        # copied from a forum                         
        string = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " | CPU load="
        string += str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline())
        with open(self.PATH, "a") as _file:
            _file.write(string + '\n')
  

# When class module is started by itself
# Following code is used for testing the LED's
if __name__ == '__main__':

    # Create instance of log class
    _log = log = LogClass("/home/pi/log_test.txt")

    print "Debugging logging class"
    # Running a series test prints to the log
    _log.write("DEBUG START")
    _log.write("This is a debug run to check class performace")
    _log.logTemp()
    _log.logCPU()
    _log.write("DEBUG FINISHED\n")
    # debug finished
    print "Debug session finished"
    print "Output file = /home/pi/log_test.txt"
    exit()