#!/usr/bin/python2

'''
    September 7, 2019
    Line Camera Rev. A

    Uses raspberry Pi camera throught raspivid program
    Recording starts and stop at designated times
    Communication with Arduino is impelented with I2C
    Arduino is used a arduino for sleep cycle

    Main program flow:
    - Declare default video recording parameters
    - Parse setup file from USB and overwrite video parameters
    - Get sleep time cycle from setup file
    - Start frist video section
    LOOP:
    - Check for video section to finish
    - Start new section or exit
    END LOOP:
    - Send sleep time to Arduino for wakeup signal
    - Shutdown - enter Halt state
'''

import os, sys, datetime            # essentials
from time import sleep              # sleep function in seconds
from arduino_class import Arduino   # custom made class for i2c com
from parser_class import SetupFile  # custom made class to read setup file
from led_class import Gpio_class    # custom made class to switch led's
from log_class import LogClass      # custom made class to log program status
from timer_class import Timer       # custom class to make timing events
from gps_class import GPS_class     # custom gps class
import subprocess                   # for subprocess opening

# Declaration of default parameters
SOFTWARE_V = "Sep 9, 2019"
DUR =               480             # video duration in minutes
VIDEO_SECTION =     20              # video sections duration min
USB_FOLDER =        "/home/pi/USB/"
SETUP_FILE =        USB_FOLDER + "setup.txt"
LOG_FILE =          USB_FOLDER + "log.txt"
REC_DAY =           3               # keeps track of the current deployment day
# Global Variables
camera = None                       # camera object
poll = 1                            # check for camera thread execution
REC_FILE = ""                       # video section file name variable
led_state = False                   # boolean value to toggle PCB LED
gps_enable = 0                      # boolean value the gps module
DEBUG = False			    # code in debug mode

# Camera default paramters
# array of parameters is passed to raspivid program as cmd args
PARAM = [
    'raspivid',                     # program to call                               (param 0)
    '-t', str(VIDEO_SECTION*60*1000), # videos duration in milliseconds             (param 2)
    '-o', USB_FOLDER+"noname.h264", # output file                                   (param 4)
    '-a', '12',                     # test annotations  20:09:33 10/28/15(param 6)  (param 6)
    '-md', '5',                     # video mode - check table to change            (param 8)
    '-rot', '180',                  # rotation                                      (param 10)
    '-fps', '30',                   # frames per second                             (param 12)
    '-b', '10000000'                # video bit-rate in bits (25M max, 15M good)    (param 14)
    '-n',                           # No Preview
    '-ae', '32,0xff,0x808000',      # Text annotation - Size,TextCol,BackgCol
    '-ih',                          # Add timing to I-frames, needed for software
    '-a', '1024'                    # Text black background
]

# start new camera recording section
# return camera.poll() -> None when running
def start_section(_log, count):
    global camera, REC_FILE
    # assemble filename
    REC_FILE = USB_FOLDER + "s"+str(count)+"_" + datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S') + ".h264"
    PARAM[4] = REC_FILE                             # parameter 4 is filename
    # start camera section
    camera = subprocess.Popen(PARAM,stdout = subprocess.PIPE,stderr = subprocess.PIPE)
    sleep(1)
    _log.write("section ["+str(count)+"] started | camera pid: "+str(camera.pid)+" | ret code: "+str(camera.poll())+" | recording ...")
    return camera.poll()

# set Arduino wake up time
# based on sleep parameter in setup file
def set_wakeup(_setup_file, _arduino, _log):
    # get sleep time from setup file and send to Arduino
    s_hr, s_min = _setup_file.getParam("sleep")
    _log.write("setting sleep for "+str(s_hr)+"hr "+str(s_min)+"min")
    # format: (byte)hour, (byte)minute sending data to Arduino using I2C
    if _arduino.setSleep(s_hr, s_min):  _log.write("Arduino sleep set succesfully")
    else:                               _log.write("ERROR: failed setting sleep interval with Arduino ")

# Shutting down routine
# finish recording, shutdown the device
def end_operation(_io, _log):
    global DEBUG
    _io.blink(10)                            # indicate code termination
    if DEBUG == False:
    	_log.write("deployment FINISHED - unmounting usb\r\n")
    	subprocess.call(['umount', USB_FOLDER])
    	subprocess.call(['poweroff'])
        sys.exit()
    else:
	_log.write("FINISHED - debug mode")
	sys.exit()

