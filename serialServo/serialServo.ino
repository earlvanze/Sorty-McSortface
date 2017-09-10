#include <Servo.h>

int pos; // variable to store bin selection
int servoPin1 = 9; //declare pin for the servo
int servoPin2 = 10;
int servoDelay = 1500; //delay to allow the servo to reach position;
int val = 0;
int sensorPin = 2;
int ledPin = 12;
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
  pos = NULL;
//  Serial.println("start loop");
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
      Serial.println("Motion ended!");
      // We only want to print on the output change, not state
      pirState = LOW;
    }
    if (Serial.available() > 0){ //wait until information is received from the serial port
      pos = Serial.parseInt(); //read the position from the servo
      Serial.print("Serial parsed data received: ");
      Serial.println(pos);
      if (pos == 3) {
        Serial.println("pos = 3");
        digitalWrite(ledPin, HIGH); 
        myServo1.write(165); //write the position into the servo
        delay(servoDelay);
        myServo1.write(90);
        delay(servoDelay);
        myServo2.write(165);
        delay(servoDelay);
        digitalWrite(ledPin, LOW);
      }
      else if (pos == 2 || pos == 4 ) {
        Serial.println("pos = 2 or 4");
        digitalWrite(ledPin, HIGH); 
        myServo1.write(150); //write the position into the servo
        delay(servoDelay*2);
        myServo2.write(30);
        digitalWrite(ledPin, LOW);
      }
      else if (pos == 1) {
        Serial.println("pos = 1");
        digitalWrite(ledPin, HIGH); 
        myServo1.write(25); //write the position into the servo
        delay(servoDelay);
        myServo1.write(90);
        delay(servoDelay);
        digitalWrite(ledPin, LOW);
      }
      else {
        Serial.println("Not a valid option");
      }
    }
  }
}

