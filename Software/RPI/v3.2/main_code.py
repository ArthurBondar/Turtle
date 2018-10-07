#!/usr/bin/python2

'''
    October 7, 2018
    Version 3.2
    Arthur Bondar

    Underwater Camera system for POV Leatherback turtle recording
    Uses raspberry Pi camera throught raspivid program
    Recording starts and stop at designated times
    Communication with Arduino is impelented with I2C
    Arduino is used a timer for sleep cycle

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

'''

import os, sys, datetime            # essentials
from time import sleep              # sleep function in seconds
from timer_class import Timer       # custom made class for i2c com
from parser_class import SetupFile  # custom made class to read setup file
from led_class import Gpio_class    # custom made class to switch led's
from log_class import LogClass      # custom made class to log program status
from gps_class import GPS_class     # custom made class for gps readings
import subprocess                   # for subprocess opening

# Declaration of default parameters
DUR =               5               # video duration in minutes
VIDEO_SECTION =     2               # video sections duration
TEMP_FOLDER =       "/home/pi/Video/"
USB_FOLDER =        "/home/pi/USB/"
SETUP_FILE =        USB_FOLDER + "setup.txt"
LOG_FILE =          USB_FOLDER + "log.txt"
# Global Variables
TERM = False
camera = None
poll = 1
REC_FILE = ""

# Camera default paramters
# array of parameters is passed to raspivid program as cmd args
PARAM = [
    'raspivid',                 # program to call                                   (param 0)
    '-t', str(VIDEO_SECTION*60*1000),# videos duration in milliseconds              (param 2)
    '-o', TEMP_FOLDER+"noname.h264",# output file                                   (param 4)
    '-a', '12',                 # test annotations - time and date 20:09:33 10/28/15(param 6)
    '-md', '4',                 # video mode - check table to change                (param 8)
    '-rot', '180',              # rotation                                          (param 10)
    '-fps', '30',               # frames per second                                 (param 12)
    '-n'                        # No Preview
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
def start_section():
    global camera, REC_FILE
    # assemble filename
    REC_FILE = TEMP_FOLDER + datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S') + ".h264"
    PARAM[4] = REC_FILE             # parameter 4 is filename
    # start camera section
    camera = subprocess.Popen(PARAM,stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
    log.write("*** section started *** camera pid: "+str(camera.pid))
    print("*** section started *** camera pid: "+str(camera.pid))
    return camera.poll()

'''
# Remounting USB in ~/USB directory
# removing unnecessary existing files
os.system("sudo umount /dev/sda1")
sleep(2)
os.system("sudo rm "+TEMP_FOLDER+"*")   # Removing temp files
os.system("sudo rm "+USB_FOLDER+"*")    # Removing old usb files
os.system("sudo mount /dev/sda1 "+USB_FOLDER) # mounting USB
sleep(2)
'''

# Creating instance of objects
# classes used for: parsing setup file, GPIO controll and I2C commands
log = LogClass(LOG_FILE)                # Log file object
timer = Timer()                         # Arduino COM object
setup_file = SetupFile(SETUP_FILE)      # Setup file object
io = Gpio_class()                       # GPIO class (switch,led,alive)
io.clear()                              # turn off al LEDs
gps = GPS_class(USB_FOLDER)             # GPS object
gps.setTime()

# Logging beginning of the program 
# indicate beginning of the code with LED flashing 
log.write("START")
io.blink(10)                        

# getting full deployment duration and sending to arduino
# checking if release time has been set
flag = timer.checkStatus()
if flag[1] == 0:
    # parsing release time from file
    time = []*2
    time = setup_file.getParam("release")
    log.write("setting release time for: "+str(time[0])+"hr "+str(time[1])+"min")
    try:
        if not time == 0: 
            resp = timer.setRelease(time[0], time[1])
            if resp == True: log.write("release time set succesfully")
            else:            log.write("release time set failed")
    except Exception as exp:
        log.write(str(exp))
        pass
    

# Parse setup.txt file and get data
# -----------------------------------------------
# get battery voltage from Arduino using I2C
log.write("battery voltage is "+timer.getVoltage()+"v")
# get video recording duration from setupfile
REC_DUR = setup_file.getParam("recording")
log.write("recording time is "+str(REC_DUR)+" min")
print("recording time is "+str(REC_DUR)+" min")
# getting video sections from setupfile
section = setup_file.getParam("sections")
# Error checking and converting to milliseconds to pass to raspivid
if section > 0 and section <= 720:          
	VIDEO_SECTION = section
	PARAM[2] = str(VIDEO_SECTION*60*1000)
log.write("recording sections "+str(VIDEO_SECTION)+" min")
# getting video parameters (width and height) according to table
v_mode = setup_file.getParam("videomode")
if v_mode >= 0 and v_mode < 8: PARAM[8] = str(v_mode)
# frames per second
fps = setup_file.getParam("fps")
if fps > 0 and fps <= 90: PARAM[12] = str(fps)
# camera rotation
rot = setup_file.getParam("rotation")
if rot > 0 and rot < 360: PARAM[10] = str(rot)

# starting first video section
if REC_DUR > 0:
    poll = start_section()


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
        sleep(2)
        move(REC_FILE)              # move file to USB
        log.logTemp()               # log CPU usage and temperature
        log.logCPU()
        # substract interval from recording time
        # if recording time not over, start new section
        REC_DUR -= VIDEO_SECTION
        if REC_DUR > 0:
            log.write("recording time left: "+str(REC_DUR)+" min")
            print("recording time left: "+str(REC_DUR)+" min")
            # starting new camera recording
            poll = start_section()
    # ------

    # Checking for manual termination when switch/button used
    # Kills the current camera process and moves the file
    TERM = io.checkSwitch()
    if TERM == True:
        log.write("killing current camera process: "+str(camera.pid))
        camera.kill()
        sleep(5)
        move(REC_FILE)  # move file to USB
        break           # exiting the main loop when switch pulled low

    # set REC LED indicator on
    # update the poll - check if camera code is finished
    io.setRec()        
    log.write(gps.writeCSV())
    #gps.dumpData()     # debug
    sleep(5)
    poll = camera.poll()
# -----------------------------------------------


# if the code was terminated using button/switch
# exit the program without sleep cycle
if TERM == True:
    log.write("code terminated using Switch")
else:
    # if the program wasn't terminated
    # get sleep time from setup file and send to Arduino
    s_hr, s_min = setup_file.getParam("sleep") 
    log.write("recording finished, sleep for "+str(s_hr)+"hr "+str(s_min)+"min")
    # sending data to Arduino using I2C
    # format: (byte)hour, (byte)minute
    if timer.setSleep(s_hr, s_min): log.write("sleep set succesfully")
    else:                           log.write("sleep failed")


# Shutting down routine
# Blink and turn off LED indicators
io.blink(10)        # indicate code termination
io.clear()          # turn off both LED's
log.write("FINISH\n")
gps.close()         # close GPS thread
#os.system("sudo umount /home/pi/USB/")
#os.system("sudo shutdown -h now")
sys.exit()