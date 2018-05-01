//#include <BasicStepperDriver.h>
#include <Servo.h>

// defines variables
long duration;
int distance;
int pirState = LOW;
int item; // variable to store bin selection
int servoDelay = 800; //delay to allow the servo to reach position;
int val = 0;
float numRevolutions = 5.2;
// Motor steps per revolution. Most steppers are 200 steps or 1.8 degrees/step
#define MOTOR_STEPS 200
#define RPM 240

// defines pins numbers
int clawDirPin = 1;
int clawPin = 2;
int servoPin = 3; //declare pin for the servo
int sensorPin = 2;
int ledPin = 13;
int irPin = 0;
int claw1 = 10;
int claw2 = 11;

// Since microstepping is set externally, make sure this matches the selected mode
// If it doesn't, the motor will move at a different RPM than chosen
// 1=full step, 2=half step etc.
#define MICROSTEPS 1
#define DIR 8
#define STEP 9

// 2-wire basic config, microstepping is hardwired on the driver
//BasicStepperDriver stepper(MOTOR_STEPS, DIR, STEP);
Servo myServo; // create a servo object called myServo

void setup() {
  Serial.begin(9600); //start serial port
  myServo.attach(servoPin); //declare to which pin is the servo connected
  pinMode(ledPin, OUTPUT);      // declare LED as output
  pinMode(sensorPin, INPUT);    // declare PIR sensor as input
  pinMode(irPin, INPUT);        // declare IR distance sensor as input
  pinMode(clawPin, INPUT);
  pinMode(clawDirPin, INPUT);
  pinMode(claw1, OUTPUT);
  pinMode(claw2, OUTPUT);
//  stepper.begin(RPM);
//  stepper.enable();
}

void motorOff() {
  digitalWrite(8,LOW);
  digitalWrite(9,LOW);
}

void clawOff() {
  digitalWrite(10,LOW);
  digitalWrite(11,LOW);
}

void clawGrab() {
  digitalWrite(claw1, HIGH);
  digitalWrite(claw2, LOW);
  delay(400);
  digitalWrite(claw1, LOW);
  digitalWrite(claw2, HIGH);
  clawOff();
}

/*
void descend() {
  stepper.rotate(MOTOR_STEPS * numRevolutions);
  stepper.disable();
}

void ascend() {
  stepper.rotate(-MOTOR_STEPS * numRevolutions);
  stepper.disable();
}
*/

void loop(){
  item = 0;
  Serial.println("ready");
  if (myServo.read() != 90) {
    myServo.write(90);
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
    delay(1000);
    if (pirState == HIGH){
      // we have just turned off
      Serial.println("still");
      // We only want to print on the output change, not state
      pirState = LOW;
    }
    while (!analogRead(clawPin)) {
      clawGrab();
      break;
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
        myServo.write(0);
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