# Save CPU and IO parameters to the log file
def log_parameters(_io, _log, _arduino):
    global camera
    _io.clear()
    _io.setRun()
    _log.logParam()              	    # log system parameters
    _log.write("Temp "+arduino.getTemperature()+" C")
    _log.write("battery voltage: "+arduino.getVoltage()+" V")
    sleep(2)

# Run Linux Shell Command as a process and log the result - output in log file
def run_cmd (args, cmd_name):
    out = "none"
    try:
        out = subprocess.check_output(args)             # run command and wait for output
        log.write(cmd_name+" finished succesfully")
        return out
    except subprocess.CalledProcessError as e:          # catch non 0 process exit status
        log.write("ERROR: "+cmd_name+" failed | command = "+str(e.cmd)+" | exit code = "+str(e.returncode)+" | output = "+str(e.output)+" | out2 = "+str(out))


# Creating instance of objects
# classes used for: parsing setup file, GPIO controll and I2C commands
log = LogClass(LOG_FILE)                # Log file object
arduino = Arduino()                     # Arduino COM object
setup_file = SetupFile(SETUP_FILE)      # Setup file object
pcb_type = setup_file.getParam("boardversion") # Getting board version string
io = Gpio_class( pcb_type )             # GPIO class (switch,led,alive)
io.clear()                              # turn off al LEDs
led_timer = Timer(0, 0.5)                 # to toggle LEDs
rec_timer = Timer(0, 10)                # checks if recording time is over

# Logging beginning of the program
# indicate beginning of the code with LED flashing
log.space()
log.write("START")
if len(sys.argv) > 1:
	DEBUG = True	# Check if debug mode should be entered
	log.write("Debug Mode entered")
log.write("board type: "+pcb_type+", software: "+SOFTWARE_V)
io.blink(10)

# Parse USB/setup.txt file and get data
# Saving the parameters for error checking
section = setup_file.getParam("sections")          # getting video sections from setupfile
v_mode = setup_file.getParam("videomode")          # getting video parameters (width and height) according to table
fps = setup_file.getParam("fps")                   # frames per second
rot = setup_file.getParam("rotation")              # camera rotation
bitrate = setup_file.getParam("bitrate")           # get Video bitrate
REC_DAY = setup_file.getParam("days")              # get the current recording day
log_timer = Timer(int(setup_file.getParam("loginterval")), 0) # Timer to log CPU and IO data
# Enabling the GPS module
gps_enable = setup_file.getParam("gpsenable")      # value to enable of disable use of the GPS
if gps_enable == 1:
    gps_timer = Timer(0, int(setup_file.getParam("gpsinterval"))) # Timer to log GPS data to CSV
    gps = GPS_class(USB_FOLDER)
    log.write("GPS enabled")
else:
    run_cmd(['killall', 'gpsd'], "disabling gps process")   # disabling GPSD process

# Setting TimeZone
if setup_file.getParam("settimezone") == 1:
    new_tz = setup_file.getParam("newtimezone")
    run_cmd(['rm', '/etc/localtime'], "remove previous time zone")
    run_cmd(['ln', '-s', '/usr/share/zoneinfo/'+new_tz, '/etc/localtime'], "set time zone")
    log.logTZ()
# Setting DateTime
if setup_file.getParam("setdate-time") == 1:
    new_dt = setup_file.getParam("newdate-time")
    run_cmd(['date', '+\'%Y-%m-%dT%H:%M:%S\'', '-s', new_dt], "set date-time")
    # Write time to RTC
    run_cmd(['hwclock', '--systohc'], "write time to RTC")

# Syncing time from RTC to the system and removing RTC polling to use i2c buss
run_cmd(['hwclock', '--hctosys'], "read time from RTC")
run_cmd(['rmmod', 'rtc_ds1307'], "remove RTC polling")

if REC_DAY < 1:
    log.write("Error - device woke up with 0 recording days, check days value in setup.txt")
    end_operation(io, log)

