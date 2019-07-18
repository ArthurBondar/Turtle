#!/usr/bin/python2

'''
    April 19, 2019
    Version 3.2
    Arthur Bondar

    Underwater Camera system for POV Leatherback turtle recording
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
    - Move the video file to USB
    - Start new section or exit
    END LOOP:
    - Send sleep time to Arduino for wakeup signal
    - Shutdown - start Halt state


    Updated: February 23, 2019
    1) Video sections stops when end of recording time reached
    2) Text annotation on video has black background
    3) Video bitrate can be set by the user

'''

import os, sys, datetime            # essentials
from time import sleep              # sleep function in seconds
from arduino_class import Arduino   # custom made class for i2c com
from parser_class import SetupFile  # custom made class to read setup file
from led_class import Gpio_class    # custom made class to switch led's
from log_class import LogClass      # custom made class to log program status
from timer_class import Timer       # custom class to make timing events
import subprocess                   # for subprocess opening

# Declaration of default parameters
DUR =               480             # video duration in minutes
VIDEO_SECTION =     20              # video sections duration min
TEMP_FOLDER =       "/home/pi/Video/"
USB_FOLDER =        "/home/pi/USB/"
SETUP_FILE =        USB_FOLDER + "setup.txt"
LOG_FILE =          USB_FOLDER + "log.txt"
REC_DAY =           3               # keeps track of the current deployment day
# Global Variables
TERM = False                        # switch termination flag
camera = None                       # camera object
poll = 1                            # check for camera thread execution
REC_FILE = ""                       # video section file name variable
led_state = False                   # boolean value to toggle PCB LED

# Camera default paramters
# array of parameters is passed to raspivid program as cmd args
PARAM = [
    'raspivid',                     # program to call                               (param 0)
    '-t', str(VIDEO_SECTION*60*1000),# videos duration in milliseconds              (param 2)
    '-o', TEMP_FOLDER+"noname.h264",# output file                                   (param 4)
    '-a', '12',                     # test annotations  20:09:33 10/28/15(param 6)  (param 6)
    '-md', '5',                     # video mode - check table to change            (param 8)
    '-rot', '180',                  # rotation                                      (param 10)
    '-fps', '30',                   # frames per second                             (param 12)
    '-b', '10000000'                # video bit-rate in bits (25M max, 15M good)    (param 14)
    '-n',                           # No Preview
    '-ae', '32,0xff,0x808000',      # Text annotation - Size,TextCol,BackgCol
    '-ih',                          # Add timing to I-frames, needed for software
    '-a', '1024',                   # Text black background
    '-pf', 'baseline'               # encoding profile
]

# move video file from Pi SD to USB
# uses cp and rm since mv cannot preserve permitions
def move(file_path):
    log.write("moving file: "+file_path+" to usb ...")
    print("moving file: "+file_path+" to usb ...")
    # move file and track the time
    now = datetime.datetime.now()
    os.system("sudo cp "+file_path+" "+USB_FOLDER)
    os.system("sudo rm "+file_path)
    diff = datetime.datetime.now() - now
    # log timing data
    log.write("move finished in: " +str(diff.seconds/60)+"min "+str(diff.seconds%60)+"sec")
    print("move finished in: " +str(diff.seconds/60)+"min "+str(diff.seconds%60)+"sec")

