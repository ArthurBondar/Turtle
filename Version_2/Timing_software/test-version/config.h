/*




*/

#include <avr/pgmspace.h>

#define SERIAL_NUM      "01"

#define VBATT_IO        A0
#define PHOTO2_IO       A1
#define PHOTO1_IO       A2
#define NTC_IO          A3
#define PI_POW_IO       2
#define PI_PIN_IO       3
#define LED_IO          6    // actual 6
#define VPI_IO          8

#define ADC_RES         5.3 / 1023.0
#define ADC_AVG         10
#define RTC_CHECK_T     2 * 1000
#define LED_ON          200
#define LED_OFF         2 * 1000

const char COMPILE_DATE[] PROGMEM = " "__DATE__ " " __TIME__;
const char FIRMWARE_VERSION[] PROGMEM = "version 3.3 SN#"SERIAL_NUM; 
