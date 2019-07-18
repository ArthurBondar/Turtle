## Underwater POV Camera System - v3.2
### Changes:
* File moving and video recording have been separated to ease the load on Pi SD card. New section is not started until video file is moved.
* Default camera mods added in the setup file. To avoid confusion with fps and resolution settings, a preset video modes are taken from Raspberry Pi Camera documentation.
* Start up scrip (rc.local) checks for DEBUG semaphore to abort beginning of the program. 
* Video indication using red LED. The LED on the PCB flashes to indicate continues recording without stalling.
* GPS sample interval is added.
* CPU parameter logging added. Parameters are saved in the log file, including CPU throttling flag.
* Class test code added. Each class module can run independently and perform a self test.
### Future updated:
* Buffer GPS data CSV file in memory instead of continues writing to USB card.
* Add commands to clean the RAM.
* Add feature to read battery voltage.

* Change timezone to Atlantic/Hamilton Bermuda
