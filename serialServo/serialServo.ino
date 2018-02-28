#include <Servo.h>

int item; // variable to store bin selection
int servoPin1 = 9; //declare pin for the servo
int servoPin2 = 10;
int servoDelay = 800; //delay to allow the servo to reach position;
int val = 0;
int sensorPin = 2;
int ledPin = 13;
int pirState = LOW; 

Servo myServo1; // create a servo object called myServo
Servo myServo2;

void setup() {
  Serial.begin(9600); //start serial port
  myServo1.attach(servoPin1); //declare to which pin is the servo connected
  myServo2.attach(servoPin2);
  pinMode(ledPin, OUTPUT);      // declare LED as output
  pinMode(sensorPin, INPUT);     // declare sensor as input
}

void loop(){
  item = 0;
//  Serial.println("No motion detected.");
  if (myServo1.read() != 90) {
    myServo1.write(90);
    delay(servoDelay);
  }
  if (myServo2.read() != 90) {
    myServo2.write(90);
    delay(servoDelay);
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
    }
    if (Serial.available() > 0){ //wait until information is received from the serial port
      item = 0;
      item = Serial.parseInt(); // read the item from serial port
      Serial.print("Serial parsed data received: ");
      Serial.println(item);
      // metal
      if (item == 1) {
        Serial.println("item = 1 // metal");
        digitalWrite(ledPin, HIGH); 
        myServo1.write(140);
        delay(servoDelay);
        myServo1.write(90);
        delay(servoDelay);
        myServo2.write(130);
        delay(servoDelay);
        digitalWrite(ledPin, LOW);
        Serial.println("done");
      }
      // plastic
      else if (item == 2) {
        Serial.println("item = 2 // plastic");
        digitalWrite(ledPin, HIGH); 
        myServo1.write(150);
        delay(servoDelay);
        myServo2.write(30);
        delay(servoDelay);
        digitalWrite(ledPin, LOW);
        Serial.println("done");
      }
      // paper or everything else (trash)
      else if (item == 3 || item == 4) {
        Serial.println("item = 3 or 4 // paper or trash");
        digitalWrite(ledPin, HIGH);
        myServo1.write(25);
        delay(servoDelay);
        myServo1.write(90);
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

