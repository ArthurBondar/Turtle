
/*
  DS3231 library for the Arduino.
  Author:          Petre Rodan <petre.rodan@simplex.ro>
  Available from:  https://github.com/rodan/ds3231
 
  The DS3231 is a low-cost, extremely accurate I2C real-time clock 
  (RTC) with an integrated temperature-compensated crystal oscillator 
  (TCXO) and crystal.

  GNU GPLv3 license:
  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
   
*/

#include <Wire.h>
#include <stdio.h>
#include "ds3231.h"

//
void DS3231_init(const uint8_t ctrl_reg)
{
    DS3231_set_creg(ctrl_reg);
    DS3231_set_32kHz_output(false);
}


//
void DS3231_set(struct ts t)
{
    uint8_t i, century;

    if (t.year >= 2000) {
        century = 0x80;
        t.year_s = t.year - 2000;
    } else {
        century = 0;
        t.year_s = t.year - 1900;
    }

    uint8_t TimeDate[7] = { t.sec, t.min, t.hour, t.wday, t.mday, t.mon, t.year_s };

    Wire.beginTransmission(DS3231_I2C_ADDR);
    Wire.write(DS3231_TIME_CAL_ADDR);
    for (i = 0; i <= 6; i++) {
        TimeDate[i] = dectobcd(TimeDate[i]);
        if (i == 5)
            TimeDate[5] += century;
        Wire.write(TimeDate[i]);
    }
    Wire.endTransmission();
}


//
void DS3231_get(struct ts *t)
{
    uint8_t TimeDate[7];            //second,minute,hour,dow,day,month,year
    uint8_t century = 0, i, n;
    uint16_t year_full;

    Wire.beginTransmission(DS3231_I2C_ADDR);
    Wire.write(DS3231_TIME_CAL_ADDR);
    Wire.endTransmission();
    delay(2);

    Wire.requestFrom(DS3231_I2C_ADDR, 7);
    
    for (i = 0; i <= 6; i++) {
        n = Wire.read();
        if (i == 5) {
            TimeDate[5] = bcdtodec(n & 0x1F);
            century = (n & 0x80) >> 7;
        } else
            TimeDate[i] = bcdtodec(n);
    }

    if (century == 1) year_full = 2000 + TimeDate[6];
    else year_full = 1900 + TimeDate[6];

    t->sec = TimeDate[0];
    t->min = TimeDate[1];
    t->hour = TimeDate[2];
    t->mday = TimeDate[4];
    t->mon = TimeDate[5];
    t->year = year_full;
    t->wday = TimeDate[3];
    t->year_s = TimeDate[6];
}


//
void DS3231_set_addr(const uint8_t addr, const uint8_t val)
{
    Wire.beginTransmission(DS3231_I2C_ADDR);
    Wire.write(addr);
    Wire.write(val);
    Wire.endTransmission();
}


//
uint8_t DS3231_get_addr(const uint8_t addr)
{
    Wire.beginTransmission(DS3231_I2C_ADDR);
    Wire.write(addr);
    Wire.endTransmission();
    delay(2);

    Wire.requestFrom(DS3231_I2C_ADDR, 1);

    return (uint8_t) Wire.read();
}


// control register
void DS3231_set_creg(const uint8_t val)
{
    DS3231_set_addr(DS3231_CONTROL_ADDR, val);
}


//
uint8_t DS3231_get_creg(void)
{
    return (uint8_t) DS3231_get_addr(DS3231_CONTROL_ADDR);
}


// status register 0Fh/8Fh
//
void DS3231_set_sreg(const uint8_t val)
{
    DS3231_set_addr(DS3231_STATUS_ADDR, val);
}


//
uint8_t DS3231_get_sreg(void)
{
    uint8_t rv;
    rv = DS3231_get_addr(DS3231_STATUS_ADDR);
    return rv;
}

// temperature register
float DS3231_get_treg()
{
    uint8_t temp_msb, temp_lsb;
    int8_t nint;

    Wire.beginTransmission(DS3231_I2C_ADDR);
    Wire.write(DS3231_TEMPERATURE_ADDR);
    Wire.endTransmission();
    delay(2);

    Wire.requestFrom(DS3231_I2C_ADDR, 2);

    temp_msb = Wire.read();
    temp_lsb = Wire.read() >> 6;

    if ((temp_msb & 0x80) != 0)
        nint = temp_msb | ~((1 << 8) - 1);      // if negative get two's complement
    else
        nint = temp_msb;

    return (float) (0.25 * temp_lsb + nint);
}


//
void DS3231_set_32kHz_output(const uint8_t on)
{
    /*
     * Note, the pin1 is an open drain pin, therfore a pullup
     * resitor is required to use the output.
     */
    if (on) {
        uint8_t sreg = DS3231_get_sreg();
        sreg &= ~DS3231_STATUS_OSF;
        sreg |= DS3231_STATUS_EN32KHZ;
        DS3231_set_sreg(sreg);
    } else {
        uint8_t sreg = DS3231_get_sreg();
        sreg &= ~DS3231_STATUS_EN32KHZ;
        DS3231_set_sreg(sreg);
    }
}

// helpers
uint8_t dectobcd(const uint8_t val)
{
    return ((val / 10 * 16) + (val % 10));
}

uint8_t bcdtodec(const uint8_t val)
{
    return ((val / 16 * 10) + (val % 16));
}

uint8_t inp2toi(char *cmd, const uint16_t seek)
{
    return (uint8_t) ((cmd[seek] - 48) * 10 + cmd[seek + 1] - 48);
}