#!/usr/bin/python2

'''
    October 7, 2018
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

'''

import os, sys, datetime            # essentials
from time import sleep              # sleep function in seconds
from arduino_class import Arduino   # custom made class for i2c com
from parser_class import SetupFile  # custom made class to read setup file
from led_class import Gpio_class    # custom made class to switch led's
from log_class import LogClass      # custom made class to log program status
from gps_class import GPS_class     # custom made class for gps readings
from timer_class import Timer       # custom class to make timing events
import subprocess                   # for subprocess opening

# Declaration of default parameters
DUR =               480             # video duration in minutes
VIDEO_SECTION =     20              # video sections duration min
TEMP_FOLDER =       "/home/pi/Video/"
USB_FOLDER =        "/home/pi/USB/"
SETUP_FILE =        USB_FOLDER + "setup.txt"
LOG_FILE =          USB_FOLDER + "log.txt"
# Global Variables
TERM = False                        # switch termination flag
camera = None                       # camera object
poll = 1                            # check for camera thread execution
REC_FILE = ""                       # video section file name variable
gps_interval = 20                   # interval for gps logging in sec
led_state = False                   # boolean value to toggle PCB LED

# Camera default paramters
# array of parameters is passed to raspivid program as cmd args
PARAM = [
    'raspivid',                     # program to call                               (param 0)
    '-t', str(VIDEO_SECTION*60*1000),# videos duration in milliseconds              (param 2)
    '-o', TEMP_FOLDER+"noname.h264",# output file                                   (param 4)
    '-a', '12',                     # test annotations  20:09:33 10/28/15(param 6)  (param 6)
    '-md', '4',                     # video mode - check table to change            (param 8)
    '-rot', '180',                  # rotation                                      (param 10)
    '-fps', '30',                   # frames per second                             (param 12)
    '-n'                            # No Preview
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
    os.system("sync")
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
    log.write("***********************")
    log.write("section started, camera pid: "+str(camera.pid))
    print("section started, camera pid: "+str(camera.pid))
    return camera.poll()

# Creating instance of objects
# classes used for: parsing setup file, GPIO controll and I2C commands
log = LogClass(LOG_FILE)                # Log file object
arduino = Arduino()                     # Arduino COM object
setup_file = SetupFile(SETUP_FILE)      # Setup file object
io = Gpio_class()                       # GPIO class (switch,led,alive)
io.clear()                              # turn off al LEDs
led_timer = Timer(0, 1)                 # to toggle LEDs
gps = GPS_class(USB_FOLDER)             # GPS object
gps.setTime()
gps_timer = Timer(0, gps_interval)      # timer take reading every 30s by default

# Logging beginning of the program 
# indicate beginning of the code with LED flashing 
log.write("START")
io.blink(20)                        

# getting full deployment duration and sending to arduino
# checking if release time has been set
flag = arduino.checkStatus()
if flag[1] == 0:
    # parsing release time from file
    time = []*2
    time = setup_file.getParam("release")
    log.write("setting release time: "+str(time[0])+"hr "+str(time[1])+"min")
    try:
        if not time == 0: 
            resp = arduino.setRelease(time[0], time[1])
            if resp == True: log.write("release set: SUCCESS")
            else:            log.write("release set: FAILED")
    except Exception as exp:
        log.write(str(exp))
        pass
    
# Parse USB/setup.txt file and get data
# Saving the parameters for error checking
REC_DUR = setup_file.getParam("recording")         # get video recording duration from setupfile
section = setup_file.getParam("sections")          # getting video sections from setupfile
v_mode = setup_file.getParam("videomode")          # getting video parameters (width and height) according to table
fps = setup_file.getParam("fps")                   # frames per second
rot = setup_file.getParam("rotation")              # camera rotation
gps_interval = setup_file.getParam("gpsinterval")  # get GPS logging interval

# Error checking each parameter from file
# Overwriting default parameter array (PARAM)
if v_mode >= 0 and v_mode < 8: PARAM[8] = str(v_mode)
if fps > 0 and fps <= 90: PARAM[12] = str(fps)
if rot >= 0 and rot < 360: PARAM[10] = str(rot)
if gps_interval > 0 and gps_interval < 3600: gps_timer.set_time(0, gps_interval)
if section > 0 and section <= 720:   
	VIDEO_SECTION = section
	PARAM[2] = str(VIDEO_SECTION*60*1000)          # Converting to milliseconds to pass to raspivid 

# Logging parametes
#log.write("battery voltage: "+arduino.getVoltage()+"v")# get battery voltage from Arduino using I2C
log.write("recording time: "+str(REC_DUR)+" min, each section: "+str(VIDEO_SECTION))
log.write("gps sample interval: "+str(gps_interval)+" sec")
log.write("video param: "+str(PARAM))
print("recording time: "+str(REC_DUR)+" min, each section: "+str(VIDEO_SECTION)+" min")
print("gps recording interval: "+str(gps_interval)+" sec")
print("video param: "+str(PARAM))

# Starting first video section
# start arduino for gps recodings
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
        sleep(1)
        move(REC_FILE)              # move file to USB
        log.logParam()              # log system parameters
        sleep(1)
        # substract interval from recording time
        # if recording time not over, start new section
        REC_DUR -= VIDEO_SECTION
        if REC_DUR > 0:
            log.write("recording time left: "+str(REC_DUR)+" min")
            print("recording time left: "+str(REC_DUR)+" min")
            poll = start_section()  # starting new camera recording

    # Checking for manual termination when switch/button used
    # Kills the current camera process and moves the file
    TERM = io.checkSwitch()
    if TERM == True:
        log.write("killing camera process: "+str(camera.pid))
        camera.kill()
        sleep(5)
        move(REC_FILE)              # move file to USB
        break                       # exiting the main loop when switch pulled low

    # logging GPS data (when fix is present)
    # interval for readings in seconds
    if gps_timer.check() == True:
        gps.writeCSV()
        gps_timer.reset()
        
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

# if the code was terminated using button/switch
# exit the program without sleep cycle
if TERM == True:
    log.write("code TERMINATED using switch")
else:
    # if the program wasn't terminated
    # get sleep time from setup file and send to Arduino
    s_hr, s_min = setup_file.getParam("sleep") 
    log.write("setting sleep for "+str(s_hr)+"hr "+str(s_min)+"min")
    # sending data to Arduino using I2C
    # format: (byte)hour, (byte)minute
    if arduino.setSleep(s_hr, s_min): log.write("sleep set: SUCCESS")
    else:                             log.write("sleep set: FAILED")

# Shutting down routine
# Blink and turn off LED indicators
io.clear()                              # turn off both LED's
io.blink(20)                            # indicate code termination
log.write("FINISH\n")
gps.close()                             # close GPS thread
os.system("sudo umount /home/pi/USB/")
print("SHUTTING DOWN")
sleep(5)
os.system("sudo shutdown -h now")
exit()