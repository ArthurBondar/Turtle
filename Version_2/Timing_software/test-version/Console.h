/*




*/

#ifndef Console_h
#define Console_h

#include "Arduino.h"
#include <avr/pgmspace.h>

#define SERIAL_BUFF 200

#define GET_CMD     0
#define SET_CMD     1
#define HELP_CMD    2
#define NO_DATA     3
#define INVALID     4
#define REPEAT_CMD  5

#define FIRMWARE_PARAM      0
#define STARTED_PARAM       1
#define END_MISSION_PARAM   2
#define START_PARAM         3
#define END_PARAM           4
#define REMAINING_PARAM     5
#define MOSFET_PARAM        6
#define TIME_PARAM          7
#define LED_PARAM           8
#define TEMP_PARAM          9
#define BATT_V_PARAM        10
#define MEM_PARAM           11
#define MEM_ALL_PARAM       12
#define CLR_MEM_PARAM       13
#define START_MISSION       14
#define NO_PARAM            99

class Console
{
  public:
    Console(int baud = 9600, int buff_size = 200);
    ~Console();
    void init();
    void print_menu();
    void serial_read();
    int get_cmd(int *param, char* arg1, char* arg2);
    static void copy_pgm (char* to, const char* from, size_t lenght);

  private:
    int buff_size = SERIAL_BUFF;
    int baud = 9600;
    String* input_buffer;
    int current_cmd = 12;
    bool new_cmd = false;
};


#endif
