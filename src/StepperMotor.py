import time
import logging, sys
import smbus
from IOExtender import MCP23017


REVOLUTION_IN_DEGREES = 360
NUMBER_OF_HALF_STEPS_PER_REV = 4096
HALF_STEP_SEQUENCE = ((1,0,0,0),
                      (1,1,0,0),
                      (0,1,0,0),
                      (0,1,1,0),
                      (0,0,1,0),
                      (0,0,1,1),
                      (0,0,0,1),
                      (1,0,0,1))

NUMBER_OF_FULL_STEPS_PER_REV = 2048
FULL_STEP_SEQUENCE = ((1,0,0,0),
                      (0,1,0,0),
                      (0,0,1,0),
                      (0,0,0,1))

from enum import Enum

class TurnDirection(Enum):
    CLOCKWISE = 1
    ANTI_CLOCKWISE = 2

class StepperMotor:
    def __init__(self, delay, pin1, pin2, pin3, pin4) -> None:
        logging.debug("StepperMotor: Initializing")
        self.step_delay = delay
        self.current_step = 0
        self.step_sequence = FULL_STEP_SEQUENCE
        self.NUMBER_OF_STEPS_PER_REV = NUMBER_OF_FULL_STEPS_PER_REV
        self.total_steps = 0
        self.pins = [pin1, pin2, pin3, pin4]

        self.I2CBus = smbus.SMBus(1)
        self.mcp = MCP23017(self.I2CBus, 0x20, 0x00, 0x00)

    def set_step_delay(self, delay) -> None:
        self.step_delay = delay

    def __turn_step(self, direction):
        # Setting ULN2003 pin to next sequence step
        logging.debug("StepperMotor: Set sequence: {} {} ({})".format(self.current_step, self.step_sequence[self.current_step], self.total_steps))

        register_byte = 0
        for index, seq_value in enumerate(self.step_sequence[self.current_step]):
            if seq_value == 1:
                register_byte |=  (1 << self.pins[index]) # Set bit
            elif seq_value == 0:
                register_byte &= ~(1 << self.pins[index]) # Clear bit

        # Write sequence to IO
        logging.debug("Written Byte: {0:08b}".format(register_byte))
        self.mcp.write_register_a(register_byte)


        if (TurnDirection.CLOCKWISE == direction):
            self.current_step += 1
            self.total_steps += 1
        elif (TurnDirection.ANTI_CLOCKWISE == direction):
            self.current_step -= 1
            self.total_steps -= 1

        if (self.current_step >= len(self.step_sequence)):
            self.current_step = 0
        elif (self.current_step < 0):
            self.current_step = len(self.step_sequence) - 1

        time.sleep(self.step_delay)


    def turn_steps(self, direction, steps) -> None:
        logging.debug("StepperMotor: Turn steps: {} {}".format(steps, direction.name))
        for i in range(self.current_step, self.current_step + steps):
            self.__turn_step(direction)

    def turn_degrees(self, direction, degrees) -> None:
        needed_steps = degrees * (self.NUMBER_OF_STEPS_PER_REV / REVOLUTION_IN_DEGREES)
        logging.debug("StepperMotor: Turn degrees: {} {} (Steps: {:4.2f})".format(degrees, direction.name, needed_steps))
        self.turn_steps(direction, int(needed_steps))








if (__name__ == "__main__"):
    motor = StepperMotor(0.01, 0x00, 0x01, 0x02, 0x03)
    motor.turn_degrees(TurnDirection.ANTI_CLOCKWISE, 360 * 30)
