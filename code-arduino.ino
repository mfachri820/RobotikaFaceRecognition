// // === PIN MAPPING (Confirmed) ===
// const int pinDIR_L = 13; // Left Motor DIR  (Port B)
// const int pinPWM_L = 11; // Left Motor PWM  (Port B)

// const int pinDIR_R = 12; // Right Motor DIR (Port A)
// const int pinPWM_R = 10; // Right Motor PWM (Port A)

// // === SPEED CONTROL ===
// // Kamu tinggal tuning leftTrim & rightTrim supaya lurus
// int maxSpeed = 120;
// int leftTrim  = +48;   // motor kiri LEBIH PELAN → kasih boost (coba 20–60)
// int rightTrim = 0;     // motor kanan lebih kuat → tidak usah di-boost

// // === MOTOR POLARITY ===
// // (Sudah sesuai dengan hasil test kamu)
// #define LEFT_FORWARD    HIGH
// #define LEFT_BACKWARD   LOW

// #define RIGHT_FORWARD   LOW
// #define RIGHT_BACKWARD  HIGH

// void setup() {
//   Serial.begin(9600);

//   pinMode(pinDIR_L, OUTPUT);
//   pinMode(pinPWM_L, OUTPUT);
//   pinMode(pinDIR_R, OUTPUT);
//   pinMode(pinPWM_R, OUTPUT);

//   stopCar();
//   Serial.println("Car Ready. Commands: F, L, R, S");
// }

// void loop() {
//   if (Serial.available()) {
//     char cmd = Serial.read();
//     switch (cmd) {
//       case 'F': moveForward(); break;
//       case 'L': turnLeft();    break;
//       case 'R': turnRight();   break;
//       case 'S': stopCar();     break;
//     }
//   }
// }

// // =========================
// //     MOVEMENT FUNCTIONS
// // =========================

// void moveForward() {
//   // Forward polarity
//   digitalWrite(pinDIR_L, LEFT_FORWARD);
//   digitalWrite(pinDIR_R, RIGHT_FORWARD);

//   // Apply trim (LEFT gets boost)
//   int pwmL = constrain(maxSpeed + leftTrim, 0, 255);
//   int pwmR = constrain(maxSpeed + rightTrim, 0, 255);

//   analogWrite(pinPWM_L, pwmL);
//   analogWrite(pinPWM_R, pwmR);

//   Serial.print("FORWARD L=");
//   Serial.print(pwmL);
//   Serial.print("  R=");
//   Serial.println(pwmR);
// }

// void moveBackward() {
//   digitalWrite(pinDIR_L, LEFT_BACKWARD);
//   digitalWrite(pinDIR_R, RIGHT_BACKWARD);

//   analogWrite(pinPWM_L, maxSpeed);
//   analogWrite(pinPWM_R, maxSpeed);

//   Serial.println("BACKWARD");
// }

// void turnLeft() {
//   // Left backward, Right forward
//   digitalWrite(pinDIR_L, LEFT_BACKWARD);
//   digitalWrite(pinDIR_R, RIGHT_FORWARD);

//   analogWrite(pinPWM_L, maxSpeed);
//   analogWrite(pinPWM_R, maxSpeed);

//   Serial.println("LEFT");
// }

// void turnRight() {
//   // Left forward, Right backward
//   digitalWrite(pinDIR_L, LEFT_FORWARD);
//   digitalWrite(pinDIR_R, RIGHT_BACKWARD);

//   analogWrite(pinPWM_L, maxSpeed);
//   analogWrite(pinPWM_R, maxSpeed);

//   Serial.println("RIGHT");
// }

// void stopCar() {
//   analogWrite(pinPWM_L, 0);
//   analogWrite(pinPWM_R, 0);
//   Serial.println("STOP");
// }

// =========================
//      PIN MAPPING
// =========================
const int pinDIR_L = 13;
const int pinPWM_L = 11;

const int pinDIR_R = 12;
const int pinPWM_R = 10;

