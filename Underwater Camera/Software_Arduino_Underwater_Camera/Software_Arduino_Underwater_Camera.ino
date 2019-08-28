/*
   August 17, 2019
   Arthur Bondar

   Board: Line Camera Rev. A

   Timing controller program
   Using I2C protocol to interface with Raspberry Pi
   Start a timer to wake Pi up at the end of set_Sleep cycle
   Triggers PIN 4 on Raspberry Pi to reboot from Half/set_Sleep state

   Excepts commands from the Pi:
   0x01 - Starts set_Sleep timer for the Pi

   I2C message format:
   [Operation code][msg lenght][Hour][Minute]

   I2C status return:
   [SleepMode][BattVoltage MSB][BattVoltage LSB]
*/

#include <Wire.h>           // I2C protocol library

// DEBUG //
// comment or uncomment for serial output
//#define DEBUG

// Digital I/O
#define GPS_EN        2       // D2 - GPS Disable when pulled LOW
#define PI_IO1        3       // D3 - shared with RPI 
#define SDA_P         5       // D6 - connected to I2C SDA line         
#define SCL_P         4       // D6 - connected to I2C SCL line - WAKEUP TRIGGER
#define BATTERY       A2      // Battery Monitor pin
#define LED_1         10      // D10 - connected to LED 1
#define LED_2         11      // D11 - connected to LED 2
#define LED_PCB       13      // D13 - breakout board LED

// ADC parameters
#define ADC_REF       3.3     // use 3.3 for 8MHz arduino
#define ADC_SAMP      5       // Average ADC batt readings
#define ADC_SCALE     4.13    // Resistor divider (1.5k and 4.7k) for the ADC values
// Timing Interrupt parameters
#define CLOCK_FREQ    8000000 // use 8M for Arduino with 8MHz clock used
#define PRESCALE      256     // Core Clock divider for the timer
#define INT_FREQ      1       // Freq for generated interrupt in Hz
#define COMP_MATCH    ( CLOCK_FREQ / (PRESCALE * INT_FREQ) ) - 1

// I2C Commands
#define I2C_ADDRESS 0x05
#define SLEEP_CODE  0x01
#define CHECK_CODE  0xAA

// Global Variables
// Used to keep track of time, LED state, I2C messages etc.
volatile uint32_t t_Sleep = 0, Sleep = 1, Sec = 0; // Sleep > t_Sleep
volatile bool Sleep_mode = false;
volatile bool New_msg = false;
volatile bool LED_state = false;
volatile bool Sec_INT = false;
volatile bool Message_flag = false;
volatile uint16_t Voltage = 0;

//
//  INIT // -----------------------------
//
void setup()
{
  //  GPIO setup  //
  pinMode(LED_1, OUTPUT);       // LED 1
  pinMode(LED_2, OUTPUT);       // LED 2
  pinMode(LED_PCB, OUTPUT);     // LED on the module

  pinMode(GPS_EN, INPUT);       // Enable/disable the GPS module 5V Line pup10k!
  pinMode(PI_IO1, INPUT);       // Shared IO with RPI
  pinMode(BATTERY, INPUT);      // Shared IO with RPI

  // Initial setup
  digitalWrite(LED_1, LOW);
  digitalWrite(LED_2, LOW);
  digitalWrite(LED_PCB, LOW);

  // Blink LED on the ProMini to start the program properly
  for (uint8_t i = 0; i < 15; i++, delay(200))
    digitalWrite(LED_PCB, (int) i % 2);

  cli();        //stop all interrupts

  // Set interrupt on Timer1 to run every second
  TCCR1A = 0;                 // set entire TCCR1A register to 0
  TCCR1B = 0;                 // same for TCCR1B
  TCNT1  = 0;                 //initialize counter value to 0
  OCR1A = COMP_MATCH;         // = (8*10^6) / (256*1) - 1 (must be <65536)
  TCCR1B |= (1 << WGM12);     // turn on CTC mode
  TCCR1B |= (1 << CS12);      // Set CS12 bit for 256 prescaler
  TIMSK1 |= (1 << OCIE1A);    // enable timer compare interrupt

  //  I2C setup  //
  Wire.begin(I2C_ADDRESS);      // join i2c bus with address
  Wire.onReceive(receiveEvent); // function pointer to receive event
  Wire.onRequest(sendEvent);    // function pointer for requested I2C register/command

  digitalWrite(A4, LOW);        // Disable Pullup - RPI has pullups
  digitalWrite(A5, LOW);

  // Trigger the Pi on reset
  triggerPi(SCL_P);

#ifdef DEBUG //  DEBUG  //
  Serial.begin(115200);           // start serial for debugging
  Serial.println("START");
#endif

  sei();    //allow interrupts
}

