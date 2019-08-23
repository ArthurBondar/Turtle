#!/usr/bin/python2

'''
    August 17, 2019
    Arthur Bondar

    Line Camera Rev. A

    Class to interract with Timing Arduino controller
    using I2C to exchange timming data
    1. Register (2nd parameter in func)
    2. Message lenght
    3. Byte array

    Note: DS3231 must be disabled for I2C bus to read properly

'''

#from smbus import SMBus
import os
from time import sleep
from smbus2 import SMBusWrapper, i2c_msg,  SMBus

class Arduino():

    BYTE_COUNT = 3      # number of bytes returned by Arduino in response to check cmd
    ARDUINO = 0x05      # fixed arduino i2c address
    SLEEP_CMD = 0x01    # command to set up sleep time
    CHECK_CMD = 0xAA    # command to check sleep status and battery voltage
    RTC_ADDR = 0x68     # ds3231 address for getting temperature
    ADC_SCALE = 2       # resistor divider scale on the arduino
    ADC_REF = 3.3       # arduino reference voltage

    # set sleep time for arduino and return result
    def setSleep(self, hour, min):
        ret = False
        with SMBusWrapper(1) as bus:
           bus.write_i2c_block_data(self.ARDUINO, self.SLEEP_CMD, [hour,min])
           sleep(0.5)
           resp = bus.read_i2c_block_data(self.ARDUINO, self.CHECK_CMD, self.BYTE_COUNT)
           if(resp[0] == 1):
               ret = True

        return ret

    # return the sleep status flag from arduino
    def checkStatus(self):
        with SMBusWrapper(1) as bus:
           resp = bus.read_i2c_block_data(self.ARDUINO, self.CHECK_CMD, self.BYTE_COUNT)
           return resp[0]

        return 0

    # getting battery voltage from arduino
    def getVoltage(self):
        ret = "0"
        with SMBusWrapper(1) as bus:
            resp = bus.read_i2c_block_data(self.ARDUINO, self.CHECK_CMD, self.BYTE_COUNT)
            try:
                vol = (resp[2] << 8) | resp[1]
                vol = float(vol)/1024 * self.ADC_REF * self.ADC_SCALE
                ret = str(round(vol, 3))
            except: pass

	    return ret

    # get temperature from DS3231 - return of type string (in C)
    def getTemperature(self):
        ret = "0"
        with SMBusWrapper(1) as bus:
            byte_tmsb = bus.read_byte_data(self.RTC_ADDR, 0x11)
            byte_tlsb = bin(bus.read_byte_data(self.RTC_ADDR, 0x12))[2:].zfill(8)
            Celsius = byte_tmsb + int(byte_tlsb[0])*2**(-1) + int(byte_tlsb[1])*2**(-2)
            ret = str(round(Celsius, 1))
        return ret

# END Timer Class


def print_flags(obj):
    sleep(1)
    flag = obj.checkStatus()
    print("Sleep flag: {}".format(flag))
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

    print("\nSetting sleep for 1 min ...")
    _arduino.setSleep(0, 1)
    print_flags(_arduino)

    print("\nReading temperature ...")
    print _arduino.getTemperature()

    print("\nTest Done")
