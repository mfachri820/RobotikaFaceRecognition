// --- FUNDUMOTO L298P SHIELD PINOUT ---
const int pinDIR_A = 12; // Motor A Direction (Left)
const int pinPWM_A = 10; // Motor A Speed

const int pinDIR_B = 13; // Motor B Direction (Right)
const int pinPWM_B = 11; // Motor B Speed

// --- MOTOR CALIBRATION ---
// IF ROBOT CURVES LEFT: Reduce 'speedRight'
// IF ROBOT CURVES RIGHT: Reduce 'speedLeft'

int speedLeft = 240; 
int speedRight = 240;

int turnSpeed = 255;   // Keep turning speed high for friction

void setup() {
  Serial.begin(9600);
  pinMode(pinDIR_A, OUTPUT);
  pinMode(pinPWM_A, OUTPUT);
  pinMode(pinDIR_B, OUTPUT);
  pinMode(pinPWM_B, OUTPUT);
  stopCar();
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    switch (command) {
      case 'F': moveForward(); break;
      case 'L': turnLeft(); break;
      case 'R': turnRight(); break;
      case 'S': stopCar(); break;
    }
  }
}

// --- MOVEMENT FUNCTIONS ---

void moveForward() {
  // Motor A (Left) - Low = Forward
  digitalWrite(pinDIR_A, LOW); 
  analogWrite(pinPWM_A, speedLeft); // Uses Calibrated Speed

  // Motor B (Right) - Low = Forward
  digitalWrite(pinDIR_B, LOW); 
  analogWrite(pinPWM_B, speedRight); // Uses Calibrated Speed
}

void turnLeft() {
  // Tank Turn Left
  digitalWrite(pinDIR_A, HIGH); 
  analogWrite(pinPWM_A, turnSpeed);
  digitalWrite(pinDIR_B, LOW); 
  analogWrite(pinPWM_B, turnSpeed);
}

void turnRight() {
  // Tank Turn Right
  digitalWrite(pinDIR_A, LOW); 
  analogWrite(pinPWM_A, turnSpeed);
  digitalWrite(pinDIR_B, HIGH); 
  analogWrite(pinPWM_B, turnSpeed);
}

void stopCar() {
  analogWrite(pinPWM_A, 0);
  analogWrite(pinPWM_B, 0);
}