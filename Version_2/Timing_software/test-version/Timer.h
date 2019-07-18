/*




*/

#ifndef Timer_h
#define Timer_h

#include "Arduino.h"


class Timer
{
  public:
    void start(uint64_t interval);
    bool check();

  private:
    bool started = false;
    uint64_t _start = 0;
    uint64_t _interval = 0;
    
};


#endif