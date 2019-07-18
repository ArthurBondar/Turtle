#!/usr/bin/python2

'''
    Changed: October 7, 2018

    Class to interract with Timing Arduino controller
    using I2C to exchange timming data
    1. Register (2nd parameter in func)
    2. Message lenght
    3. Byte array

'''

#from smbus import SMBus
import os
from time import sleep
from smbus2 import SMBusWrapper, i2c_msg,  SMBus

class Arduino():
    # Definitions
    ARDUINO = 0x05
    SLEEP_CMD = 0x01
    RELEASE_CMD = 0x02
    CHECK_CMD = 0xAA
    RTC_ADDR = 0x68
    ADC_SCALE = 1.5
    ADC_REF = 3.28

    # set sleep time for arduino and return result
    def setSleep(self, hour, min):
        os.system('sudo rmmod rtc_ds1307')
        ret = False
        with SMBusWrapper(1) as bus:
           bus.write_i2c_block_data(self.ARDUINO, self.SLEEP_CMD, [hour,min])
           sleep(0.5)
           resp = bus.read_i2c_block_data(self.ARDUINO, self.CHECK_CMD, 4)
           if(resp[0] == 1):
               ret = True

	sleep(0.5)
        os.system('sudo modprobe rtc_ds1307')
        return ret

    # set release time for arduino and return result
    def setRelease(self, hour, min):
        os.system('sudo rmmod rtc_ds1307')
        ret = False
        with SMBusWrapper(1) as bus:
           bus.write_i2c_block_data(self.ARDUINO, self.RELEASE_CMD, [hour,min])
           sleep(0.5)
           resp = bus.read_i2c_block_data(self.ARDUINO, self.CHECK_CMD, 4)
           if(resp[1] == 1):
               ret = True

	sleep(0.5)
        os.system('sudo modprobe rtc_ds1307')
        return ret

    # return array of two status flags from arduino [sleep, release]
    def checkStatus(self):
        os.system('sudo rmmod rtc_ds1307')
        ret = [0, 0]
        with SMBusWrapper(1) as bus:
           ret = bus.read_i2c_block_data(self.ARDUINO, self.CHECK_CMD, 4)

	sleep(0.5)
        os.system('sudo modprobe rtc_ds1307')
        return ret

    # getting battery voltage from arduino
    def getVoltage(self):
        os.system('sudo rmmod rtc_ds1307')
        ret = "0"
        with SMBusWrapper(1) as bus:
            resp = bus.read_i2c_block_data(self.ARDUINO, self.CHECK_CMD, 4)
            try:
                vol = (resp[3] << 8) | resp[2]
                vol = float(vol)/1024 * self.ADC_REF * self.ADC_SCALE
                ret = str(round(vol, 3))
            except: pass

	sleep(0.5)
        os.system('sudo modprobe rtc_ds1307')
	return ret

    def getTemperature(self):
        os.system('sudo rmmod rtc_ds1307')
	ret = "0"
        with SMBusWrapper(1) as bus:
            byte_tmsb = bus.read_byte_data(self.RTC_ADDR, 0x11)
            byte_tlsb = bin(bus.read_byte_data(self.RTC_ADDR, 0x12))[2:].zfill(8)
            Celsius = byte_tmsb + int(byte_tlsb[0])*2**(-1) + int(byte_tlsb[1])*2**(-2)
            ret = str(round(Celsius, 1))

	sleep(0.5)
        os.system('sudo modprobe rtc_ds1307')
	return ret


# END Timer Class


def print_flags(obj):
    sleep(1)
    flag = []*2
    flag = obj.checkStatus()
    print("Sleep flag: {}".format(flag[0]))
    print("Release flag: {}".format(flag[1]))
    sleep(1)

# When class module is started by itself
# Following code is used for testing the Class
if __name__ == "__main__":

    # Arduino COM object
    print("--- Starting Arduino COM test ---\n")
    print("use ($sudo i2cdetect -y 1) to check connection\n")
    _arduino = Arduino()

    print("Voltage reading from Arduino: {}".format(_arduino.getVoltage()))
    print_flags(_arduino)

    print("\nSetting release for 1 min ...")
    _arduino.setRelease(0, 1)
    print_flags(_arduino)

    print("\nSetting sleep for 1 min ...")
    _arduino.setSleep(0, 1)
    print_flags(_arduino)

    print("\nReading temperature ...")
    print _arduino.getTemperature()

    print("\nTest Done")
