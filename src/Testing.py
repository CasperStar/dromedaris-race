


from enum import Enum
import abc 

class IOType(Enum):
    IO_EXTENDER_DIGITAL  = 0
    IO_RASPBERRY_DIGITAL = 1
    IO_RASPBERRY_PWM     = 2

class IODefinition:
    def __init__(self, io_type) -> None:
        pass

class IOController():
    def __init__(self) -> None:
        pass

    def set_pin(self, ) -> None:
        pass

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# [Digital Pins]
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

from IOExtender import MCP23017

class IODirection(Enum):
    INPUT  = 0
    OUTPUT = 1

class DigitalPin(abc.ABC):
    @abc.abstractmethod
    def set(self, value):
        pass

    @abc.abstractmethod
    def get(self):
        pass

class RaspberryPin(DigitalPin):
    def __init__(self, pin, direction) -> None:
        self.direction = direction
        self.pin = pin
        if (direction == IODirection.OUTPUT):
            GPIO.setup(pin, GPIO.OUT)
        elif (direction == IODirection.INPUT):
            GPIO.setup(pin, GPIO.IN)

    def set(self, value):
        if (self.direction == IODirection.OUTPUT):
            GPIO.output(self.pin, value)
        else:
            raise Exception("RaspberryPin: pin {:02} setting an input!".format(self.pin))

    def get(self) -> bool:
        return GPIO.input(self.pin)


class ExtenderPin(DigitalPin):
    def __init__(self, device_addr, pin, direction) -> None:
        pass

    def set(self, value):
        pass

    def get(self):
        pass

    



if (__name__ == "__main__"):
    game = RaspberryPin(0x20, 3)
    