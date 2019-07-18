/*




*/

#include <Wire.h>
#include "ds3231.h"
#include "config.h"
#include "Console.h"
#include "Memory.h"
#include "Timer.h"


volatile bool led_stat = false;
volatile bool pi_stat = false;
volatile bool start_mission = false;
volatile struct ts start = {0}, end = {0}, f_start = {0}, f_end = {0};
volatile char arg1[20] = {0}, arg2[20] = {0};
volatile int param = NO_PARAM, cmd = NO_DATA, prev_cmd = NO_DATA;

Console console(9600, 200);
Memory eeprom;
Timer t_rtc;

void setup()
{
  init_gpio();
  turnPi(false);
  console.init();
  console.print_menu();
  Wire.begin();
  DS3231_init(DS3231_CONTROL_INTCN);
  for (int i = 0; i < 11; i++, delay(150)) digitalWrite(LED_IO, i % 2); // blink 10 times
  eeprom.init();
  //eeprom.set_entries( 0 );
  t_rtc.start(RTC_CHECK_T);

}


void loop()
{
  struct ts t = {0};

  cmd = console.get_cmd(&param, arg1, arg2);
  if(cmd == REPEAT_CMD) respond(prev_cmd, param, arg1, arg2);
  if (cmd == GET_CMD || cmd == SET_CMD) {
    //Serial.println(cmd); Serial.println(cmd); Serial.println(cmd); Serial.println(cmd);
    respond(cmd, param, arg1, arg2);
    prev_cmd = cmd;
  }
  else if (cmd == HELP_CMD) console.print_menu();
  else if (cmd == INVALID) Serial.println("invalid");

  if (t_rtc.check() == true && start_mission == true)
  {
    DS3231_get(&t);
    if ( toSec(&t) < toSec(&start) || toSec(&t) > toSec(&end) ) {
      led_stat = 1;
      digitalWrite(LED_IO, led_stat);
    }

  }



}


void init_gpio()
{
  pinMode(VBATT_IO , INPUT);
  pinMode(PHOTO2_IO , INPUT);
  pinMode(PHOTO1_IO , INPUT);
  pinMode(NTC_IO , INPUT);
  pinMode(PI_PIN_IO , INPUT);
  pinMode(VPI_IO , INPUT);
  pinMode(LED_IO , OUTPUT);
  pinMode(PI_POW_IO , OUTPUT);
}


/*
  SerialEvent occurs whenever a new data comes in the hardware serial RX. This
  routine is run between each time loop() runs, so using delay inside loop can
  delay response. Multiple bytes of data may be available.
*/
void serialEvent()
{
  console.serial_read();
}


