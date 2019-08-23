#!/usr/bin/python2

'''
    August 18, 2019

    Class to interract with setup.txt file
    Parses according to the following format list:
    [parameter]=[value][\n(Linux)\r\n(Windows)]

    Loading the parameter-value list into integer arrays
    Index of is used to loop throught and retrieve data
    This class relies on currect system time to calculate
    sleep and recording interval from the file
''' 

import datetime, sys
from time import sleep              # sleep function in seconds

class SetupFile():
    # default parameters overwritten by parsed data from setup file
    filepath = "/home/pi/USB/setup.txt"
    delim = '='     
    param = []
    value = []
    start = "08:00"
    end = "17:00"
    datetime = "18-08-2019_18:30:30"   # format +"%d-%m-%Y_%T"
    timezone = "America/Halifax"       # default TZ

    # Constructor - opens the file and loads all the data into arrays
    def __init__(self, path):
        self.param = []
        self.value = []
        self.filepath = path
        # Openning the file as Universal format
        # since Windows uses /r/n convention and Unix/Linux only /n
        # loading parameter-value pair into corresponding array
        with open(self.filepath, 'rU') as _file:
            # loop throught each line
            for line in _file:
                line = line.replace(" ","")                             # remove white spaces
                if line and line[0].isalpha():                          # skip comments
                    try:
                        p,val = line.split(self.delim)                  # split delimiter (=)
                        val = val.replace("\r", "").replace("\n", "")   # strip /r/n
                        self.param.append(p)                            # save param in array (int)
                        if val == "yes":        self.value.append(1)    # interpret yes as a 1
                        elif val == "no":       self.value.append(0)    # no as a 0
                        else:                   self.value.append(val)  # save value in array as int
                        # save special (string) parameters into separate variables
                        if(p == "start"): self.start = val
                        if(p == "end"): self.end = val
                        if(p == "newdate-time"): self.datetime = val
                        if(p == "newtimezone"): self.timezone = val
                    except Exception as e: 
                        print(str(e))

    # Return value based on parameter name
    # runs throught the array and searches for parameter
    # return 0 if parameter not found
    def getParam(self, parameter):
        try:
            # returning calculated sleep and recording interval
            # calculation based on start-end time, format: [hour]:[minute]
            if(parameter == "sleep"): return self.calcSleep()
            if(parameter == "recording"): return self.calcRec()
            if(parameter == "start"): return self.start
            if(parameter == "end"): return self.end
            if(parameter == "newdate-time"): return self.datetime
            if(parameter == "newtimezone"): return self.timezone
            # returning any other parameter from the file
            for i in range(len(self.param)):
                if(self.param[i] == parameter): return int(self.value[i])

        except Exception as e:
            print e
        
        # return 0 if a parmeter not found
        return 0

    # Calculates and returns sleep interval
    # format: (int) [hour,min] array of 2 elements
    # sleep time is calculated from start and end time
    # sleep interval: time < start, time > end
    def calcSleep(self):
        try:
            # Converting from [hour]:[minute] notation
            # to [minute] parameter
            _start = self.toMin(self.start)             # start time
            _now = datetime.datetime.now()              # current time
            _now = self.toMin(str(_now.hour)+":"+str(_now.minute))

            # Two cases are possible when camera is started
            # 1. Camera is started before start time
            # sleep: sleeping untill start time 
            if(_now <= _start):
                duration = _start - _now

            # 2. Camera is past start time
            # Sleeping until the next days (next start time)
            # Adding 24-hours in minutes to start value
            elif(_now > _start): 
                _start += 1440
                duration = _start - _now
            
            # break down to [hh,mm] from [minutes]
            # returning in array format
            hr = int(duration/60)
            m = duration%60
            return [hr, m]

        except Exception as exp:
            print exp
            pass

        # default return in case of failure 15hr sleep
        return [15, 0]


    # Calculated and returns recording interval
    # format: (int) interval in minutes
    # recording time calculated from start and end time 
    # recording inverval: start < time < end
    def calcRec(self):
        try:
            # Converting from [hour]:[minute] notation to [minutes]
            # uses start,end and current time
            _start = self.toMin(self.start)             # start time
            _end = self.toMin(self.end)                 # end time
            _now = datetime.datetime.now()              # current time
            _now = self.toMin(str(_now.hour)+":"+str(_now.minute))

            # Two cases are possible when camera is started
            # 1. Camera is started within recording interval time
            # rec inverval: difference between end time and start time
            if(_now >= _start and _now <= _end):
                interval = _end - _now
            # 2. Camera is started before designated time
            # rec interval is 0m
            elif(_now > _end or _now < _start): 
                interval = 0
            # returning recording interval in minutes
            return interval

        except Exception as exp:
            print exp

        # default return in case of failure 8hrs - 480m
        return 480


    # convert from string [hh]:[mm] to int [min]
    # return 0 if code failed to parse data
    def toMin(self, str_time):
        try:
            hr, min = str_time.split(':')
            return int(hr)*60 + int(min)

        except Exception as exp:
            print exp

        # default return
        return 0


    # Returns the full content of the param:value pair
    # used to test the class
    def dump(self):
        for i in range(len(self.param)):
            try:
                print "[{}] {} : {}".format( str(i), self.param[i], self.value[i])
            except: pass


    # End of deployment day
    # Decrement the day value in the days file
    def setDays(self, old_val, new_val):
        val_found = False
        # Openning the file as Universal format
        new_lines = []
        with open(self.filepath, 'rU') as _file:
            for line in _file:
                if line.replace(" ", "").replace("\r", "").replace("\n", "") == "days="+str(old_val):
                    val_found = True
                    line = "days = "+str(new_val)+"\r\n"
                new_lines.append(line)
        # rewriting the file with new days time
        if val_found == True:
            with open(self.filepath, 'w') as _file:
                for line in new_lines:
                    _file.write(line)
            return "File rewritten"
        else:
            return "Days value not found"

                
# END Setup Class


# When class module is started by itself
# Following code is used for testing the parser class
# Accepts file path for setup file as input
if __name__ == '__main__':

    try:
        _SETUP_FILE = str(sys.argv[1])
    except:
        print "not enough arguments provided"
        exit()

    print "Test code started\nfile = "+_SETUP_FILE

    setup_file = SetupFile(_SETUP_FILE)

    print "Dumpint data -----------------------"
    setup_file.dump()

    print "Sleep inverval: {}".format(str(setup_file.calcSleep()))
    print "Recording inverval: {}m".format(str(setup_file.calcRec()))

    day = setup_file.getParam("days")
    print "Changing deployment days: {}".format(setup_file.setDays(day, day - 1))
    del setup_file

    print "Dumpint data -----------------------"
    setup_file = SetupFile(_SETUP_FILE)
    setup_file.dump()

    print "Changing deployment days: {}".format(setup_file.setDays(day - 1, day))
    del setup_file

    print "Dumpint data -----------------------"
    setup_file = SetupFile(_SETUP_FILE)
    setup_file.dump()