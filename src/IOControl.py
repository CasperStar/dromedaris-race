
import logging, random, sys
import abc
from enum import Enum

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)

import smbus
GLOBAL_I2C_BUS = smbus.SMBus(1)


class ExtenderContainer:
    def __init__(self, extender_mapping) -> None:
        logging.debug("ExtenderContainer: Initializing")

        self.io_extenders = extender_mapping

    def poll(self):
        result = list()
        for extender in self.io_extenders:
            polling_result = (extender.get_device_addr(), extender.read_output_register_a(), extender.read_output_register_b())
            result.append(polling_result)

        return result

class IODirection(Enum):
    OUTPUT = 0
    INPUT  = 1

class DigitalPin(abc.ABC):
    @abc.abstractmethod
    def set(self, value):
        pass

    @abc.abstractmethod
    def get(self):
        pass

class RaspberryPin(DigitalPin):
    def __init__(self, pin, direction) -> None:
        logging.debug("RaspberryPin: Initializing PIN:{:02} DIR:{}".format(pin, direction.name))
        self.pin = pin
        self.direction = direction
        if (self.direction == IODirection.INPUT):
            GPIO.setup(self.pin, GPIO.IN)
        elif (self.direction == IODirection.OUTPUT):
            GPIO.setup(self.pin, GPIO.OUT)

    def set(self, value):
        if (self.direction == IODirection.OUTPUT):
            GPIO.output(self.pin, value)
        else:
            raise Exception("RaspberryPin: Writing PIN:{:02} while it is an input!".format(self.pin))

    def get(self):
        return GPIO.input(self.pin)

class RaspberryPinPWM():
    def __init__(self, pin, frequency_hz) -> None:
        logging.debug("RaspberryPinPWM: Initializing PIN:{:02} on {:03}Hz".format(pin, frequency_hz))
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm_pin = GPIO.PWM(self.pin, frequency_hz)

    def start(self, duty_cycle):
        self.pwm_pin.start(duty_cycle)

    def stop(self):
        self.pwm_pin.stop()

    def set_frequency(self, frequency_hz):
        self.pwm_pin.ChangeFrequency(frequency_hz)

    def set_duty_cycle(self, duty_cycle):
        self.pwm_pin.ChangeDutyCycle(duty_cycle)

class ExtenderPin(DigitalPin):
    def __init__(self, device_addr, pin, direction) -> None:
        logging.debug("ExtenderPin: Initializing DEV:0x{:02X} PIN:{:02} DIR:{}".format(device_addr, pin, direction.name))
        self.pin = pin
        self.direction = direction
        self.extender = MCP23017(device_addr)
        self.extender.write_direction_pin(pin, direction)

    def set(self, value):
        if (self.direction == IODirection.OUTPUT):
            self.extender.write_output_pin(self.pin, value)
        else:
            raise Exception("ExtenderPin: Writing DEV:0x{:02X} PIN:{:02} while it is an input!".format(self.extender.get_device_addr(), self.pin))

    def get(self):
        return self.extender.read_output_pin(self.pin)

