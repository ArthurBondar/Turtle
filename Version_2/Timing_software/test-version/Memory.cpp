/*







*/



#include "Memory.h"


Memory::Memory()
{

}


void Memory::init()
{
    this->entry = EEPROM.read( LENGH_ADDR );
}


uint8_t Memory::get_entries()
{
    return this->entry;
}


void Memory::set_entries(uint8_t new_val)
{
    this->entry = new_val;
    EEPROM.write( LENGH_ADDR, new_val);
}


void Memory::clr_mem()
{
    this->entry = 0;
    this->set_entries(this->entry);

}

void Memory::write(uint8_t entry, struct MemCell cell)
{
    if( entry >= ENTRY_MAX || entry < 1 )
        return;
    EEPROM.put( entry * sizeof(struct MemCell), cell);
}


bool Memory::read(uint8_t entry, struct MemCell *cell)
{
    if( entry >= ENTRY_MAX || entry < 1)
        return false;
    EEPROM.get(this->entry * sizeof(struct MemCell), cell);
}

// True - success , False - failed
bool Memory::push(struct MemCell cell)
{
    if( this->entry >= ENTRY_MAX )
        return false;

    this->entry++;
    EEPROM.put( this->entry * sizeof(struct MemCell), cell);
    this->set_entries(this->entry);
    return true;
}

// True - success , False - failed
bool Memory::pop(struct MemCell* cell)
{
    if( this->entry >= ENTRY_MAX || this->entry < 1)
        return false;

    this->entry--;
    EEPROM.get( this->entry * sizeof(struct MemCell), cell);
    this->set_entries(this->entry);
    return true;
}

uint8_t Memory::available_mem()
{
    return ( (uint8_t) (ENTRY_MAX) - this->entry);
}
