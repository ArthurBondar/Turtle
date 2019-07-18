/*





*/


#include "Timer.h"


void Timer::start(uint64_t interval)
{
    this->_interval = interval;
    this->_start = millis();
    this->started = true;
}


bool Timer::check()
{
    
    if( this->started )
    {
        // Overflow protection
        if (this->_start > millis()) this->_start = millis();

        if( millis() - this->_start > this->_interval ) 
            return true;
    }
    else 
        return false;

}