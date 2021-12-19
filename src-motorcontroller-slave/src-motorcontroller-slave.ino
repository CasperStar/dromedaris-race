#include <Wire.h>

#define NUMBER_OF_MOTORS 6
#define I2C_SLAVE_ADDRESS 4

typedef enum MotorAction {
  STOP_PASSIVE,
  TURN_CLOCKWISE,
  TURN_ANTI_CLOCKWISE,
  STOP_ACTIVE,
} MotorAction;

typedef struct MotorPinMapping {
  int pwm_pin;
  int input_1;
  int input_2;
} MotorPinMapping;

MotorPinMapping motor_pin_mapping[NUMBER_OF_MOTORS] = { 
  { 3,  0,  1},  // MOTOR 0 (D2, D1)
  { 5,  2,  4},  // MOTOR 1 (D2, D4)
  { 6,  7,  8},  // MOTOR 2 (D7, D8)
  { 9, 12, 13},  // MOTOR 3 (D12, D13)
  {10, 14, 15},  // MOTOR 4 (A0, A2)
  {11, 16, 17}}; // MOTOR 5 (A2, A3)
  

void setup() 
{
  //Serial.begin(9600); // Debug print
  pinMode(0, OUTPUT);
  pinMode(1, OUTPUT);
  Wire.begin(I2C_SLAVE_ADDRESS);
  Wire.onReceive(process_request);
}

void loop() 
{
  delay(5000);
}

void set_motor_speed(int motor_id, int percentage)
{
  int pwm = motor_pin_mapping[motor_id].pwm_pin;

  // Convert percentage to analog_value
  int analog_value = map(percentage, 0, 100, 0, 255);
  analogWrite(pwm, analog_value);

  // Debug Print
  Serial.print("Motor: ");
  Serial.print(motor_id);
  Serial.print(" Set Motor Speed: ");
  Serial.print(percentage);
  Serial.print("% -> ");
  Serial.print(analog_value);
  Serial.print(" PWM:");
  Serial.println(pwm);
}

void set_motor_action(int motor_id, MotorAction action)
{
  int input_pin1 = motor_pin_mapping[motor_id].input_1;
  int input_pin2 = motor_pin_mapping[motor_id].input_2;

  // Debug print
  Serial.print("Motor: ");
  Serial.print(motor_id);
  Serial.print(" (P1:");
  Serial.print(input_pin1);
  Serial.print("P2:");
  Serial.print(input_pin2);
  Serial.print(") ");
  
  switch(action)
  {
    case STOP_PASSIVE:
      digitalWrite(input_pin1, LOW);
      digitalWrite(input_pin2, LOW);
      Serial.println(" STOP PASSIVE"); // Debug print
      break;
    case TURN_CLOCKWISE:
      digitalWrite(input_pin1, HIGH);
      digitalWrite(input_pin2, LOW);
      Serial.println(" TURN CLOCKWISE"); // Debug print
      break;
    case TURN_ANTI_CLOCKWISE:
      digitalWrite(input_pin1, LOW);
      digitalWrite(input_pin2, HIGH);
      Serial.println(" TURN ANTI CLOCKWISE"); // Debug print
      break;
    case STOP_ACTIVE:
      digitalWrite(input_pin1, HIGH);
      digitalWrite(input_pin2, HIGH);
      Serial.println(" STOP ACTIVE"); // Debug print
      break; 
  }
}

void process_request(int bytes_received)
{
  //Serial.print("Bytes Received: ");
  //Serial.println(bytes_received);

  // Parse Parameters
  if (bytes_received != 4) {
    return clean_up();
  }
  
  int motor_id = Wire.read();
  if (motor_id > NUMBER_OF_MOTORS - 1) {
    return clean_up();
  }
  
  int number_of_bytes_left = Wire.read();
  if (number_of_bytes_left != 2) {
    return clean_up();
  }

  // Process Motor Action
  int motor_action = Wire.read();
  int action_value = Wire.read();

  switch(motor_action)
  {
    case 0x10:
      set_motor_speed(motor_id, action_value);
      break;
    case 0x20:
      set_motor_action(motor_id, (MotorAction) action_value);
      break;
  }

  clean_up();
}

void clean_up() {
  while(Wire.available()) 
    int c = Wire.read();
}
