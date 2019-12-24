// Ian Moore & Nick Washuta
// EE101 Final Project
// Code sourced from EE 101 Labs
// Autonomous & Remote Controlled Robot

// We had to separate each function into its own void loop as the board (YourDuinoRoboRED Arduino-UNO) was 
//    unable to execute all functions at once. (hence why some are commented out and there are multiple void loops)

#include <Wire.h>             // imports Wire library - Do we use this?
#include "BLESerial.h"        // importing BLESerial library
#include <SoftwareSerial.h>   // includes SoftwareSerial library enables connection through 
                              // the serial monitor even when other commands are running
#include <NewPing.h>          // include NewPing Library
# include <EEPROM.h>
SoftwareSerial ble(8, 9);     // setting pin 8 & 9 as bluetooth communication pins
                              // using ble object
#include <OneWire.h>            // library for temp sensor
#include <DallasTemperature.h>  // other library for temp sensor

#define ONE_WIRE_BUS 14                   // data pin is plugged into pin 14 on the Arduino
OneWire oneWire(ONE_WIRE_BUS);            // Setup a oneWire instance to communicate with any OneWire devices (not just Maxim/Dallas temperature ICs)
DallasTemperature thermistor(&oneWire);   // Pass our oneWire reference to Dallas Temperature                           //
float temp;                               // creates temp float


const int trigPin = 6;        // sets pin for trigger of ultrasonics sensor
const int echoPin = 7;        // sets pin for echo of ultrasonic sensor
long duration;                // creates duration variable to store ultrasonics ranging times
int distance = 0;             // integer for sonar distance
float distanceInch;           // creates a float for converting durations to distances in inches
#define maximumDistance 200   // creates a maximum_distance variable
NewPing sonar(trigPin, echoPin, maximumDistance);    //sensor function

int latch = 10;          // IC pin 12 on SN for LED strip
int data = 11;           // IC pin 14 on SN for LED strip
int clockpin = 12;       // IC pin 11 on SN for LED strip
byte pattern[]=          // pattern for LED Strip (tried something different)
{B10101010,   
 B01010101};
byte patternOff[]=       // pattern for turning the LEDs on and off
{B00000000};
int index = 0;                // indexer for byte patterns
int count = sizeof(pattern);  // sets count to length of byte pattern for indexer

const int buttonPin = 13;     // sets the pushbutton pin
int buttonState = 0;          // creates buttonState int that will store button position
int lastButtonState = 0;      // creates lastButtonState int that will store last button position
int buttonPushCounter = 0;    // creates a counter int to store number of button presses

const int buttonPin2 = 14;    // sets the pushbutton pin for buzzer // used to be 14
int buttonState2 = 0;         // creates buttonState int that will store button position
int lastButtonState2 = 0;     // creates lastButtonState int that will store last button position
int buttonPushCounter2 = 0;   // creates a counter int to store number of button presses
const int buzzerPin = 15;     // sets buzzer pin // used to be 15

#define maximum_distance 200       // max distance
boolean goesForward = false;       // boolean for driving 
char getstr;                       // defines char for receiving 
const int LeftMotorForward   = 5;  // sets left motor forward pin
const int LeftMotorBackward  = 4;  // sets left motor backward pin
const int RightMotorBackward = 3;  // sets right motor backward pin
const int RightMotorForward  = 2;  // sets right motor forward pin



void setup(){
  Serial.begin(9600);    // begins Serial communication
  ble.begin(9600);       // initializing the bluetooth connection
  thermistor.begin();    // begins thermistor input
  
  pinMode(RightMotorForward, OUTPUT);  // sets each motor pin as an output
  pinMode(LeftMotorForward, OUTPUT);
  pinMode(LeftMotorBackward, OUTPUT);
  pinMode(RightMotorBackward, OUTPUT);
  
  pinMode(buttonPin, INPUT);       // sets button as an input
  pinMode(clockpin,OUTPUT);        // sets clockpin as an output
  pinMode(latch,OUTPUT);           // sets latch pin as an output
  pinMode(data,OUTPUT);            // sets data pin as an output 
  
  pinMode(trigPin, OUTPUT);        // sets sonar trigger pin as an output
  pinMode(echoPin, INPUT);         // sets sonar echo pin as an input
  distance = ultRange();           // read distance
  delay(100);                      // delays

  Serial.print("Last Temperature: "); // prints last temperature
  Serial.print(EEPROM.read(temp));    // read last temp value from EEPROM
  
  }

void mForward(){  
  digitalWrite(LeftMotorForward, HIGH);
  digitalWrite(RightMotorForward, HIGH);
  digitalWrite(LeftMotorBackward, LOW);
  digitalWrite(RightMotorBackward, LOW);
}

void mBack(){ 
  digitalWrite(LeftMotorForward, LOW);
  digitalWrite(RightMotorForward, LOW);
  digitalWrite(LeftMotorBackward, HIGH);
  digitalWrite(RightMotorBackward, HIGH);
}

void mLeft(){
  digitalWrite(LeftMotorBackward, LOW); 
  digitalWrite(RightMotorForward, HIGH);
  digitalWrite(LeftMotorForward, LOW);
  digitalWrite(RightMotorBackward, LOW);
}

void mRight(){
  digitalWrite(LeftMotorForward, HIGH);
  digitalWrite(RightMotorBackward, LOW); 
  digitalWrite(LeftMotorBackward, LOW);
  digitalWrite(RightMotorForward, LOW);
}

