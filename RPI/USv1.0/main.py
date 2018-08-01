#!/usr/bin/python2

'''

    July 30, 2018
    US version 1.0
    Arthur Bondar

    Underwater Camera system for POV Leatherback turtle recording
    Uses raspberry Pi camera throught raspivid program
    Recording starts and stop at designated times
    Communication with Arduino is impelented with I2C
    Arduino is used a timer for sleep cycle

    Main program flow:
    - Declare default video recording parameters
    - Parse setupfile and overwrite video parameters
    - Get sleep time cycle from setup file
    LOOP:
    - Start video section
    - Move old section to USB file
    - Record mission data to log file
    END LOOP:
    - Move remaining secion
    - Send sleep time to Arduino for wakeup signal
    - Shutdown - start Halt state

'''

import os, sys, datetime            # essentials
from time import sleep              # sleep function in seconds
from timer_class import Timer       # custom made class for i2c com
from parser_class import SetupFile  # custom made class to read setup file
from led_class import Gpio_class    # custom made class to switch led's
from log_class import LogClass      # custom made class to log program status
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
NEW_FILE = ""
OLD_FILE = ""
# Camera default paramters
# array of parameters is passed to raspivid program as cmd args
PARAM = [
    'raspivid',                 # program to call                                   (param 0)
    '-t', str(VIDEO_SECTION*60*1000),# videos duration in milliseconds              (param 2)
    '-o', TEMP_FOLDER+"noname.h264",# output file                                   (param 4)
    '-a', '12',                 # test annotations - time and date 20:09:33 10/28/15(param 6)
    '-ae', '32,0xff,0x808000',  # white test on black background                    (param 8)
    '-w', '1640',               # image width   1920x1080-16:9-30fps-FOV:partial    (param 10)
    '-h', '1232',               # image height  1640x1232-4:3-40fps-FOV:Full        (param 12)
    '-b', '15000000',           # bit rate, for 1080p30 15Mbits/s                   (param 14)
    '-rot', '180',              # bit rate, for 1080p30 15Mbits/s                   (param 16)
    '-fps', '30'                # frames per second                                 (param 18)
]

# move video file from Pi SD to USB
# uses cp and rm since mv cannot preserve permitions
def move(old_path, new_path):
    os.system("sudo cp "+OLD_FILE+" "+USB_FOLDER)
    os.system("sudo rm "+OLD_FILE)
    
# Return CPU temperature as a character string  
# uses a pipe to get info from vcgencmd program                                    
def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n",""))

# Return % of CPU used by user as a character string       
# copied from a forum                         
def getCPUuse():
    return(str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip(\
)))

# Creating instance of objects
# classes used for: parsing setup file, GPIO controll and I2C commands
log = LogClass(LOG_FILE)                # Log file object
timer = Timer()                         # Arduino COM object
setup_file = SetupFile(SETUP_FILE)      # Setup file object
io = Gpio_class()                       # GPIO class (switch,led,alive)
io.clear()                              # turn off al LEDs

# Remounting USB in ~/USB directory
# removing unnecessary existing files
os.system("sudo umount /dev/sda1")
os.system("sudo rm "+TEMP_FOLDER+"*")   # Removing temp files
os.system("sudo rm "+USB_FOLDER+"*")    # Removing old usb files
os.system("sudo mount /dev/sda1 "+USB_FOLDER) # mounting USB

# Logging beginning of the program 
# indicate beginning of the code with LED flashing 
log.write("START")
io.blink(10)                     

# get battery voltage from Arduino using I2C
log.write("battery voltage is "+timer.getVoltage()+"v")

# get vidoe recording duration from setupfile
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

# get video width from setupfile
width = setup_file.getParam("width")
if width > 0 and width <= 3280: PARAM[10] = str(width)

# video height from setupfile
height = setup_file.getParam("height")
if height > 0 and height <= 2464: PARAM[12] = str(height)

# frames per second from setupfile
fps = setup_file.getParam("fps")
if fps > 0 and fps <= 90: PARAM[18] = str(fps)

# camera rotation from setupfile
rot = setup_file.getParam("rotation")
if rot > 0 and rot <= 360: PARAM[16] = str(rot)

# MAIN LOOP START
# exit conditions: recording time is finished AND camera section is finished
# -----------------------------------------------
while REC_DUR > 0 or poll == None:

    # Checking if recording section is finished
    # if its not running: 
    # 1. start new section
    # 2. move old setion from ~/Video to ~/USB directory
    if not poll == None:
        io.setRun()                             # indicating video processing

        # monitoring PI CPU temperature
        log.write("CPU temp: "+str(getCPUtemperature()))
        log.write("CPU use: "+str(getCPUuse()))

        # substract interval from recording time since section is finished
        REC_DUR -= VIDEO_SECTION
        log.write("time left: {} min".format(str(REC_DUR)))
        print("time left: {} min".format(str(REC_DUR)))

        # assemble new filename for section and rewriting the parameter
        NEW_FILE = TEMP_FOLDER + datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S') + ".h264"
        PARAM[4] = NEW_FILE             # parameter 4 is filename

        # starting raspivid for new section of time
        camera = subprocess.Popen(PARAM,stdout = subprocess.PIPE,stderr = subprocess.STDOUT)
        log.write("camera pid: "+str(camera.pid))
        print("camera pid: "+str(camera.pid))

        # moving previous file section to USB
        os.system("date")
        log.write("moving file: {} to usb ...".format(OLD_FILE))
        print("moving file: {} to usb ...".format(OLD_FILE))
        move(OLD_FILE, USB_FOLDER)
        log.write("file moved")
        print("file moved")

        # new section becomes previous section for cycle to repeat
        OLD_FILE = NEW_FILE
    # ------

    # Checking for manual termination when switch/button used
    # Kills the current camera process
    TERM = io.checkSwitch()
    if TERM == True:
        log.write("killing current camera process: "+str(camera.pid))
        camera.kill()       # closing current camera program
        break               # exiting the main loop when switch pulled low

    # set REC LED indicator on
    # update the poll - check if camera code is finished
    io.setRec()
    sleep(5)
    poll = camera.poll()

# MAIN LOOP END
# -----------------------------------------------


# moving any remaining video section to USB
# tracking everything in log file
log.write("moving file: "+OLD_FILE+" to usb ...")
move(OLD_FILE, USB_FOLDER)
log.write("file moved")

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

# Blink and turn off LED indicators
io.blink(10)        
io.clear()  

# Track end of day cycle and switch to Half state - sleep      
log.write("CYCLE FINISHED\n")
os.system("sudo shutdown -h now")
sys.exit()