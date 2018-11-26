#include <Servo.h>

// Login pins
const int greenLED = 2;
const int redLED = 4;
const int buzzerPin = 8;
// PhotoRes pins
const int photoResPin = A1;
const int photoResLED = 7;
// Servo pins
const int servoPotPin = A0;
// Ultrasonic sensor pins
const int trigPin = 5;
const int echoPin = 6;
// State pins
const int waitToLogInPin = 11;
const int loggedInPin = 12;
const int wrongPasswordPin = 13;

// States
enum state {
  waitToLogIn,
  loggedIn,
  wrongPassword
};
state curr_state;

// Variables
int photoResVoltage = 0;
int wrongPassCnt = 0;
long uvDuration;
int uvDistance;
int buzzerTime = 0;

// Servo
Servo servoKnob;
int servoVoltage;

void setup() {
  Serial.begin(9600);

  // Log in pin setup.
  pinMode(2, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(9, OUTPUT);

  // PhotoRes pin setup.
  pinMode(A1, INPUT);
  pinMode(7, OUTPUT);

  // Servo setup.
  servoKnob.attach(9);

  // UV sensor setup.
  pinMode(6, INPUT);
  pinMode(5, OUTPUT);

  // State pin setup.
  pinMode(11, OUTPUT);
  pinMode(12, OUTPUT);
  pinMode(13, OUTPUT);

  // Start state
  curr_state = waitToLogIn;
}

void manageStateLEDs() {
  digitalWrite(waitToLogInPin, LOW);
  digitalWrite(loggedInPin, HIGH);
  digitalWrite(wrongPasswordPin, LOW);
}

void managePhotoResLED() {
  photoResVoltage = analogRead(photoResPin);
  photoResVoltage = 255 - map(photoResVoltage, 0, 1023, 0, 255);
  analogWrite(photoResLED, photoResVoltage);
}

void manageServo() {
  servoVoltage = analogRead(servoPotPin);
  servoVoltage = map(servoVoltage, 0, 1023, 0, 180);
  servoKnob.write(servoVoltage);
  delay(15);
}

void manageUVSensor() {
  // Clear trig pin.
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  
  // Set the trig pin on HIGH
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  // Read the echoPin and calculate the distance (cm).
  uvDuration = pulseIn(echoPin, HIGH);
  uvDistance = uvDuration * 0.034 / 2;

  // Turn the buzzer if distance is less than 10cm.
  if (uvDistance < 10) {
    tone(buzzerPin, 1000);
  } else {
    noTone(buzzerPin);
  }
}

void loop() {
  switch (curr_state) {

    case waitToLogIn: {
      // State LED.
      digitalWrite(waitToLogInPin, HIGH);
      digitalWrite(loggedInPin, LOW);
      digitalWrite(wrongPasswordPin, LOW);
      
      // Reset.
      digitalWrite(redLED, LOW);
      digitalWrite(greenLED, LOW);

      // Check if there is information about logging.
      if (Serial.available() > 0) {
        char enter_house = Serial.read();
        if (enter_house == '1') {
          curr_state = loggedIn;
        } else {
          curr_state = wrongPassword;
          wrongPassCnt = 0;
        }
      }
    } break;

    case loggedIn: {
      // Turn on Green LED.
      digitalWrite(greenLED, HIGH);

      // Manage smart house.
      manageStateLEDs();
      managePhotoResLED();
      manageServo();
      manageUVSensor();
    } break;

    case wrongPassword: {
      // State LED.
      digitalWrite(waitToLogInPin, LOW);
      digitalWrite(loggedInPin, LOW);
      digitalWrite(wrongPasswordPin, HIGH);
      
      // Turn on buzzer and blink LED.
      if (buzzerTime <= 500) {
        tone(buzzerPin, 1000);
        digitalWrite(redLED, HIGH);
      } else {
        noTone(buzzerPin);
        digitalWrite(redLED, LOW);
      }
      delay(50);
      buzzerTime = (buzzerTime + 50) % 1000;
          
      // End with this state after 5 loops.
      wrongPassCnt++;
      if (wrongPassCnt == 100) {
        curr_state = waitToLogIn;
      }
    } break;
  }

}
