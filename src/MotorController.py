import logging, sys

#TODO: REMOVE DEBUG BELOW
from IOExtender import RaspberryPin, RaspberryPinPWM, IODirection
import time

from enum import Enum

class TurnDirection(Enum):
    CLOCKWISE = 1
    ANTI_CLOCKWISE = 2

class MotorController():
    def __init__(self, motor_id, pwm_pin, dir_pin_1, dir_pin_2) -> None:
        logging.debug("MotorController: Initializing {:02}".format(motor_id))
        self.motor_id = motor_id
        self.pwm_pin  = pwm_pin
        self.direction_pin_1 = dir_pin_1
        self.direction_pin_2 = dir_pin_2

    def start(self, turn_direction, speed):
        logging.debug("MotorController: Motor {:02} running {} at {:02}%".format(self.motor_id, turn_direction.name, speed))
        self.set_direction(turn_direction)
        self.pwm_pin.start(speed)

    def stop(self):
        logging.debug("MotorController: Motor {:02} stopping".format(self.motor_id))
        self.direction_pin_1.set(False)
        self.direction_pin_2.set(False)
        self.pwm_pin.stop()

    def set_speed(self, speed):
        logging.debug("MotorController: Motor {:02} set speed {:02}%".format(self.motor_id, speed))
        self.pwm_pin.set_duty_cycle(speed)

    def set_direction(self, turn_direction):
        logging.debug("MotorController: Motor {:02} set direction {}".format(self.motor_id, turn_direction.name))
        if (TurnDirection.CLOCKWISE == turn_direction):
            self.direction_pin_1.set(True)
            self.direction_pin_2.set(False)
        elif (TurnDirection.ANTI_CLOCKWISE == turn_direction):
            self.direction_pin_1.set(False)
            self.direction_pin_2.set(True)



if (__name__ == "__main__"):
    motor = MotorController(1, RaspberryPinPWM(18, 100), RaspberryPin(19,  IODirection.OUTPUT), RaspberryPin(20, IODirection.OUTPUT))

    for val in range(10, 100, 10):
        motor.start(TurnDirection.CLOCKWISE, val)
        time.sleep(2)

    motor.stop()

    for val in range(10, 100, 10):
        motor.start(TurnDirection.ANTI_CLOCKWISE, val)
        time.sleep(2)

    motor.stop()