# start new camera recording section
# return camera.poll() -> None when running
def start_section(count):
    global camera, REC_FILE
    # assemble filename
    REC_FILE = TEMP_FOLDER + datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S') + ".h264"
    PARAM[4] = REC_FILE             # parameter 4 is filename
    # start camera section
    camera = subprocess.Popen(PARAM,stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
    log.write(" - - - - - - - - - - - ")
    log.write("section  started, camera pid: "+str(camera.pid))
    log.write("recording . . . . ")
    print("section ["+str(count)+"] started, camera pid: "+str(camera.pid))
    return camera.poll()

# set Arduino wake up time
# based on sleep parameter in setup file
def set_wakeup(_setup_file, _arduino, _log):
    # get sleep time from setup file and send to Arduino
    s_hr, s_min = _setup_file.getParam("sleep") 
    _log.write("setting sleep for "+str(s_hr)+"hr "+str(s_min)+"min")
    print("setting sleep for "+str(s_hr)+"hr "+str(s_min)+"min")
    # sending data to Arduino using I2C
    # format: (byte)hour, (byte)minute
    if _arduino.setSleep(s_hr, s_min): _log.write("sleep set: SUCCESS")
    else:                             _log.write("sleep set: FAILED")

# Shutting down routine
# finish recording, shutdown the device
def end_operation(_io, _log):
    # Blink and turn off LED indicators
    _io.clear()                              # turn off both LED's
    _io.blink(20)                            # indicate code termination
    _log.write("FINISH\r\n")
    os.system("sudo umount /home/pi/USB/")
    print("FINISH")
    sleep(5)
    os.system("sudo shutdown -h now")
    sys.exit()

# Creating instance of objects
# classes used for: parsing setup file, GPIO controll and I2C commands
log = LogClass(LOG_FILE)                # Log file object
arduino = Arduino()                     # Arduino COM object
setup_file = SetupFile(SETUP_FILE)      # Setup file object
io = Gpio_class()                       # GPIO class (switch,led,alive)
io.clear()                              # turn off al LEDs
led_timer = Timer(0, 1)                 # to toggle LEDs
rec_timer = Timer(1, 0)                 # checks if recording time is over

# Logging beginning of the program
# indicate beginning of the code with LED flashing
log.space()
log.write("START")
io.blink(20)

# Parse USB/setup.txt file and get data
# Saving the parameters for error checking
REC_DUR = setup_file.getParam("recording")         # get video recording duration from setupfile
section = setup_file.getParam("sections")          # getting video sections from setupfile
v_mode = setup_file.getParam("videomode")          # getting video parameters (width and height) according to table
fps = setup_file.getParam("fps")                   # frames per second
rot = setup_file.getParam("rotation")              # camera rotation
bitrate = setup_file.getParam("bitrate")           # get Video bitrate
REC_DAY = setup_file.getParam("days")              # get the current recording day
if REC_DAY < 1: 
    log.write("Error - device woke up with 0 recording days, check days value in setup.txt")
    end_operation(io, log)

# Error checking each parameter from file
# Overwriting default parameter array (PARAM)
if v_mode >= 0 and v_mode < 8: PARAM[8] = str(v_mode)
if fps > 0 and fps <= 90: PARAM[12] = str(fps)
if rot >= 0 and rot < 360: PARAM[10] = str(rot)
if bitrate >= 0 and bitrate <= 25: PARAM[14] = str(int(float(bitrate)*1000000))
if section > 0 and section <= 720:
	VIDEO_SECTION = section
	PARAM[2] = str(VIDEO_SECTION*60*1000) # Converting to milliseconds

# Logging parametes
log.write("battery voltage: "+arduino.getVoltage()+" V") # get battery voltage from Arduino using I2C
log.write("day - "+str(REC_DAY)+", left - "+str(REC_DAY - 1)+" days")
log.write("rec time: "+str(REC_DUR)+"m, each section: "+str(VIDEO_SECTION)+"m")
log.write("parameters "+str(PARAM))
print("recording time: "+str(REC_DUR)+" min, each section: "+str(VIDEO_SECTION)+" min")
print("parameters "+str(PARAM))

# Starting first video section
# start arduino for gps recodings
i_sec = 0 #section counter
if REC_DUR > 0:
    poll = start_section(i_sec)
    i_sec+=1
else:
    log.write("Warning - recording duration is 0")
    # Setting to the timer for a new recording day
    set_wakeup(setup_file, arduino, log)
    # sequence that unmonts the disk and shuts off the Pi
    end_operation(io, log)


# MAIN LOOP START
# exit conditions: recording time is over
# -----------------------------------------------
while REC_DUR > 0:

    # checking if section is finished
    # poll == None -> section is still running
    # 1. move file to USB
    # 2. start new recording
    if not poll == None:
        log.write("section finished")
        print("section finished")
        io.setRun()                 # indicating video processing (Green LED)
        log.logParam()              # log system parameters
        log.write("Temp "+arduino.getTemperature()+" C")
        log.write("battery voltage: "+arduino.getVoltage()+" V")
        move(REC_FILE)              # move file to USB
        # substract interval from recording time
        # if recording time not over, start new section
        REC_DUR -= VIDEO_SECTION
        if REC_DUR > 0:
            log.write("recording time left: "+str(REC_DUR)+" min")
            print("recording time left: "+str(REC_DUR)+" min")
            poll = start_section(i_sec)  # starting new camera recording
            i_sec+=1

    # Checking for manual termination when switch/button used
    # Kills the current camera process and moves the file
    TERM = io.checkSwitch()
    if TERM == True:
        log.write("code TERMINATED using switch")
        log.write("closing camera process: "+str(camera.pid))
        camera.kill()
        log.logParam()              # log system parameters
        log.write("Temp "+arduino.getTemperature()+" C")
        log.write("battery voltage: "+arduino.getVoltage()+" V")
        io.setRun()                 # indicating video moving (Green LED)
        sleep(1)
        move(REC_FILE)              # move file to USB
        end_operation(io, log)

    # Check to see if recording time is over
    # interval for readings in 1 minutes
    if rec_timer.check() == True:
        if setup_file.getParam("recording") <= 0:
            log.write("recording time is over")
            log.write("closing camera process: "+str(camera.pid))
            camera.kill()
            log.logParam()              # log system parameters
            log.write("Temp "+arduino.getTemperature()+" C")
            log.write("battery voltage: "+arduino.getVoltage()+" V")
            io.setRun()                 # indicating video moving (Green LED)
            sleep(5)
            move(REC_FILE)              # move file to USB
            break                       # exiting the main loop
        # reseting the timer to start a new minute
        rec_timer.reset()               
        
    # set REC LED indicator on
    # update the poll - check if camera code is finished
    if led_timer.check() == True:
        if led_state == True: 
            io.clear()
            led_state = False
        else:
            io.setRec()
            led_state = True
        led_timer.reset()

    sleep(0.2)
    poll = camera.poll()
# -----------------------------------------------
# MAIN LOOP END

# If another day is left in deployment, set up the wake up Arduino timer
if REC_DAY > 1:
    # Setting to the timer for a new recording day
    set_wakeup(setup_file, arduino, log)
else:
    # setting the yellow LED to let user know rec cycle is finished
    arduino.setRelease(0, 1)

# Decrementing deployment day counter in setup.txt
setup_file.setDays(REC_DAY, REC_DAY - 1)
log.write("recording days left: "+str(REC_DAY - 1))

# sequence that unmonts the disk and shuts off the Pi
end_operation(io, log)