// =========================
//      SPEED SETTINGS
// =========================

// BASE SPEED
int maxSpeed = 140;

// AUTO TRIM untuk gerakan LURUS
// (silakan tuning 0–70)
int trimLeft  = 50;   
int trimRight = 0;    

// TURN STRENGTH — belokan harus lebih kuat dari forward
int turnBoostLeft  = 30;   // ekstra power saat belok kiri
int turnBoostRight = 40;   // ekstra power saat belok kanan

// soft start minimal PWM (motor murah kadang harus 60–80)
int minPWM = 70;

// =========================
//   MOTOR POLARITY
// =========================
#define LEFT_FORWARD    HIGH
#define LEFT_BACKWARD   LOW

#define RIGHT_FORWARD   LOW
#define RIGHT_BACKWARD  HIGH

void setup() {
  Serial.begin(9600);

  pinMode(pinDIR_L, OUTPUT);
  pinMode(pinPWM_L, OUTPUT);
  pinMode(pinDIR_R, OUTPUT);
  pinMode(pinPWM_R, OUTPUT);

  stopCar();
  Serial.println("Car Ready. Commands: F, L, R, S");
}

// =========================
//   MOVEMENT FUNCTIONS
// =========================

int applySoftStart(int pwm) {
  if (pwm < minPWM && pwm > 0)
      return minPWM;
  return pwm;
}

void moveForward() {
  digitalWrite(pinDIR_L, LEFT_FORWARD);
  digitalWrite(pinDIR_R, RIGHT_FORWARD);

  int pwmL = maxSpeed + trimLeft;
  int pwmR = maxSpeed + trimRight;

  pwmL = applySoftStart(constrain(pwmL, 0, 255));
  pwmR = applySoftStart(constrain(pwmR, 0, 255));

  analogWrite(pinPWM_L, pwmL);
  analogWrite(pinPWM_R, pwmR);

  Serial.print("FORWARD L=");
  Serial.print(pwmL);
  Serial.print("  R=");
  Serial.println(pwmR);
}

void turnLeft() {
  // left backwards, right forward
  digitalWrite(pinDIR_L, LEFT_BACKWARD);
  digitalWrite(pinDIR_R, RIGHT_FORWARD);

  // boost belok kiri
  int pwmL = maxSpeed + turnBoostLeft;
  int pwmR = maxSpeed + turnBoostLeft;

  pwmL = applySoftStart(constrain(pwmL, 0, 255));
  pwmR = applySoftStart(constrain(pwmR, 0, 255));

  analogWrite(pinPWM_L, pwmL);
  analogWrite(pinPWM_R, pwmR);

  Serial.print("LEFT L=");
  Serial.print(pwmL);
  Serial.print("  R=");
  Serial.println(pwmR);
}

void turnRight() {
  // left forward, right backward
  digitalWrite(pinDIR_L, LEFT_FORWARD);
  digitalWrite(pinDIR_R, RIGHT_BACKWARD);

  // boost belok kanan (lebih besar karena kamu bilang kanan susah)
  int pwmL = maxSpeed + turnBoostRight;
  int pwmR = maxSpeed + turnBoostRight;

  pwmL = applySoftStart(constrain(pwmL, 0, 255));
  pwmR = applySoftStart(constrain(pwmR, 0, 255));

  analogWrite(pinPWM_L, pwmL);
  analogWrite(pinPWM_R, pwmR);

  Serial.print("RIGHT L=");
  Serial.print(pwmL);
  Serial.print("  R=");
  Serial.println(pwmR);
}

void stopCar() {
  analogWrite(pinPWM_L, 0);
  analogWrite(pinPWM_R, 0);

  Serial.println("STOP");
}

void loop() {
  if (Serial.available()) {
    char cmd = Serial.read();
    switch (cmd) {
      case 'F': moveForward(); break;
      case 'L': turnLeft();    break;
      case 'R': turnRight();   break;
      case 'S': stopCar();     break;
    }
  }
}
