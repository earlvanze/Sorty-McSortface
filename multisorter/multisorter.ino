#include <Servo.h>

int item; // variable to store bin selection
int servoPin = 9; //declare pin for the servo
int servoDelay = 800; //delay to allow the servo to reach position;

int ledPin = 13;
int pirState = LOW;

// defines pins numbers
const int trigPin = 5;
const int echoPin = 6;

// defines variables
long duration;
int distance;

Servo myServo; // create a servo object called myServo

void setup() {
  Serial.begin(9600); //start serial port
  myServo.attach(servoPin); //declare to which pin is the servo connected
  pinMode(ledPin, OUTPUT);      // declare LED as output
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT); // Sets the echoPin as an Input
}

void loop(){
  item = 0;
  Serial.println("No motion");
  if (myServo.read() != 90) {
    myServo.write(90);
    delay(servoDelay);
  }
  
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

  if (distance < 30) {            // check if the input is HIGH
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
