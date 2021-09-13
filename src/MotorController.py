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
        logging.debug("MotorController: Initializing {:02s}".format(motor_id))
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

        logging.debug("MotorController: Motor {:02s} running {:02s}%".format(self.motor_id, speed))
        self.pwm_output.start(speed)

    def stop(self):
        GPIO.output(self.direction_pin1, GPIO.LOW)
        GPIO.output(self.direction_pin2, GPIO.LOW)
        self.pwm_output.stop()


if (__name__ == "__main__"):
    MotorController(1, 18, 50, 19, 20)
    MotorController.run(TurnDirection.CLOCKWISE, 50)
    time.sleep(2)
    MotorController.stop()
    time.sleep(2)
    MotorController.run(TurnDirection.ANTI_CLOCKWISE, 75)
    time.sleep(3)
    



# Moving distance = 400 CM 
# Max Score = 25 