void mStop(){
  digitalWrite(RightMotorForward, LOW);
  digitalWrite(LeftMotorForward, LOW);
  digitalWrite(RightMotorBackward, LOW);
  digitalWrite(LeftMotorBackward, LOW);
}



// Ultrasonic Ranging Sensor section
float ultRange() {                      // If doesn't work, comment out float distanceInch and uncomment everything else 
//  digitalWrite(trigPin, LOW);
//  delayMicroseconds(2);
//  digitalWrite(trigPin, HIGH);
//  delayMicroseconds(10);            // we may be able to bump this up to get more acc readouts
//  digitalWrite(trigPin, LOW);
//  duration = pulseIn(echoPin, HIGH);
  float distanceInch = sonar.ping_in();
//  distanceInch = duration*0.0135/2;
  ble.print("Distance: ");
  ble.print(distanceInch);// Prints the distance value from the sensor
  ble.print(" inches");
  ble.println();
  delay(50);
  return distanceInch;
}

float getTemp(){
  thermistor.requestTemperatures();                 // Send the command to get temperatures
  float temp = thermistor.getTempCByIndex(0);       // stores temp in temp variable
  ble.print("Temperature is: ");                    // prints statements 
  ble.println(temp);                                // prints temperature readout
  delay(250);
  EEPROM.write(0, thermistor.getTempCByIndex(0)); 
  }

void LEDStripON() {
    digitalWrite(latch,LOW);                                    // sets latch pin to low
    shiftOut(data,clockpin,MSBFIRST,pattern[index]);            // shift function shifts out a byte of data one bit at a time
    digitalWrite(latch,HIGH);                                   // sets latch pin to high
    delay(50);                                                  // sets delay to Hz
    index++;                                                    // counter
    if(index>=count) {                                          // checks if were at the end of the byte pattern
      index=0;}                                                 // if so, sets index back to 0
}
  
void LEDStripOFF() {
    digitalWrite(latch,LOW);                                    // sets latch pin to low
    shiftOut(data,clockpin,MSBFIRST,patternOff[index]);            // shift function shifts out a byte of data one bit at a time
    digitalWrite(latch,HIGH);                                   // sets latch pin to high
    delay(50);                                                  // sets delay to Hz
    index++;                                                    // counter
    if(index>=count) {                                          // checks if were at the end of the byte pattern
      index=0;}                                                 // if so, sets index back to 0
}

void checkButton() {
  buttonState = digitalRead(buttonPin);   // sets buttonState to readout of buttonPin
  if (buttonState != lastButtonState) {   // compares buttonState and lastButtonState
    if (buttonState == HIGH) {            // if buttonState is high
      buttonPushCounter++;}               // add one to counter
    else {}                               // otherwise delay
      delay(50);}                         // delay
   lastButtonState = buttonState;         // sets LastButtonState to buttonState
   if (buttonPushCounter % 2 == 0) {      // checks if there is remainder when dividing by two
                                          // this will turn the LED strip on or off with every
                                          // press
    LEDStripON();}                        // if there is turn the LED strip on
   else {                                 // otherwise:
    LEDStripOFF();{                       // turn the LED strip off
      }
   }
}



void checkButton2() {         // For buzzer
  buttonState2 = digitalRead(buttonPin2);   // sets buttonState to readout of buttonPin
  if (buttonState2 != lastButtonState2) {   // compares buttonState and lastButtonState
    if (buttonState2 == HIGH) {             // if buttonState is high
      buttonPushCounter2++;}                // add one to counter
  
    else {}                                 // otherwise delay
      delay(50);}                           // delay
      lastButtonState2 = buttonState2;         // sets LastButtonState to buttonState
   if (buttonPushCounter2 % 2 == 0) {       // checks if there is remainder when dividing by two
                                            // this will turn the buzzer on or off with every
                                            //  press
      for(int i=0;i<80;i++){                // will play buzzer at a frequency for a short time   
      digitalWrite(buzzerPin,HIGH);         // turn buzzer on
      delay(1);                             // delay
      digitalWrite(buzzerPin,LOW);          // turn buzzer off
      delay(1);}                            // delay
    }       
   else {                                   // otherwise:
      digitalWrite(buzzerPin, LOW);}
}





//void loop(){      // LED loop. Commented 
//  checkButton();
//}

//void loop(){      // Buzzer loop
//  checkButton2();
//}

//void loop(){      // Temperature loop
//  getTemp();
//}

void loop(){                
  if (distance <= 20){
    mStop();
    delay(300);
    mBack();
    delay(400);
    mStop();
    delay(300);
  }
   else{ 
  getstr=ble.read();
 if(getstr=='A'){       // Forward
    mForward();
//    while (getstr=='A'){
//      mForward();
//      ble.available();
//      if (getstr=='G'){
//        mStop();
//        delay(500);
//      }
//    }
  }
  else if(getstr=='C'){ // Back 
    mBack();
    delay(1000);
    mStop();
  }
  else if(getstr=='B'){ // Left
    mLeft();
    delay(500);
    mStop();
  }
  else if(getstr=='D'){ // Right
    mRight();
    delay(500);
    mStop();
  }
  else if(getstr=='G'){ // Stop
    mStop();   
    delay(500);  
  }
   }
   distance = readPing();
}
int readPing(){
  //delay(70);
  int cm = sonar.ping_cm();
  if (cm==0){
    cm=250;
  }
  return cm;
}