void respond(int cmd, int param, char* arg1, char* arg2)
{
  char buff[50];
  struct ts t = {0};
  struct MemCell cell = { 0 };

  // ***************
  if (cmd == GET_CMD) // ----- GET -----
  {
    // get firmware
    if ( param == FIRMWARE_PARAM )
    {
      Console::copy_pgm(buff, FIRMWARE_VERSION, strlen_P(FIRMWARE_VERSION));
      Serial.print(buff);
      Console::copy_pgm(buff, COMPILE_DATE, strlen_P(COMPILE_DATE));
      Serial.println(buff);
    }

    // get started
    else if ( param == STARTED_PARAM )
    {
      sprintf(buff, "%02d/%02d/%04d %02d:%02d:%02d",
              f_start.mday, f_start.mon, f_start.year, f_start.hour, f_start.min, f_start.sec);
      Serial.println(buff);
    }

    // get end_mission
    else if ( param == END_MISSION_PARAM )
    {
      sprintf(buff, "%02d/%02d/%04d %02d:%02d:%02d",
              f_end.mday, f_end.mon, f_end.year, f_end.hour, f_end.min, f_end.sec);
      Serial.println(buff);
    }

    // get start
    else if ( param == START_PARAM )
    {
      sprintf(buff, "%02d:%02d:%02d",
              start.hour, start.min, start.sec);
      Serial.println(buff);
    }

    // get end
    else if ( param == END_PARAM )
    {
      sprintf(buff, "%02d:%02d:%02d",
              end.hour, end.min, end.sec);
      Serial.println(buff);
    }

    // get remaining
    else if ( param == REMAINING_PARAM )
    {
      DS3231_get(&t);
      uint32_t t_sec = toSec(&t);
      if ( t_sec > toSec(&start) && t_sec < toSec(&end) )
        Serial.println( toSec(&end) - t_sec );
      else
        Serial.println( 0 );
    }

    // get mosfet
    else if ( param == MOSFET_PARAM )
    {
      Serial.println(pi_stat);
    }

    // get time
    else if ( param == TIME_PARAM )
    {
      DS3231_get(&t);
      sprintf(buff, "%02d/%02d/%04d %02d:%02d:%02d",
              t.mday, t.mon, t.year, t.hour, t.min, t.sec);
      Serial.println(buff);
    }

    // get led
    else if ( param == LED_PARAM )
    {
      Serial.println(led_stat);
    }

    // get temperature
    else if ( param == TEMP_PARAM )
    {
      Serial.println(DS3231_get_treg());
    }

    // get batt_voltage
    else if ( param == BATT_V_PARAM )
    {
      float sum = 0;
      for (int i = 0; i < ADC_AVG; i++)
        sum += ( analogRead(VBATT_IO) * ADC_RES ) ;
      Serial.println( sum / ADC_AVG );
    }

    // get mem_all
    else if ( param == MEM_ALL_PARAM )
    {
      for ( int b = eeprom.pop(&cell), i = eeprom.get_entries(); b > 0; b = eeprom.pop(&cell), i++ )
      {
        sprintf(buff, "[%d] %02d/%02d/%04d %02d:%02d %.3f",
                i, cell.mday, cell.mon, (int) cell.year + 2000, cell.hour, cell.min, cell.val);
        Serial.println(buff);
      }

    }

    // get start_mission
    else if ( param == START_MISSION )
    {
      Serial.println(start_mission);

    }

  }

  // ***************
  else if (cmd == SET_CMD) // ----- SET -----
  {
    // set start HHMMSS
    if ( param == START_PARAM )
    {
      start.hour = (arg1[0] - '0') * 10 + (arg1[1] - '0');
      start.min = (arg1[2] - '0') * 10 + (arg1[3] - '0');
      start.sec = (arg1[4] - '0') * 10 + (arg1[5] - '0');
    }

    // set end HHMMSS
    else if ( param == END_PARAM )
    {
      end.hour = (arg1[0] - '0') * 10 + (arg1[1] - '0');
      end.min = (arg1[2] - '0') * 10 + (arg1[3] - '0');
      end.sec = (arg1[4] - '0') * 10 + (arg1[5] - '0');
    }

    // set led [0/1]
    else if ( param == LED_PARAM )
    {
      led_stat = (arg1[0] == '1') ? true : false;
      digitalWrite(LED_IO, led_stat);
    }

    // set mosfet [0/1]
    else if ( param == MOSFET_PARAM )
    {
      pi_stat = (arg1[0] == '1') ? true : false;
      turnPi(pi_stat);
    }

    // set time DDMMYYYY HHMMSS
    else if ( param == TIME_PARAM )
    {
      t.mday = (arg1[0] - '0') * 10 + (arg1[1] - '0');
      t.mon = (arg1[2] - '0') * 10 + (arg1[3] - '0');
      t.year = (arg1[4] - '0') * 1000 + (arg1[5] - '0') * 100 + (arg1[6] - '0') * 10 + (arg1[7] - '0');
      t.hour = (arg2[0] - '0') * 10 + (arg2[1] - '0');
      t.min = (arg2[2] - '0') * 10 + (arg2[3] - '0');
      t.sec = (arg2[4] - '0') * 10 + (arg2[5] - '0');
      DS3231_set(t);
    }

    // set clearmem
    else if ( param == CLR_MEM_PARAM )
    {
      eeprom.clr_mem();
    }

    // set start_mission
    else if ( param == START_MISSION )
    {
      start_mission = (arg1[0] == '1') ? true : false;
      if ( start_mission ) DS3231_get(&f_start); // record operation start time
    }
    else
    {
      Serial.println("invalid");
    }

    Serial.println("done");
  }
}


uint32_t toSec( volatile struct ts* t)
{
  uint32_t total_min = 0;
  total_min += ( (uint32_t)t->hour * 60 * 60 );
  total_min += ( (uint32_t)t->min * 60 );
  total_min += ( (uint32_t)t->sec );
  return total_min;
}


void turnPi (bool on)
{
  if ( on ) digitalWrite(PI_POW_IO, 0);
  else      digitalWrite(PI_POW_IO, 1);
}
