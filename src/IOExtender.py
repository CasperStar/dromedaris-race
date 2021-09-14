
import logging, random
from DromedarisRace import GLOBAL_I2C_BUS
from Testing import IODirection
import smbus
import abc
from enum import Enum

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

class ExtenderPin(DigitalPin):
    def __init__(self, device_addr, pin, direction) -> None:
        self.pin = pin
        self.direction = direction
        self.extender = MCP23017(GLOBAL_I2C_BUS, device_addr)
        self.extender.set_pin_direction(pin, direction)

    def set(self, value):
        if (self.direction == IODirection.OUTPUT):
            self.extender.write_output_pin(self.pin, value)
        else:
            raise Exception("Writing to a input!")

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

    def __init__(self, bus, addr, dir_reg_a = None, pullup_reg_a = None, dir_reg_b = None, pullup_reg_b = None) -> None:
        logging.debug("MCP23017: ID:%s Initializing" %(addr))
        self.bus = bus
        self.device_addr = addr

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
        if (pin < 7):
            return self.read_pin(self.GPIOA)
        else:
            pin = pin % 8
            return self.read_pin(self.GPIOB)

    def read_output_register_a(self):
        return self.read_regsiter(self.GPIOA)

    def read_output_register_b(self):
        return self.read_regsiter(self.GPIOB)

    def write_output_pin(self, pin, value):
        if (pin < 7):
            self.write_pin(self.OLATA, value)
        else:
            pin = pin % 8
            self.write_pin(self.OLATB, value)

    def write_output_register_a(self, byte):
        self.write_regsiter(self.OLATA, byte)

    def write_output_register_b(self, byte):
        self.write_regsiter(self.OLATB, byte)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    # [REGISTER GET + SET: PULLUP]
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

    def read_pullup_pin(self, pin):
        if (pin < 7):
            return self.read_pin(self.GPPUA)
        else:
            pin = pin % 8
            return self.read_pin(self.GPPUB)

    def read_pullup_register_a(self):
        return self.read_regsiter(self.GPPUA)

    def read_pullup_register_b(self):
        return self.read_regsiter(self.GPPUB)

    def write_pullup_pin(self, pin, value):
        if (pin < 7):
            self.write_pin(self.GPPUA, value)
        else:
            pin = pin % 8
            self.write_pin(self.GPPUB, value)

    def write_pullup_register_a(self, byte):
        self.write_regsiter(self.GPPUA, byte)

    def write_pullup_register_b(self, byte):
        self.write_regsiter(self.GPPUB, byte)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    # [REGISTER GET + SET: DIRECTION]
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

    def read_direction_pin(self, pin):
        if (pin < 7):
            return self.read_pin(self.IODIRA)
        else:
            pin = pin % 8
            return self.read_pin(self.IODIRB)

    def read_direction_register_a(self):
        return self.read_regsiter(self.IODIRA)

    def read_direction_register_b(self):
        return self.read_regsiter(self.IODIRB)

    def write_direction_pin(self, pin, value):
        if (pin < 7):
            self.write_pin(self.IODIRA, value)
        else:
            pin = pin % 8
            self.write_pin(self.IODIRB, value)

    def write_direction_register_a(self, byte):
        self.write_regsiter(self.IODIRA, byte)

    def write_direction_register_b(self, byte):
        self.write_regsiter(self.IODIRB, byte)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    # [GENERIC REGISTER GET + SET]
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

    def read_pin(self, register, pin):
        logging.debug("MCP23017: ID:{} Reading pin {:02} from {:02X}".format(self.device_addr, pin, register))
        current_value = self.read_regsiter(register)
        return current_value & (1 << pin)

    def write_pin(self, register, pin, value):
        logging.debug("MCP23017: ID:{} Setting pin {:02} in {:02} to {}".format(self.device_addr, pin, register, value))
        current_value = self.read_regsiter(register)
        if (value == True):
            current_value |= (1 << pin) # Set Pin
        elif (value == False):
            current_value &= ~(1 << pin) # Clear Pin

        self.write_regsiter(register, current_value)

    def read_regsiter(self, register):
        byte = self.bus.read_byte_data(self.device_addr, register)
        logging.debug("MCP23017: ID:{} Reading register {:02X} ({:08b})".format(self.device_addr, register, byte))
        return byte

    def write_regsiter(self, register, byte):
        logging.debug("MCP23017: ID:{} Writing register {:02X} ({:08b})".format(self.device_addr, register, byte))
        self.bus.write_byte_data(self.device_addr, register, byte)
