/*
http://forums.trossenrobotics.com/tutorials/how-to-diy-128/complete-control-of-an-arduino-via-serial-3300/

1 = Write:
1 = digital:
"pin number"
"1 for LOW"
"2 for HIGH"
2 = analog:
"pin number"
"frequency (0-255)"

2 = Read:
1 = digital:
"pin number"
2 = analog:
"pin number"
3 = Servo:
1 = read:
"pin number"
2 = wright:
"pin number"
" position"
4 = Your Function:
1 = Your Sub Function:
"your variables"
2 = Your Sub Function:
"your variables"

int servoPoses[80] = {}; 
Stores the current position of all the servos

int attachedServos[80] = {};
If a servo is attached the value corresponding to the pin number is set to one; this is important so you don't attach the same servo twice. 

Servo myservo[] = {};
Stores all the servo object in an array so they are easy to access

int servoPin;
Pin of the servo the user wants

int servoPose;
Position the user wants the specified servo to go to 
*/

#include <Servo.h>

unsigned long serialdata;
int inbyte;
int servoPose;
int servoPoses[80] = {};
int attachedServos[80] = {};
int servoPin;
int pinNumber;
int sensorVal;
int analogRate;
int digitalState;
Servo myservo[] = {};

void setup()
{
  Serial.begin(9600);
}

void loop()
{
  getSerial();
  switch(serialdata)
  {
  case 1:
    {
      //analog digital write
      getSerial();
      switch (serialdata)
      {
      case 1:
        {
          //analog write
          getSerial();
          pinNumber = serialdata;
          getSerial();
          analogRate = serialdata;
          pinMode(pinNumber, OUTPUT);
          analogWrite(pinNumber, analogRate);
          pinNumber = 0;
          break;
        }
      case 2:
        {
          //digital write
          getSerial();
          pinNumber = serialdata;
          getSerial();
          digitalState = serialdata;
          pinMode(pinNumber, OUTPUT);
          if (digitalState == 1)
          {
            digitalWrite(pinNumber, LOW);
          }
          if (digitalState == 2)
          {
            digitalWrite(pinNumber, HIGH);
          }
          pinNumber = 0;
          break;
         
        }
     }
     break; 
    }
    case 2:
    {
      getSerial();
      switch (serialdata)
      {
      case 1:
        {
          //analog read
          getSerial();
          pinNumber = serialdata;
          pinMode(pinNumber, INPUT);
          sensorVal = analogRead(pinNumber);
          Serial.println(sensorVal);
          sensorVal = 0;
          pinNumber = 0;
          break;
        } 
      case 2:
        {
          //digital read
          getSerial();
          pinNumber = serialdata;
          pinMode(pinNumber, INPUT);
          sensorVal = digitalRead(pinNumber);
          Serial.println(sensorVal);
          sensorVal = 0;
          pinNumber = 0;
          break;
        }
      }
      break;
    }
    case 3:
    {
      getSerial();
      switch (serialdata)
      {
        case 1:
        {
           //servo read
           getSerial();
           servoPin = serialdata;
           Serial.println(servoPoses[servoPin]);
           break;
        }
        case 2:
        {
           //servo write
           getSerial();
           servoPin = serialdata;
           getSerial();
           servoPose = serialdata;
           if (attachedServos[servoPin] == 1)
           {
             myservo[servoPin].write(servoPose);
           }
           if (attachedServos[servoPin] == 0)
           {
             Servo s1;
             myservo[servoPin] = s1;
             myservo[servoPin].attach(servoPin);
             myservo[servoPin].write(servoPose);
             attachedServos[servoPin] = 1;
           }
           servoPoses[servoPin] = servoPose;
           break;
        }
        case 3:
        {
          //detach
          getSerial();
          servoPin = serialdata;
          if (attachedServos[servoPin] == 1)
          {
            myservo[servoPin].detach();
            attachedServos[servoPin] = 0;  
          }
        }
      }
    break;
    }
  }
}

long getSerial()
{
  serialdata = 0;
  while (inbyte != '/')
  {
    inbyte = Serial.read(); 
    if (inbyte > 0 && inbyte != '/')
    {
     
      serialdata = serialdata * 10 + inbyte - '0';
    }
  }
  inbyte = 0;
  Serial.println(serialdata);
  return serialdata;
}
