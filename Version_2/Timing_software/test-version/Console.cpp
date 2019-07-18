/*




*/

#include "Console.h"


static const char _get_cmd[] PROGMEM = "get";
static const char _set_cmd[] PROGMEM = "set";
static const char _help_cmd[] PROGMEM = "help";

#define PARAM_LEN     14
static const char parameter[][PARAM_LEN] PROGMEM = {
  "firmware",             // GET
  "started",              // GET
  "end_mission",          // GET
  "start",                // GET/SET hh:mm
  "end",                  // GET/SET hh:mm
  "remaining",            // GET
  "mosfet",               // GET/SET 0/1
  "time",                 // GET/SET DDMMYYYY hhmmss
  "led",                  // GET/SET
  "temperature",          // GET
  "batt_voltage",         // GET
  "mem",                  // GET/SET [index]
  "mem_all",              // GET
  "clearmem",             // SET
  "start_mission"         // SET
};
#define PARAM_NUM       15


Console::Console(int baud, int buff_size)
{
  this->baud = baud;
  this->buff_size = buff_size;
  this->input_buffer = new String();
}


Console::~Console()
{
  delete this->input_buffer;
  this->input_buffer = NULL;
}


void Console::init()
{
  this->input_buffer->reserve(this->buff_size);       // dynamically allocate 200 characters
  *(this->input_buffer) = "";
  Serial.begin(this->baud);                           // start serial peripheral
}


/*
    Print all avaiable console parameters
*/
void Console::print_menu()
{
  char ch;

  Serial.println("\nuse get/set or help");
  for (int i = 0; i < PARAM_NUM; i++)
  {
    for (int c = 0; c < strlen_P(parameter[i]); c++)
    {
      ch = pgm_read_byte_near(parameter[i] + c);
      Serial.print(ch);
    }
    Serial.println();
  }
}


void Console::serial_read ()
{
  while (Serial.available())
  {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    if (inChar == '\n') {
      this->new_cmd = true;
      *(this->input_buffer) += '\0';
    }
    else
      *(this->input_buffer) += inChar;
  }
}


void Console::copy_pgm (char* to, const char* from, size_t lenght)
{
  int i = 0;
  for ( ; i < lenght; i++ )
    to[i] = pgm_read_byte_near(from + i);

  to[i] = '\0';
}


/*

    Format: [GET/SET/HELP] [param] [arg1] [arg2?]
*/
int Console::get_cmd(int *param, char* arg1, char* arg2)
{
  char buff[PARAM_LEN], *p;
  int cmd = NO_DATA, i = 0;

  if (this->new_cmd)
  {
    this->new_cmd = false;
    
    // Check for REPEAT command
    if ( this->input_buffer->c_str() [0] == '\0' ) {
      *(this->input_buffer) = "";
      return REPEAT_CMD;
    }

    // Check for HELP command
    Console::copy_pgm(buff, _help_cmd, strlen_P(_help_cmd));
    if (strcmp( this->input_buffer->c_str(), buff ) == 0)
    {
      *(this->input_buffer) = "";
      return HELP_CMD;
    }

    // Check command SET or GET
    p = strtok(this->input_buffer->c_str(), " ");
    Console::copy_pgm(buff, _get_cmd, strlen_P(_get_cmd));
    if (strcmp( p, buff ) == 0) cmd = GET_CMD;
    Console::copy_pgm(buff, _set_cmd, strlen_P(_set_cmd));
    if (strcmp( p, buff ) == 0) cmd = SET_CMD;

    // Check if parameter present
    p = strtok( NULL, " ");
    if ( p == NULL ) {
      *(this->input_buffer) = "";
      return INVALID;
    }

    // Find the parameter
    for (i = 0, *param = NO_PARAM; i < PARAM_NUM; i++)
    {
      Console::copy_pgm(buff, parameter[i], strlen_P(parameter[i]));
      if ( strcmp( p, buff ) == 0) {
        *param = i;
        break;
      }
    }
    if ( *param == NO_PARAM ) {
      *(this->input_buffer) = "";
      return INVALID;
    }

    // Get arguments from SET command
    if ( cmd == SET_CMD )
    {
      // Extract Arguments
      p = strtok( NULL, " ");
      if ( p == NULL ) {
        *(this->input_buffer) = "";
        return INVALID;
      }
      strcpy(arg1, p);
      // Arg2
      p = strtok( NULL, " ");
      if ( p != NULL )
        strcpy(arg2, p);
    }

    *(this->input_buffer) = "";
  }

  return cmd;
}
