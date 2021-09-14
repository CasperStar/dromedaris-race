from enum import Enum
import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)

import time

class TurnDirection(Enum):
    CLOCKWISE = 1
    ANTI_CLOCKWISE = 2

class MotorController():
    def __init__(self, motor_id, pwm_pin, pwm_freq_khz, direction_pin1, direction_pin2) -> None:
        logging.debug("MotorController: Initializing {:02}".format(motor_id))
        self.motor_id     = motor_id
        self.pwm_pin      = pwm_pin
        self.pwm_freq_khz = pwm_freq_khz
        self.direction_pin1 = direction_pin1
        self.direction_pin2 = direction_pin2

        GPIO.setup(self.pwm_pin, GPIO.OUT)
        self.pwm_output = GPIO.PWM(self.pwm_pin, self.pwm_freq_khz)

        GPIO.setup(self.direction_pin1, GPIO.OUT)
        GPIO.output(self.direction_pin1, GPIO.HIGH)

        GPIO.setup(self.direction_pin2, GPIO.OUT)
        GPIO.output(self.direction_pin2, GPIO.LOW)

    def run(self, turn_direction, speed):
        if (TurnDirection.CLOCKWISE == turn_direction):
            GPIO.output(self.direction_pin1, GPIO.HIGH)
            GPIO.output(self.direction_pin2, GPIO.LOW)
        elif (TurnDirection.ANTI_CLOCKWISE == turn_direction):
            GPIO.output(self.direction_pin1, GPIO.LOW)
            GPIO.output(self.direction_pin2, GPIO.HIGH)

        logging.debug("MotorController: Motor {:02} running {:02}%".format(self.motor_id, speed))
        self.pwm_output.start(speed)

    def stop(self):
        logging.debug("MotorController: Motor {:02} stopping".format(self.motor_id))
        GPIO.output(self.direction_pin1, GPIO.LOW)
        GPIO.output(self.direction_pin2, GPIO.LOW)
        self.pwm_output.stop()


if (__name__ == "__main__"):
    motor = MotorController(1, 12, 100, 16, 18)

    for val in range(10, 100, 10):
        motor.run(TurnDirection.CLOCKWISE, val)
        time.sleep(2)

    motor.stop()

    for val in range(10, 100, 10):
        motor.run(TurnDirection.ANTI_CLOCKWISE, val)
        time.sleep(2)

    motor.stop()

    GPIO.cleanup()
    



# Moving distance = 400 CM 
# Max Score = 25 
