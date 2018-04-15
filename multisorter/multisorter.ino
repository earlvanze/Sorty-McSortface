/*
 Stepper Motor Control - one revolution

 This program drives a unipolar or bipolar stepper motor.
 The motor is attached to digital pins 8 - 11 of the Arduino.

 The motor should revolve one revolution in one direction, then
 one revolution in the other direction. 


 Created 11 Mar. 2007
 Modified 30 Nov. 2009
 by Tom Igoe

*/

#include <Servo.h>
#include <Stepper.h>

const int stepsPerRevolution = 200;  // change this to fit the number of steps per revolution
// for your motor

// initialize the stepper library on pins 8 through 11:
Stepper myStepper(stepsPerRevolution, 8, 9, 10, 11);

int item; // variable to store bin selection
int servoPin = 12; //declare pin for the servo
int servoDelay = 800; //delay to allow the servo to reach position;
int val = 0;
int sensorPin = 2;
int ledPin = 13;
int pirState = LOW;

// defines pins numbers
const int trigPin = 5;
const int echoPin = 6;

// defines variables
long duration;
int distance;
int numRevolutions = 5;
bool doorOpened = 0;

Servo myServo; // create a servo object called myServo

void setup() {
  Serial.begin(9600); //start serial port
  myServo.attach(servoPin); //declare to which pin is the servo connected
  pinMode(ledPin, OUTPUT);      // declare LED as output
  pinMode(sensorPin, INPUT);     // declare sensor as input
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT); // Sets the echoPin as an Input
  myStepper.setSpeed(60);  // set the stepper speed at 60 rpm
}

int checkDistance() {
  // Clears the trigPin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);
  // Calculating the distance
  distance= duration*0.034/2;
  // Prints the distance on the Serial Monitor
  Serial.print("Distance (cm): ");
  Serial.println(distance);
  return distance;
}

void openDoor() {
    myStepper.step(stepsPerRevolution * numRevolutions);
    doorOpened = 1;
}

void closeDoor() {
    myStepper.step(-stepsPerRevolution * numRevolutions);
    doorOpened = 0;
}

void loop(){
  item = 0;
  Serial.println("No motion");
  if (myServo.read() != 90) {
    myServo.write(90);
    delay(servoDelay);
  }
  if (!doorOpened && checkDistance() < 30){
    openDoor();
  }
  val = digitalRead(sensorPin);  // read input value
  if (val == HIGH) {            // check if the input is HIGH
    digitalWrite(ledPin, HIGH);  // turn LED ON
    if (pirState == LOW) {
      // we have just turned on
      Serial.println("Motion detected!");
      // We only want to print on the output change, not state
      pirState = HIGH;
    }
  } else {
    digitalWrite(ledPin, LOW); // turn LED OFF
    if (pirState == HIGH){
      // we have just turned off
      Serial.println("still");
      // We only want to print on the output change, not state
      pirState = LOW;
      if (doorOpened) {
        closeDoor();
      }
    }
    if (Serial.available() > 0){ //wait until information is received from the serial port
      item = 0;
      item = Serial.parseInt(); // read the item from serial port
      Serial.print("Serial parsed data received: ");
      Serial.println(item);
      // paper or everything else (trash)
      if (item == 3 || item == 4) {
        Serial.println("item = 3 or 4 // paper or trash");
        digitalWrite(ledPin, HIGH);
        myServo.write(25);
        delay(servoDelay);
        myServo.write(90);
        delay(servoDelay);
        digitalWrite(ledPin, LOW);
        Serial.println("done");
      }
      else {
        Serial.println("Not a valid option");
      }
    }
  }
}