//
//  MAIN LOOP  // ---------------------------
//
void loop()
{
  // When message received from i2c
  // Parse the message and reset the flag
  if (New_msg == true) {
    parseMessage(); // Getting data from I2C register
    New_msg = false;
  }

  // Checking for start of set_Sleep mode //
  // Turning ON/OFF the LED on the board to indicate set_Sleep mode
  if (Sleep_mode) {
    digitalWrite(LED_1, HIGH);
    enableGPS(false);
  } else {
    digitalWrite(LED_1, LOW);
    enableGPS(true);
  }


  // Checking for end of set_Sleep mode //
  // If Minutes timer is bigger than set_Sleep time
  // Reset the flag + timer and trigger Pi to wake up
  if (Sleep_mode && (t_Sleep >= Sleep)) {
    Sleep_mode = false;
    t_Sleep = 0;               // Reset sleep timer !
    triggerPi(SCL_P);
#ifdef DEBUG //  DEBUG  //
    Serial.println("Pi Triggered");
#endif
  }

  // Enter if 1 sec past  //
  // Read battery voltage and save in memory
  if (Sec_INT) {
    Sec_INT = false;
    // flick the LED
    LED_state = (LED_state == true) ? false : true;
    digitalWrite(LED_PCB, LED_state);
    // Battery voltage reading
    uint16_t adc_avg = 0;
    for (int i = 0; i < ADC_SAMP; i++)
      adc_avg += analogRead(BATTERY);
    Voltage = (uint16_t) (adc_avg / ADC_SAMP); // Saving battery Voltage

#ifdef DEBUG //  DEBUG  //
  Serial.println("...");
#endif
  }

  // If seconds timer overflows (every 60 sec)
  // Increment the minutes timer if in sleep mode
  if (Sec >= 60) {
    Sec = 0;                    // seconds overflow
    if (Sleep_mode) t_Sleep ++; // Sleep mode active
    else t_Sleep = 0;
#ifdef DEBUG //  DEBUG  //
    if (Sleep_mode) Serial.println("Sleep: " + String(t_Sleep + 1) + " out of " + String(Sleep));
    Serial.println("ADC: " + String(Voltage) + " Voltage: " + String( ((float)Voltage * ADC_REF * ADC_SCALE) / 1024) );
#endif
  }

#ifdef DEBUG //  DEBUG  //
  if (Message_flag == true) {
    Message_flag = false;
    Serial.println("message sent over I2C");
  }
#endif
} // END LOOP


//
//  Interrupt running every seconds to increment the clock (F=1Hz)
//
ISR(TIMER1_COMPA_vect)
{
  Sec++;   // Increment seconds counter
  Sec_INT = true;
}

//
// Interrrupt function, gets triggered when I2C new data available
//
void receiveEvent( void *arg )
{
  New_msg = true;   // sets a flag for the main program
}

//
//  function that receives I2C data and parses it
//  format: [(byte)Operation code][(byte)hours][(byte)minutes]
//
void parseMessage()
{
  byte hour = 0, min = 0, OPC = 0;

  // Reading Operation Code
  if (Wire.available()) OPC = Wire.read();
  else return;
  // Reading Hours
  if (Wire.available()) hour = Wire.read();
  else return;
  // Reading Minutes
  if (Wire.available()) min = Wire.read();
  else return;

  // Power timer command
  if (OPC == SLEEP_CODE)
  {
    // Converting from: hour(24), minute(60) -> minutes
    Sleep = (((uint32_t)hour) * 60) + (uint32_t)min;
    if (Sleep > 1500) { // Error checking
      Sleep = 0;
      return;
    }
    // Setting up mode parameters
    Sec = 0;
    Sleep_mode = true;  // Enter Sleep mode
#ifdef DEBUG //  DEBUG  //
    Serial.println("sleeping for: " + String(Sleep) + " min");
#endif
  }

}

//
//  Enable / Disable GPS - 5V EN line pulled up 10k
//
void enableGPS (bool enable)
{
  if (enable)
    pinMode(GPS_EN, INPUT);     // input tri state mode GPS enabled
  else
  {
    pinMode(GPS_EN, OUTPUT);
    digitalWrite(GPS_EN, LOW);  // Pulled low - GPS disabled
  }
}


//
//  Grounds pin 5 (SCL) on Raspberry pi to wake it up
//
void triggerPi(int pin)
{
  digitalWrite(pin, LOW);   // setting pin LOW
  pinMode(pin, OUTPUT);     // switching port from High-Z to OUTPUT
  for (uint32_t i = 0; i < 100000; i++); // Delay loop
  pinMode(pin, INPUT);      // enabling Tri-state
}

//
//  Interrrupt function, gets triggered when I2C master requests data
//  Sends pack the mode status: [Sleep0/1][VoltageLSB][VoltageMSB]
//
void sendEvent()
{
  byte resp[] = {0, 0, 0};

  resp[0] = (Sleep_mode == true) ? 0x01 : 0x00;
  resp[1] = (byte) (Voltage & 0x00FF);
  resp[2] = (byte) ((Voltage & 0xFF00) >> 8);
  Wire.write(resp, 3);
  Message_flag = true;
}