# Error checking each parameter from file
# Overwriting default parameter array (PARAM)
REC_DUR = setup_file.getParam("recording")         # get video recording duration from setupfile
if v_mode >= 0 and v_mode < 8: PARAM[8] = str(v_mode)
if fps > 0 and fps <= 90: PARAM[12] = str(fps)
if rot >= 0 and rot < 360: PARAM[10] = str(rot)
if bitrate >= 0 and bitrate <= 25: PARAM[14] = str(int(float(bitrate)*1000000))
if section > 0 and section <= 720:
	VIDEO_SECTION = section
	PARAM[2] = str(VIDEO_SECTION*60*1000) # Converting to milliseconds

# Logging parametes
log.write("battery voltage: "+arduino.getVoltage()+" V") # get battery voltage from Arduino using I2C
log.write("day - "+str(REC_DAY)+",  left - "+str(REC_DAY - 1)+" days")
log.write("start time: "+str(setup_file.getParam("start"))+",  end time: "+str(setup_file.getParam("end")))
log.write("rec duration: "+str(REC_DUR)+"m,  each section: "+str(VIDEO_SECTION)+"m")
log.write("parameters "+str(PARAM))

# Starting first video section
i_sec = 0                                       # video section counter
if REC_DUR > 0:
    poll = start_section(log, i_sec)
    log_parameters(io, log, arduino)
    i_sec+=1
else:
    log.write("WARNING: recording duration is 0, device woke up before start time")
    set_wakeup(setup_file, arduino, log)        # Setting to the timer for a new recording day
    end_operation(io, log)                      # sequence that unmonts the disk and shuts off the Pi


# MAIN LOOP START
# exit conditions: recording time is over / switch triggered / camera failed
# -----------------------------------------------
while REC_DUR > 0:

    # checking if section is finished and starting new section
    # poll == None -> section is still running
    if not poll == None:
	if camera.returncode != 0:		# checking for critinal camera errors
		log.write("ERROR: Camera process failed | strerr = "+camera.stderr.read().decode()+"| code = "+str(camera.returncode))
		break				# terminate if camera returned non zero
        log.write("section finished")
        # substract interval from recording time
        # if recording time not over, start new section
        REC_DUR -= VIDEO_SECTION
        if REC_DUR > 0:
            log.write("recording time left: "+str(REC_DUR)+" min")
            poll = start_section(log, i_sec)  # starting new camera recording
            i_sec+=1
        sleep(5)

    # Checking for manual termination when switch/button used
    # Kills the current camera process and moves the file
    terminate = io.checkSwitch(1)
    if terminate == True:
        log.write("code TERMINATED using switch")
        log.write("closing camera process: "+str(camera.pid))
        camera.kill()
        log_parameters(io, log, arduino)
        sleep(0.5)
        end_operation(io, log)

    # Check to see if recording time is over
    # interval for readings in 1 minutes
    if rec_timer.check() == True:
        if setup_file.getParam("recording") <= 0:
            log.write("recording time is over")
            log.write("closing camera process: "+str(camera.pid))
            camera.kill()
            log_parameters(io, log, arduino)
            sleep(0.5)
            break          # exiting the main loop
        # reseting the timer to start a new minute
        rec_timer.reset()

    # GPS data recording
    if gps_enable == 1:
        if gps_timer.check() == True:
            gps.writeCSV()
            gps_timer.reset()

    # set REC LED indicator on
    # update the poll - check if camera code is finished
    if led_timer.check() == True:
        io.toggleRec()
        led_timer.reset()

    # Write system parameters (CPU, IO, V) to the log file
    if log_timer.check() == True:
        log_parameters(io, log, arduino)
        log_timer.reset()

    sleep(0.25)
    poll = camera.poll()
# -----------------------------------------------
# MAIN LOOP END

# If another day is left in deployment, set up the wake up Arduino timer
if REC_DAY > 1:
    set_wakeup(setup_file, arduino, log)    # Setting to the timer for a new recording day

# Decrementing deployment day counter in setup.txt
setup_file.setDays(REC_DAY, REC_DAY - 1)
log.write("recording days left: "+str(REC_DAY - 1))
#if gps_enable == 1:
#	log.write("closing GPS module")
#	gps.close()     # hangs and breaks the code !

# sequence that unmonts the disk and shuts off the Pi
end_operation(io, log)