class MCP23017:
    IODIRA = 0x00 # Pin direction register A
    IODIRB = 0x01 # Pin direction register B
    GPPUA  = 0x0C # Pull-up Resistor Register A
    GPPUB  = 0x0D # Pull-up Resistor Register B
    GPIOA  = 0x12 # Pin I/O Register A
    GPIOB  = 0x13 # Pin I/O Register B
    OLATA  = 0x14 # Output Latch Register A
    OLATB  = 0x15 # Output Latch Register B

    def __init__(self, addr, dir_reg_a = None, pullup_reg_a = None, dir_reg_b = None, pullup_reg_b = None) -> None:
        logging.debug("MCP23017: ID:0x{:02X} Initializing".format(addr))
        self.bus = GLOBAL_I2C_BUS
        self.device_addr = addr

        if (dir_reg_a != None):
            self.write_direction_register_a(dir_reg_a)
            self.write_pullup_register_a(pullup_reg_a)
            self.write_direction_register_b(dir_reg_b)
            self.write_pullup_register_b(pullup_reg_b)

    def get_device_addr(self):
        return self.device_addr

    # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # [REGISTER GET + SET: INPUT / OUTPUT]
    # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def read_output_pin(self, pin):
        if (pin < 8):
            return self.read_pin(self.GPIOA)
        else:
            pin = pin % 8
            return self.read_pin(self.GPIOB)

    def read_output_register_a(self):
        return self.read_regsiter(self.GPIOA)

    def read_output_register_b(self):
        return self.read_regsiter(self.GPIOB)

    def write_output_pin(self, pin, value):
        if (pin < 8):
            self.write_pin(self.OLATA, pin, value)
        else:
            pin = pin % 8
            self.write_pin(self.OLATB, pin, value)

    def write_output_register_a(self, byte):
        self.write_regsiter(self.OLATA, byte)

    def write_output_register_b(self, byte):
        self.write_regsiter(self.OLATB, byte)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # [REGISTER GET + SET: PULLUP]
    # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def read_pullup_pin(self, pin):
        if (pin < 8):
            return self.read_pin(self.GPPUA)
        else:
            pin = pin % 8
            return self.read_pin(self.GPPUB)

    def read_pullup_register_a(self):
        return self.read_regsiter(self.GPPUA)

    def read_pullup_register_b(self):
        return self.read_regsiter(self.GPPUB)

    def write_pullup_pin(self, pin, value):
        if (pin < 8):
            self.write_pin(self.GPPUA, pin, value)
        else:
            pin = pin % 8
            self.write_pin(self.GPPUB, pin, value)

    def write_pullup_register_a(self, byte):
        self.write_regsiter(self.GPPUA, byte)

    def write_pullup_register_b(self, byte):
        self.write_regsiter(self.GPPUB, byte)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # [REGISTER GET + SET: DIRECTION]
    # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def read_direction_pin(self, pin):
        if (pin < 8):
            return self.read_pin(self.IODIRA)
        else:
            pin = pin % 8
            return self.read_pin(self.IODIRB)

    def read_direction_register_a(self):
        return self.read_regsiter(self.IODIRA)

    def read_direction_register_b(self):
        return self.read_regsiter(self.IODIRB)

    def write_direction_pin(self, pin, value):
        if (pin < 8):
            self.write_pin(self.IODIRA, pin, value)
        else:
            pin = pin % 8
            self.write_pin(self.IODIRB, pin, value)

    def write_direction_register_a(self, byte):
        self.write_regsiter(self.IODIRA, byte)

    def write_direction_register_b(self, byte):
        self.write_regsiter(self.IODIRB, byte)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # [GENERIC REGISTER GET + SET]
    # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def read_pin(self, register, pin):
        logging.debug("MCP23017: ID:0x{:02X} Reading pin {:02} from 0x{:02X}".format(self.device_addr, pin, register))
        current_value = self.read_regsiter(register)
        return current_value & (1 << pin)

    def write_pin(self, register, pin, value):
        logging.debug("MCP23017: ID:0x{:02X} Setting pin {:02} in {:02} to {}".format(self.device_addr, pin, register, value))
        current_value = self.read_regsiter(register)
        if (value == True):
            current_value |= (1 << pin) # Set Pin
        elif (value == False):
            current_value &= ~(1 << pin) # Clear Pin

        self.write_regsiter(register, current_value)

    def read_regsiter(self, register):
        byte = self.bus.read_byte_data(self.device_addr, register)
        logging.debug("MCP23017: ID:0x{:02X} Reading register 0x{:02X} ({:08b})".format(self.device_addr, register, byte))
        return byte

    def write_regsiter(self, register, byte):
        logging.debug("MCP23017: ID:0x{:02X} Writing register 0x{:02X} ({:08b})".format(self.device_addr, register, byte))
        self.bus.write_byte_data(self.device_addr, register, byte)
