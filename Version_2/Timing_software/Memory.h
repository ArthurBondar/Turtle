/*




*/

#ifndef Memory_h
#define Memory_h

#include "Arduino.h"
#include <EEPROM.h>

#define EEPROM_FULLSIZE_B       1024
#define ENTRY_SIZE_B            8  
#define ENTRY_MAX               ( EEPROM_FULLSIZE_B / sizeof( struct MemCell ) ) - 1 // 113 - 1 = 112
#define LENGH_ADDR              0

struct MemCell {
    uint8_t min;         /* minutes */
    uint8_t hour;        /* hours */
    uint8_t mday;        /* day of the month */
    uint8_t mon;         /* month */
    uint8_t year;        /* year */
    float val;
};

class Memory
{
  public:
    Memory();
    void init();
    void write(uint8_t entry, struct MemCell cell);
    bool read(uint8_t entry, struct MemCell *cell);
    bool push(struct MemCell cell);
    bool pop(struct MemCell* cell);
    void clr_mem();
    uint8_t available_mem();
    uint8_t get_entries();
    void set_entries(uint8_t new_val);

  private:
    
    uint8_t entry = 0;
    
};


#endif
